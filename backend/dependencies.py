"""
Dependencies para FastAPI
Autenticação JWT, injeção de usuário autenticado, etc.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from sqlalchemy.orm import Session
from typing import Optional

from auth import decode_access_token
from database import User, Tenant

def get_db():
    """Dependency para obter sessão do banco de dados"""
    from main import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obter o usuário autenticado a partir do JWT token.
    Valida o token e retorna o usuário.
    """
    # Extrair token do header Authorization
    auth_header = request.headers.get("Authorization", "")
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.replace("Bearer ", "")
    
    # Decodificar token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    if not user_id or not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não contém informações de usuário",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar usuário no banco
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo"
        )
    
    return user

async def get_current_tenant(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Tenant:
    """
    Dependency para obter o tenant do usuário autenticado.
    """
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant não encontrado"
        )
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant inativo"
        )
    
    return tenant

async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para exigir que o usuário tenha role ADMIN.
    """
    from database import UserRole
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores"
        )
    
    return user
