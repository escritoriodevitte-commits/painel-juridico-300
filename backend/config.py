"""Configuração lida de variáveis de ambiente (segredos nunca no código)."""
import os


class Settings:
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-insecure-change-me")
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MIN", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    PASSWORD_RESET_EXPIRE_MIN: int = int(os.environ.get("PASSWORD_RESET_EXPIRE_MIN", "30"))
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./backend_app.db")
    OPENAI_API_KEY: str | None = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o")


settings = Settings()
