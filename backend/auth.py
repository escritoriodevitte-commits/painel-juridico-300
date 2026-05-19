"""
Utilitários de autenticação para Painel Jurídico v2
Inclui geração de tokens JWT, password hashing e validação
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# ==================== CONFIGURAÇÕES ====================

SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-mudar-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==================== PASSWORD HASHING ====================

def hash_password(password: str) -> str:
    """Hash uma senha usando bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se uma senha coincide com o hash"""
    return pwd_context.verify(plain_password, hashed_password)

# ==================== JWT TOKENS ====================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Cria um JWT refresh token com validade de 7 dias"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verifica e decodifica um JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica um access token e retorna os dados se válido"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verifica se não é refresh token
        if payload.get("type") == "refresh":
            return None
        
        return payload
    except JWTError:
        return None

def decode_refresh_token(token: str) -> Optional[dict]:
    """Decodifica um refresh token e retorna os dados se válido"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verifica se é refresh token
        if payload.get("type") != "refresh":
            return None
        
        return payload
    except JWTError:
        return None
