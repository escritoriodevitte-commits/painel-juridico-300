"""CRUD de processos + andamentos e audiências (escopo de tenant)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import audit, get_current_user, require_roles

router = APIRouter(prefix="/api/v1/processos", tags=["processos"])

_ESCRITA = require_roles("admin", "advogado")


def _get_proc(db: Session, processo_id: int, tenant_id: int) -> models.Processo:
    obj = db.get(models.Processo, processo_id)
    if obj is None or obj.tenant_id != tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Processo não encontrado")
    return obj


@router.get("", response_model=list[schemas.ProcessoOut])
def listar(
    skip: int = 0,
    limit: int = 50,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Processo)
        .where(models.Processo.tenant_id == user.tenant_id)
        .order_by(models.Processo.id)
        .offset(skip)
        .limit(min(limit, 200))
    )
    return list(db.scalars(stmt))


@router.post("", response_model=schemas.ProcessoOut, status_code=201)
def criar(
    payload: schemas.ProcessoIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    cliente = db.get(models.Cliente, payload.cliente_id)
    if cliente is None or cliente.tenant_id != user.tenant_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cliente inválido")
    obj = models.Processo(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(obj)
    db.flush()
    audit(db, user, "create", "processo", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/{processo_id}", response_model=schemas.ProcessoOut)
def obter(
    processo_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _get_proc(db, processo_id, user.tenant_id)


@router.put("/{processo_id}", response_model=schemas.ProcessoOut)
def atualizar(
    processo_id: int,
    payload: schemas.ProcessoIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    obj = _get_proc(db, processo_id, user.tenant_id)
    if payload.cliente_id != obj.cliente_id:
        cliente = db.get(models.Cliente, payload.cliente_id)
        if cliente is None or cliente.tenant_id != user.tenant_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cliente inválido")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    audit(db, user, "update", "processo", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{processo_id}", status_code=204)
def remover(
    processo_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_roles("admin")),
):
    obj = _get_proc(db, processo_id, user.tenant_id)
    db.delete(obj)
    audit(db, user, "delete", "processo", processo_id)
    db.commit()


# ---------- Andamentos ----------
@router.get("/{processo_id}/andamentos", response_model=list[schemas.AndamentoOut])
def listar_andamentos(
    processo_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_proc(db, processo_id, user.tenant_id)
    stmt = (
        select(models.Andamento)
        .where(models.Andamento.processo_id == processo_id)
        .order_by(models.Andamento.data.desc())
    )
    return list(db.scalars(stmt))


@router.post(
    "/{processo_id}/andamentos", response_model=schemas.AndamentoOut, status_code=201
)
def criar_andamento(
    processo_id: int,
    payload: schemas.AndamentoIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    _get_proc(db, processo_id, user.tenant_id)
    obj = models.Andamento(
        tenant_id=user.tenant_id, processo_id=processo_id, descricao=payload.descricao
    )
    db.add(obj)
    db.flush()
    audit(db, user, "create", "andamento", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


# ---------- Audiências ----------
@router.get("/{processo_id}/audiencias", response_model=list[schemas.AudienciaOut])
def listar_audiencias(
    processo_id: int,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_proc(db, processo_id, user.tenant_id)
    stmt = (
        select(models.Audiencia)
        .where(models.Audiencia.processo_id == processo_id)
        .order_by(models.Audiencia.data)
    )
    return list(db.scalars(stmt))


@router.post(
    "/{processo_id}/audiencias", response_model=schemas.AudienciaOut, status_code=201
)
def criar_audiencia(
    processo_id: int,
    payload: schemas.AudienciaIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    _get_proc(db, processo_id, user.tenant_id)
    obj = models.Audiencia(
        tenant_id=user.tenant_id, processo_id=processo_id, **payload.model_dump()
    )
    db.add(obj)
    db.flush()
    audit(db, user, "create", "audiencia", obj.id)
    db.commit()
    db.refresh(obj)
    return obj
