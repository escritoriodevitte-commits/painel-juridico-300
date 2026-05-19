"""
Painel Jurídico v2 - Backend FastAPI
Sistema SaaS de gestão jurídica com suporte multi-tenant
"""

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# ==================== CONFIGURAÇÕES ====================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/painel_juridico"
)

SECRET_KEY = os.getenv("SECRET_KEY", "sua-chave-secreta-mudar-em-producao")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MERCADO_PAGO_TOKEN = os.getenv("MERCADO_PAGO_TOKEN", "")
MERCADO_PAGO_PUBLIC_KEY = os.getenv("MERCADO_PAGO_PUBLIC_KEY", "")

# ==================== APLICAÇÃO FASTAPI ====================

app = FastAPI(
    title="Painel Jurídico v2 API",
    description="API SaaS para gestão jurídica",
    version="2.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DATABASE ====================

engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== ROTAS PRINCIPAIS ====================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Painel Jurídico v2 API",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check com verificação de banco de dados"""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")

# ==================== IMPORTAR ROTAS ====================

from api.routes.auth import router as auth_router
from api.routes.users import router as users_router
from api.routes.ia_gerador import router as ia_router

# Incluir routers
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(ia_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    """Evento de inicialização da aplicação"""
    print("🚀 Painel Jurídico v2 API iniciado")
    print(f"📊 Banco de dados: {DATABASE_URL}")
    print(f"🔐 Autenticação: JWT")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de encerramento da aplicação"""
    print("🛑 Painel Jurídico v2 API finalizado")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
