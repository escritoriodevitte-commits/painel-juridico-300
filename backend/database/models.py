"""
Modelos SQLAlchemy para Painel Jurídico v2
Define estrutura do banco de dados para usuários, tenants, assinaturas e pagamentos
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

Base = declarative_base()

# ==================== ENUMS ====================

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    FAILED = "failed"
    REFUNDED = "refunded"

# ==================== MODELOS ====================

class Tenant(Base):
    """
    Representa um tenant (cliente/organização) no sistema.
    Cada tenant tem seus próprios dados isolados.
    """
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relacionamentos
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="tenant", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    """
    Usuários do sistema com suporte multi-tenant.
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Único por tenant
    __table_args__ = (
        # email deve ser único por tenant
    )
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="users")

class Subscription(Base):
    """
    Assinaturas de planos de pagamento.
    """
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    plan = Column(Enum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.INACTIVE)
    
    # Dados de assinatura Mercado Pago
    mercado_pago_subscription_id = Column(String(255), nullable=True, unique=True)
    
    # Datas
    started_at = Column(DateTime, default=datetime.utcnow)
    ends_at = Column(DateTime, nullable=True)
    renewal_date = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Informações de cobrança
    monthly_price = Column(Float, default=0.0)
    next_billing_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")

class Payment(Base):
    """
    Registro de pagamentos processados via Mercado Pago.
    """
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=True)
    
    # Dados do pagamento
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="BRL")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Mercado Pago
    mercado_pago_payment_id = Column(String(255), nullable=True, unique=True)
    mercado_pago_reference = Column(String(255), nullable=True)
    
    # Descrição
    description = Column(String(500), nullable=True)
    
    # Datas
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    
    # Relacionamentos
    tenant = relationship("Tenant", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")

class AuditLog(Base):
    """
    Log de auditoria para rastrear ações importantes.
    """
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=False)
    
    details = Column(String(1000), nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
