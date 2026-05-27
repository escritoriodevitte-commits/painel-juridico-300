# Imagem do backend SaaS. Build a partir da RAIZ do repo:
#   docker build -f backend/Dockerfile -t saas-juridico .
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    AUTO_CREATE_TABLES=0

WORKDIR /app

COPY backend/requirements.txt backend/requirements.txt
RUN pip install -r backend/requirements.txt

COPY backend ./backend
COPY alembic.ini ./alembic.ini

EXPOSE 8000

# Aplica migrações e sobe gunicorn com workers uvicorn.
CMD ["sh", "-c", "alembic upgrade head && gunicorn backend.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}"]
