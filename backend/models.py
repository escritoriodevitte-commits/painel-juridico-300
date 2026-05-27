"""Modelos ORM multi-tenant. Toda entidade de negócio carrega tenant_id."""
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

ROLES = ("admin", "advogado", "cliente", "financeiro")


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    users: Mapped[list["User"]] = relationship(back_populates="tenant")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    nome: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    ativo: Mapped[bool] = mapped_column(default=True)
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_expira: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    tenant: Mapped[Tenant] = relationship(back_populates="users")


class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    nome: Mapped[str] = mapped_column(String(200))
    cpf_cnpj: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Processo(Base):
    __tablename__ = "processos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    numero: Mapped[str] = mapped_column(String(40))
    tribunal: Mapped[str | None] = mapped_column(String(120), nullable=True)
    vara: Mapped[str | None] = mapped_column(String(120), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="em_andamento")
    valor_causa: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    andamentos: Mapped[list["Andamento"]] = relationship(
        back_populates="processo", cascade="all, delete-orphan"
    )
    audiencias: Mapped[list["Audiencia"]] = relationship(
        back_populates="processo", cascade="all, delete-orphan"
    )


class Andamento(Base):
    __tablename__ = "andamentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    processo_id: Mapped[int] = mapped_column(ForeignKey("processos.id"), index=True)
    descricao: Mapped[str] = mapped_column(Text)
    data: Mapped[datetime] = mapped_column(DateTime, default=_now)

    processo: Mapped[Processo] = relationship(back_populates="andamentos")


class Audiencia(Base):
    __tablename__ = "audiencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    processo_id: Mapped[int] = mapped_column(ForeignKey("processos.id"), index=True)
    data: Mapped[datetime] = mapped_column(DateTime)
    tipo: Mapped[str] = mapped_column(String(60))
    local: Mapped[str | None] = mapped_column(String(200), nullable=True)

    processo: Mapped[Processo] = relationship(back_populates="audiencias")


class Tarefa(Base):
    __tablename__ = "tarefas"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    titulo: Mapped[str] = mapped_column(String(200))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    responsavel_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    processo_id: Mapped[int | None] = mapped_column(
        ForeignKey("processos.id"), nullable=True
    )
    prazo: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="aberta")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class Honorario(Base):
    __tablename__ = "honorarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), index=True)
    cliente_id: Mapped[int] = mapped_column(ForeignKey("clientes.id"), index=True)
    processo_id: Mapped[int | None] = mapped_column(
        ForeignKey("processos.id"), nullable=True
    )
    descricao: Mapped[str] = mapped_column(String(255))
    valor: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="pendente")
    vencimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(index=True)
    user_id: Mapped[int | None] = mapped_column(nullable=True)
    acao: Mapped[str] = mapped_column(String(40))
    entidade: Mapped[str] = mapped_column(String(40))
    entidade_id: Mapped[int | None] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=_now)
