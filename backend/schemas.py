"""
Schemas Pydantic para Painel Jurídico v2
Validação de requisições e respostas da API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from database import UserRole, SubscriptionPlan, SubscriptionStatus, PaymentStatus

# ==================== AUTH SCHEMAS ====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    tenant_name: Optional[str] = None  # Para registro novo

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

# ==================== TENANT SCHEMAS ====================

class TenantBase(BaseModel):
    name: str
    slug: str
    email: EmailStr

class TenantCreate(TenantBase):
    pass

class TenantResponse(TenantBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ==================== SUBSCRIPTION SCHEMAS ====================

class SubscriptionBase(BaseModel):
    plan: SubscriptionPlan

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionResponse(SubscriptionBase):
    id: str
    tenant_id: str
    status: SubscriptionStatus
    monthly_price: float
    mercado_pago_subscription_id: Optional[str]
    started_at: datetime
    next_billing_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== PAYMENT SCHEMAS ====================

class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None

class PaymentCreate(PaymentBase):
    subscription_id: str

class PaymentResponse(PaymentBase):
    id: str
    tenant_id: str
    status: PaymentStatus
    currency: str
    mercado_pago_payment_id: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== ERROR SCHEMAS ====================

class ErrorResponse(BaseModel):
    detail: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
