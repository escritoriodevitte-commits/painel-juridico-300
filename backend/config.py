"""Configuração lida de variáveis de ambiente (segredos nunca no código)."""
import os


def _normalize_db_url(url: str) -> str:
    # Render/Heroku entregam "postgres://"; SQLAlchemy 2 precisa do driver explícito.
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


class Settings:
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MIN", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    PASSWORD_RESET_EXPIRE_MIN: int = int(os.environ.get("PASSWORD_RESET_EXPIRE_MIN", "30"))

    DATABASE_URL: str = _normalize_db_url(
        os.environ.get("DATABASE_URL", "sqlite:///./backend_app.db")
    )

    # Em produção define-se a tabela na criação; em dev (SQLite) cria automaticamente.
    AUTO_CREATE_TABLES: bool = os.environ.get(
        "AUTO_CREATE_TABLES", "1"
    ).lower() in ("1", "true", "yes")

    # CORS: lista separada por vírgula. "*" libera tudo (apenas para dev).
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.environ.get("CORS_ORIGINS", "*").split(",")
        if o.strip()
    ]

    # Rate limit do login/reset (janela fixa, em processo).
    LOGIN_RATE_MAX: int = int(os.environ.get("LOGIN_RATE_MAX", "10"))
    LOGIN_RATE_WINDOW_SEC: int = int(os.environ.get("LOGIN_RATE_WINDOW_SEC", "60"))

    # IA via Claude (Anthropic). Sem chave, o endpoint usa template local (R$ 0).
    ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
    # Padrão: modelo Claude mais capaz. Para baratear, defina CLAUDE_MODEL=claude-haiku-4-5.
    CLAUDE_MODEL: str = os.environ.get("CLAUDE_MODEL", "claude-opus-4-7")


settings = Settings()
