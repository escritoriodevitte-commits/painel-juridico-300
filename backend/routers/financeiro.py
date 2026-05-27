"""Financeiro: honorários (escrita: admin/financeiro; leitura inclui advogado)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import audit, require_roles

router = APIRouter(prefix="/api/v1/financeiro", tags=["financeiro"])

_LEITURA = require_roles("admin", "financeiro", "advogado")
_ESCRITA = require_roles("admin", "financeiro")


def _get_owned(db: Session, hon_id: int, tenant_id: int) -> models.Honorario:
    obj = db.get(models.Honorario, hon_id)
    if obj is None or obj.tenant_id != tenant_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Honorário não encontrado")
    return obj


@router.get("/honorarios", response_model=list[schemas.HonorarioOut])
def listar(
    user: models.User = Depends(_LEITURA),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Honorario)
        .where(models.Honorario.tenant_id == user.tenant_id)
        .order_by(models.Honorario.vencimento)
    )
    return list(db.scalars(stmt))


@router.post("/honorarios", response_model=schemas.HonorarioOut, status_code=201)
def criar(
    payload: schemas.HonorarioIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    cliente = db.get(models.Cliente, payload.cliente_id)
    if cliente is None or cliente.tenant_id != user.tenant_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Cliente inválido")
    obj = models.Honorario(tenant_id=user.tenant_id, **payload.model_dump())
    db.add(obj)
    db.flush()
    audit(db, user, "create", "honorario", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/honorarios/{hon_id}", response_model=schemas.HonorarioOut)
def atualizar(
    hon_id: int,
    payload: schemas.HonorarioIn,
    db: Session = Depends(get_db),
    user: models.User = Depends(_ESCRITA),
):
    obj = _get_owned(db, hon_id, user.tenant_id)
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    audit(db, user, "update", "honorario", obj.id)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/relatorio", response_model=schemas.FinanceiroResumoOut)
def relatorio(
    user: models.User = Depends(_LEITURA),
    db: Session = Depends(get_db),
):
    honorarios = list(
        db.scalars(
            select(models.Honorario).where(
                models.Honorario.tenant_id == user.tenant_id
            )
        )
    )
    pago = sum(h.valor for h in honorarios if h.status == "pago")
    pendente = sum(h.valor for h in honorarios if h.status == "pendente")
    return schemas.FinanceiroResumoOut(
        total=pago + pendente,
        pago=pago,
        pendente=pendente,
        qtd=len(honorarios),
    )
