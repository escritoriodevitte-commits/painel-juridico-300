"""CRUD de tarefas (escopo de tenant; escrita: admin/advogado)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import audit, get_current_user, require_roles

router = APIRouter(prefix="/api/v1/tarefas", tags=["tarefas"])

_ESCRITA = require_roles("admin", "advogado")


def _get_owned(db: Session, tarefa_id: int, tenant_id: int) -> models.Tarefa:
    obj = db.get(models.Tarefa, tarefa_id)
    if obj is None or obj.tenant_id != tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tarefa não encontrada")
    return obj


@router.get("", response_model=list[schemas.TarefaOut])
def listar(
    status_filtro: str | None = None,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(models.Tarefa).where(models.Tarefa.tenant_id == user.tenant_id)
    if status_filtro:
        stmt = stmt.where(models.Tarefa.status == status_filtro)
    return list(db.scalars(stmt.order_by(models.Tarefa.prazo)))


@router.post("", response_model=schemas.TarefaOut, status_code=201)
def criar(
    payload: schemas.TarefaIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    obj = models.Tarefa(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(obj)
    db.flush()
    audit(db, user, "create", "tarefa", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{tarefa_id}", response_model=schemas.TarefaOut)
def obter(
    tarefa_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_owned(db, tarefa_id, user.tenant_id)


@router.put("/{tarefa_id}", response_model=schemas.TarefaOut)
def atualizar(
    tarefa_id: int,
    payload: schemas.TarefaIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    obj = _get_owned(db, tarefa_id, user.tenant_id)
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    audit(db, user, "update", "tarefa", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{tarefa_id}", status_code=204)
def remover(
    tarefa_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    obj = _get_owned(db, tarefa_id, user.tenant_id)
    db.delete(obj)
    audit(db, user, "delete", "tarefa", tarefa_id)
    db.commit()
