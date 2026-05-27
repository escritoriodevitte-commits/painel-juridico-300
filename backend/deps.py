"""Dependências de autenticação e RBAC."""
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

_CRED_EXC = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Credenciais inválidas",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise _CRED_EXC
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise _CRED_EXC

    user = db.get(models.User, user_id)
    if user is None or not user.ativo:
        raise _CRED_EXC
    return user


def require_roles(*roles: str):
    """Garante que o usuário atual tenha um dos papéis informados."""

    def checker(user: models.User = Depends(get_current_user)) -> models.User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão negada para o seu perfil",
            )
        return user

    return checker


def audit(
    db: Session,
    user: models.User,
    acao: str,
    entidade: str,
    entidade_id: int | None = None,
) -> None:
    db.add(
        models.AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            acao=acao,
            entidade=entidade,
            entidade_id=entidade_id,
        )
    )
