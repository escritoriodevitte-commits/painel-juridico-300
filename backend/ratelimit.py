"""Rate limiting simples em memória (janela fixa).

Adequado e barato para 1 instância (free tier). Para múltiplos workers/instâncias,
trocar por um backend compartilhado (ex.: Redis).
"""
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Request, status

from .config import settings

_hits: dict[str, list[float]] = defaultdict(list)


def rate_limit(max_requests: int, window_seconds: int):
    def dependency(request: Request) -> None:
        client = request.client.host if request.client else "anon"
        key = f"{client}:{request.url.path}"
        now = time.monotonic()
        recent = [t for t in _hits[key] if now - t < window_seconds]
        if len(recent) >= max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas requisições. Tente novamente em instantes.",
                headers={"Retry-After": str(window_seconds)},
            )
        recent.append(now)
        _hits[key] = recent

    return dependency


# Limite usado nos endpoints sensíveis de autenticação.
login_rate_limit = Depends(
    rate_limit(settings.LOGIN_RATE_MAX, settings.LOGIN_RATE_WINDOW_SEC)
)
