"""Aplicação FastAPI do SaaS jurídico. Execute: uvicorn backend.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import engine
from .models import Base
from .routers import auth, clientes, financeiro, ia, processos, tarefas

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Em produção, usar migrações (Alembic) em vez de create_all.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="SaaS Jurídico Trabalhista",
    version="0.1.0",
    description="API multi-tenant para escritórios de advocacia trabalhista.",
    lifespan=lifespan,
)


@app.get("/health", tags=["infra"])
def health() -> dict:
    return {"status": "healthy"}


app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(processos.router)
app.include_router(tarefas.router)
app.include_router(financeiro.router)
app.include_router(ia.router)
