"""Hash de senha (bcrypt) e emissão/validação de JWT (HS256)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings

# bcrypt aceita no máximo 72 bytes
_MAX = 72


def hash_password(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8")[:_MAX], bcrypt.gensalt()).decode("utf-8")


def verify_password(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8")[:_MAX], senha_hash.encode("utf-8"))
    except ValueError:
        return False


def create_token(
    *, sub: int, tenant_id: int, role: str, token_type: str, expires: timedelta
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(sub),
        "tenant_id": tenant_id,
        "role": role,
        "type": token_type,
        "iat": now,
        "exp": now + expires,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALG)


def create_access_token(*, sub: int, tenant_id: int, role: str) -> str:
    return create_token(
        sub=sub,
        tenant_id=tenant_id,
        role=role,
        token_type="access",
        expires=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN),
    )


def create_refresh_token(*, sub: int, tenant_id: int, role: str) -> str:
    return create_token(
        sub=sub,
        tenant_id=tenant_id,
        role=role,
        token_type="refresh",
        expires=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    # algorithms explícito -> nunca aceita alg:none
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALG])
