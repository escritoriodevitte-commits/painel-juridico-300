"""
Rotas de autenticação para Painel Jurídico v2
Endpoints: register, login, refresh token
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from database import User, Tenant, UserRole
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    decode_access_token
)
from main import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==================== REGISTRO ====================

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar novo usuário e criar tenant.
    Caso tenant_name não seja fornecido, usa o email como base.
    """
    # Verificar se email já existe (globalmente)
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado no sistema"
        )
    
    # Gerar slug para o tenant (baseado no email ou tenant_name)
    if user.tenant_name:
        slug = user.tenant_name.lower().replace(" ", "-")[:100]
    else:
        slug = user.email.split("@")[0].lower()[:100]
    
    # Verificar se slug já existe
    existing_tenant = db.query(Tenant).filter(Tenant.slug == slug).first()
    if existing_tenant:
        slug = f"{slug}-{uuid.uuid4().hex[:4]}"
    
    try:
        # Criar novo tenant
        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=user.tenant_name or user.email,
            slug=slug,
            email=user.email,
            is_active=True
        )
        db.add(tenant)
        db.flush()  # Flush para obter o ID do tenant
        
        # Criar novo usuário como admin do tenant
        new_user = User(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            email=user.email,
            full_name=user.full_name,
            hashed_password=hash_password(user.password),
            role=UserRole.ADMIN,  # Primeiro usuário é admin
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar usuário: {str(e)}"
        )

# ==================== LOGIN ====================

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login com email e senha.
    Retorna access_token e refresh_token.
    """
    # Buscar usuário por email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha inválidos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    # Atualizar last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Gerar tokens
    access_token_data = {
        "sub": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "role": user.role.value
    }
    refresh_token_data = {
        "sub": user.id,
        "tenant_id": user.tenant_id
    }
    
    access_token = create_access_token(access_token_data)
    refresh_token = create_refresh_token(refresh_token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=30 * 60  # 30 minutos em segundos
    )

# ==================== REFRESH TOKEN ====================

from pydantic import BaseModel

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """
    Renovar access token usando refresh token.
    Corpo da requisição: {"refresh_token": "seu-refresh-token"}
    """
    refresh_token_value = request.refresh_token
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token não fornecido"
        )
    
    # Decodificar refresh token
    payload = decode_refresh_token(refresh_token_value)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    # Buscar usuário
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo"
        )
    
    # Gerar novo access token
    access_token_data = {
        "sub": user.id,
        "email": user.email,
        "tenant_id": user.tenant_id,
        "role": user.role.value
    }
    
    access_token = create_access_token(access_token_data)
    new_refresh_token = create_refresh_token({
        "sub": user.id,
        "tenant_id": user.tenant_id
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=30 * 60
    )
