"""Autenticação: registro de tenant, login, refresh, usuários e reset de senha."""
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import settings
from ..deps import audit, get_current_user, require_roles
from ..database import get_db
from ..security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def _get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.email == email.lower()))


@router.post("/register", response_model=schemas.UserOut, status_code=201)
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    """Cria um novo escritório (tenant) e seu usuário administrador."""
    if _get_user_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado")
    tenant = models.Tenant(nome=payload.tenant_nome)
    db.add(tenant)
    db.flush()
    user = models.User(
        tenant_id=tenant.id,
        nome=payload.nome,
        email=payload.email.lower(),
        senha_hash=hash_password(payload.senha),
        role="admin",
    )
    db.add(user)
    db.flush()
    audit(db, user, "register", "tenant", tenant.id)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.TokenOut)
def login(
    form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = _get_user_by_email(db, form.username)
    if user is None or not verify_password(form.password, user.senha_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "E-mail ou senha inválidos")
    if not user.ativo:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Usuário inativo")
    return schemas.TokenOut(
        access_token=create_access_token(
            sub=user.id, tenant_id=user.tenant_id, role=user.role
        ),
        refresh_token=create_refresh_token(
            sub=user.id, tenant_id=user.tenant_id, role=user.role
        ),
    )


@router.post("/refresh", response_model=schemas.TokenOut)
def refresh(payload: schemas.RefreshIn, db: Session = Depends(get_db)):
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise ValueError
        user_id = int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Refresh token inválido")
    user = db.get(models.User, user_id)
    if user is None or not user.ativo:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Usuário indisponível")
    return schemas.TokenOut(
        access_token=create_access_token(
            sub=user.id, tenant_id=user.tenant_id, role=user.role
        ),
        refresh_token=create_refresh_token(
            sub=user.id, tenant_id=user.tenant_id, role=user.role
        ),
    )


@router.get("/me", response_model=schemas.UserOut)
def me(user: models.User = Depends(get_current_user)):
    return user


@router.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(
    payload: schemas.UserCreateIn,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_roles("admin")),
):
    """Admin cria usuários (advogado/cliente/financeiro) dentro do seu tenant."""
    if _get_user_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado")
    user = models.User(
        tenant_id=admin.tenant_id,
        nome=payload.nome,
        email=payload.email.lower(),
        senha_hash=hash_password(payload.senha),
        role=payload.role,
    )
    db.add(user)
    db.flush()
    audit(db, admin, "create", "user", user.id)
    db.commit()
    db.refresh(user)
    return user


@router.post("/password-reset/request")
def password_reset_request(
    payload: schemas.PasswordResetRequestIn, db: Session = Depends(get_db)
):
    """Gera token de uso único. Em produção, enviar por e-mail (nunca na resposta)."""
    user = _get_user_by_email(db, payload.email)
    generic = {"detail": "Se o e-mail existir, um token de redefinição foi gerado"}
    if user is None:
        return generic
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_expira = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MIN
    )
    db.commit()
    # DEV: devolvemos o token para facilitar testes locais.
    return {**generic, "reset_token": token}


@router.post("/password-reset/confirm")
def password_reset_confirm(
    payload: schemas.PasswordResetConfirmIn, db: Session = Depends(get_db)
):
    user = db.scalar(
        select(models.User).where(models.User.reset_token == payload.token)
    )
    expira = user.reset_expira if user else None
    if expira is not None and expira.tzinfo is None:
        expira = expira.replace(tzinfo=timezone.utc)
    if user is None or expira is None or expira < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido ou expirado")
    user.senha_hash = hash_password(payload.nova_senha)
    user.reset_token = None
    user.reset_expira = None
    audit(db, user, "password_reset", "user", user.id)
    db.commit()
    return {"detail": "Senha redefinida com sucesso"}
