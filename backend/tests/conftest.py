"""
Configuração e fixtures para testes pytest
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import uuid
from datetime import datetime

from main import app, get_db
from database import Base, Tenant, User, UserRole
from auth import hash_password
from passlib.context import CryptContext

# Usar banco de dados em memória para testes
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# CRÍTICO: Criar tabelas antes de usar
Base.metadata.create_all(bind=engine, checkfirst=True)

test_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password_test(password: str) -> str:
    """Hash de senha para testes com backend compatível."""
    return test_pwd_context.hash(password)


def override_get_db():
    """Override da dependência get_db para usar DB de teste"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Fornece sessão de banco para testes"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Cliente HTTP para testes"""
    return TestClient(app)


@pytest.fixture(scope="function")
def test_tenant(db):
    """Cria um tenant de teste"""
    tenant = Tenant(
        id=str(uuid.uuid4()),
        name="Test Company",
        slug="test-company",
        email="test@company.com",
        is_active=True
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def test_admin_user(db, test_tenant):
    """Cria um usuário admin de teste"""
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=test_tenant.id,
        email="admin@company.com",
        full_name="Admin User",
        hashed_password=hash_password_test("TestPass123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_regular_user(db, test_tenant):
    """Cria um usuário regular de teste"""
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=test_tenant.id,
        email="user@company.com",
        full_name="Regular User",
        hashed_password=hash_password_test("TestPass123"),
        role=UserRole.USER,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_token(client, test_admin_user):
    """Obtém token JWT do usuário admin"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_admin_user.email,
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def user_token(client, test_regular_user):
    """Obtém token JWT do usuário regular"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_regular_user.email,
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_headers(admin_token):
    """Headers com autenticação do admin"""
    return {"Authorization": f"Bearer {admin_token}"}
