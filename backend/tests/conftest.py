import os

# Banco em memória para a engine real (usada só no startup); queries usam o override.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret")
# Rate limit alto nos testes funcionais (o limiter é exercitado em teste próprio).
os.environ.setdefault("LOGIN_RATE_MAX", "100000")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import get_db
from backend.main import app
from backend.models import Base


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    def _override():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def register(client, tenant="Escritório A", email="admin@a.com", senha="senha12345"):
    r = client.post(
        "/api/v1/auth/register",
        json={"tenant_nome": tenant, "nome": "Admin", "email": email, "senha": senha},
    )
    assert r.status_code == 201, r.text
    return r.json()


def login(client, email, senha):
    r = client.post(
        "/api/v1/auth/login", data={"username": email, "password": senha}
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
