"""CRUD de clientes (escopo de tenant; escrita: admin/advogado)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import audit, get_current_user, require_roles

router = APIRouter(prefix="/api/v1/clientes", tags=["clientes"])


def _get_owned(db: Session, cliente_id: int, tenant_id: int) -> models.Cliente:
    obj = db.get(models.Cliente, cliente_id)
    if obj is None or obj.tenant_id != tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Cliente não encontrado")
    return obj


@router.get("", response_model=list[schemas.ClienteOut])
def listar(
    skip: int = 0,
    limit: int = 50,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Cliente)
        .where(models.Cliente.tenant_id == user.tenant_id)
        .order_by(models.Cliente.id)
        .offset(skip)
        .limit(min(limit, 200))
    )
    return list(db.scalars(stmt))


@router.post("", response_model=schemas.ClienteOut, status_code=201)
def criar(
    payload: schemas.ClienteIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin", "advogado")),
):
    obj = models.Cliente(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(obj)
    db.flush()
    audit(db, user, "create", "cliente", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{cliente_id}", response_model=schemas.ClienteOut)
def obter(
    cliente_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned(db, cliente_id, user.tenant_id)


@router.put("/{cliente_id}", response_model=schemas.ClienteOut)
def atualizar(
    cliente_id: int,
    payload: schemas.ClienteIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin", "advogado")),
):
    obj = _get_owned(db, cliente_id, user.tenant_id)
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    audit(db, user, "update", "cliente", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{cliente_id}", status_code=204)
def remover(
    cliente_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin")),
):
    obj = _get_owned(db, cliente_id, user.tenant_id)
    db.delete(obj)
    audit(db, user, "delete", "cliente", cliente_id)
    db.commit()
