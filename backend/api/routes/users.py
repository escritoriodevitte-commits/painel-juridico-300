"""
Rotas de gerenciamento de usuários para o Admin Dashboard
Endpoints: listar, criar, atualizar, deletar usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from schemas import UserResponse, UserCreate
from database import User, UserRole, Tenant
from dependencies import get_current_user, get_current_tenant, require_admin, get_db
from auth import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users Management"])

# ==================== LISTAR USUÁRIOS ====================

@router.get("", response_model=List[UserResponse])
async def list_users(
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Listar todos os usuários do tenant (apenas admin).
    Parâmetros de paginação: skip, limit
    """
    users = db.query(User).filter(
        User.tenant_id == admin.tenant_id
    ).offset(skip).limit(limit).all()
    
    return [
        UserResponse(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at
        )
        for u in users
    ]

# ==================== OBTER USUÁRIO ATUAL ====================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Obter dados do usuário autenticado"""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

# ==================== CRIAR USUÁRIO ====================

@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Criar novo usuário no tenant (apenas admin).
    O novo usuário terá role USER por padrão.
    """
    # Verificar se email já existe no tenant
    existing_user = db.query(User).filter(
        User.email == user_data.email,
        User.tenant_id == admin.tenant_id
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado neste tenant"
        )
    
    try:
        # Criar novo usuário
        new_user = User(
            id=str(uuid.uuid4()),
            tenant_id=admin.tenant_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hash_password(user_data.password),
            role=UserRole.USER,  # Novos usuários são USER
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
            detail=f"Erro ao criar usuário: {str(e)}"
        )

# ==================== ATUALIZAR USUÁRIO ====================

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: dict,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Atualizar dados de um usuário (apenas admin).
    Campos atualizáveis: full_name, is_active, role
    """
    # Buscar usuário no tenant
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == admin.tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Impedir alteração do próprio usuário
    if user.id == admin.id and "is_active" in user_data and not user_data["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode desativar sua própria conta"
        )
    
    # Atualizar campos
    if "full_name" in user_data:
        user.full_name = user_data["full_name"]
    if "is_active" in user_data:
        user.is_active = user_data["is_active"]
    if "role" in user_data and user_data["role"] in ["admin", "user"]:
        user.role = UserRole(user_data["role"])
    
    user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            created_at=user.created_at
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar usuário: {str(e)}"
        )

# ==================== DELETAR USUÁRIO ====================

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Deletar um usuário (apenas admin).
    Impede deletar o próprio usuário.
    """
    # Buscar usuário no tenant
    user = db.query(User).filter(
        User.id == user_id,
        User.tenant_id == admin.tenant_id
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Impedir deletar a si mesmo
    if user.id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você não pode deletar sua própria conta"
        )
    
    try:
        db.delete(user)
        db.commit()
        
        return {
            "message": f"Usuário {user.email} deletado com sucesso",
            "user_id": user.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar usuário: {str(e)}"
        )

# ==================== ALTERAR SENHA ====================

@router.post("/me/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Alterar senha do usuário autenticado.
    Requer senha atual para validação.
    """
    from auth import verify_password, hash_password
    
    # Verificar senha atual
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha atual incorreta"
        )
    
    # Validar nova senha
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova senha deve ter pelo menos 8 caracteres"
        )
    
    # Atualizar senha
    current_user.hashed_password = hash_password(new_password)
    current_user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        return {"message": "Senha alterada com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao alterar senha: {str(e)}"
        )
