"""Aplicação FastAPI do SaaS jurídico. Execute: uvicorn backend.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine
from .models import Base
from .routers import auth, clientes, financeiro, ia, processos, tarefas

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Dev/SQLite: cria tabelas automaticamente. Produção: usar Alembic
    # (alembic upgrade head) e definir AUTO_CREATE_TABLES=0.
    if settings.AUTO_CREATE_TABLES:
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SaaS Jurídico Trabalhista",
    version="0.1.0",
    description="API multi-tenant para escritórios de advocacia trabalhista.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    # CSP estrito nas respostas de API; isenta o Swagger/Redoc (carregam JS de CDN).
    if not request.url.path.startswith(_DOCS_PATHS):
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'"
        )
    return response


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(processos.router)
app.include_router(tarefas.router)
app.include_router(financeiro.router)
app.include_router(ia.router)
