"""Schemas Pydantic (validação de entrada/saída)."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

Role = Literal["admin", "advogado", "cliente", "financeiro"]


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class RegisterIn(BaseModel):
    tenant_nome: str = Field(min_length=1, max_length=200)
    nome: str = Field(min_length=1, max_length=200)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)


class UserCreateIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    role: Role


class UserOut(ORMModel):
    id: int
    tenant_id: int
    nome: str
    email: EmailStr
    role: Role
    ativo: bool


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshIn(BaseModel):
    refresh_token: str


class PasswordResetRequestIn(BaseModel):
    email: EmailStr


class PasswordResetConfirmIn(BaseModel):
    token: str
    nova_senha: str = Field(min_length=8, max_length=128)


# ---------- Clientes ----------
class ClienteIn(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    cpf_cnpj: str | None = Field(default=None, max_length=20)
    email: EmailStr | None = None
    telefone: str | None = Field(default=None, max_length=40)
    endereco: str | None = Field(default=None, max_length=255)


class ClienteOut(ORMModel):
    id: int
    nome: str
    cpf_cnpj: str | None
    email: str | None
    telefone: str | None
    endereco: str | None
    created_at: datetime


# ---------- Processos ----------
class ProcessoIn(BaseModel):
    cliente_id: int
    numero: str = Field(min_length=1, max_length=40)
    tribunal: str | None = Field(default=None, max_length=120)
    vara: str | None = Field(default=None, max_length=120)
    status: str = Field(default="em_andamento", max_length=40)
    valor_causa: float = 0.0


class ProcessoOut(ORMModel):
    id: int
    cliente_id: int
    numero: str
    tribunal: str | None
    vara: str | None
    status: str
    valor_causa: float
    created_at: datetime


class AndamentoIn(BaseModel):
    descricao: str = Field(min_length=1)


class AndamentoOut(ORMModel):
    id: int
    processo_id: int
    descricao: str
    data: datetime


class AudienciaIn(BaseModel):
    data: datetime
    tipo: str = Field(min_length=1, max_length=60)
    local: str | None = Field(default=None, max_length=200)


class AudienciaOut(ORMModel):
    id: int
    processo_id: int
    data: datetime
    tipo: str
    local: str | None


# ---------- Tarefas ----------
class TarefaIn(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    descricao: str | None = None
    responsavel_id: int | None = None
    processo_id: int | None = None
    prazo: date | None = None
    status: Literal["aberta", "em_andamento", "concluida"] = "aberta"


class TarefaOut(ORMModel):
    id: int
    titulo: str
    descricao: str | None
    responsavel_id: int | None
    processo_id: int | None
    prazo: date | None
    status: str
    created_at: datetime


# ---------- Financeiro ----------
class HonorarioIn(BaseModel):
    cliente_id: int
    processo_id: int | None = None
    descricao: str = Field(min_length=1, max_length=255)
    valor: float = Field(ge=0)
    status: Literal["pendente", "pago", "cancelado"] = "pendente"
    vencimento: date | None = None


class HonorarioOut(ORMModel):
    id: int
    cliente_id: int
    processo_id: int | None
    descricao: str
    valor: float
    status: str
    vencimento: date | None
    created_at: datetime


class FinanceiroResumoOut(BaseModel):
    total: float
    pago: float
    pendente: float
    qtd: int


# ---------- IA ----------
class PeticaoIn(BaseModel):
    tipo: str = Field(min_length=1, max_length=60)
    cliente_nome: str = Field(min_length=1, max_length=200)
    fatos: str = Field(min_length=1)
    pedidos: str = Field(min_length=1)


class PeticaoOut(BaseModel):
    tipo: str
    fonte: Literal["claude", "template"]
    texto: str
