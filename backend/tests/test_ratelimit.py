"""Teste do limiter isoladamente (independente do limite alto usado na suíte)."""
import pytest
from fastapi import HTTPException

from backend.ratelimit import rate_limit


class _FakeClient:
    host = "1.2.3.4"


class _FakeURL:
    path = "/api/v1/auth/login"


class _FakeRequest:
    client = _FakeClient()
    url = _FakeURL()


def test_rate_limit_bloqueia_apos_limite():
    dep = rate_limit(max_requests=3, window_seconds=60)
    req = _FakeRequest()
    # 3 chamadas passam
    for _ in range(3):
        dep(req)
    # a 4ª estoura
    with pytest.raises(HTTPException) as exc:
        dep(req)
    assert exc.value.status_code == 429
