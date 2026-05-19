# 🚀 Guia de Deployment - Painel Jurídico v2

Instruções completas para deploy em produção na AWS, DigitalOcean ou ambiente local.

## 📋 Índice
1. [Setup Local](#setup-local)
2. [Testes](#testes)
3. [Docker](#docker)
4. [AWS Deployment](#aws-deployment)
5. [DigitalOcean](#digitalocean)
6. [Segurança](#segurança)
7. [Monitoramento](#monitoramento)

---

## Setup Local

### Pré-requisitos
- Python 3.11+
- PostgreSQL 14+ (ou SQLite para desenvolvimento)
- Git

### Instalação Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/painel-juridico-v2.git
cd painel_juridico_v2/backend

# 2. Criar virtual environment
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env

# 5. Editar .env com valores corretos
nano .env  # ou use seu editor preferido
```

### Arquivo .env para Desenvolvimento

```env
# Banco de dados
DATABASE_URL=postgresql://user:password@localhost:5432/painel_juridico

# Segurança
SECRET_KEY=sua-chave-aleatoria-minimo-32-caracteres-mude-em-producao
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (opcional)
OPENAI_API_KEY=sk-proj-sua-chave-aqui

# Mercado Pago (opcional)
MERCADO_PAGO_TOKEN=seu-token
MERCADO_PAGO_PUBLIC_KEY=sua-chave-publica

# Frontend
FRONTEND_URL=http://localhost:3000

# Debug
DEBUG=false
```

### Inicializar Banco de Dados

```bash
# 1. Aplicar migrations
alembic upgrade head

# 2. Verificar status
alembic current

# 3. Criar usuário admin inicial (opcional)
python -c "
from database import SessionLocal, Tenant, User, UserRole
from auth import hash_password
import uuid

db = SessionLocal()
tenant = Tenant(
    id=str(uuid.uuid4()),
    name='Admin Company',
    slug='admin-company',
    email='admin@example.com'
)
db.add(tenant)
db.flush()

user = User(
    id=str(uuid.uuid4()),
    tenant_id=tenant.id,
    email='admin@example.com',
    full_name='Admin',
    hashed_password=hash_password('SenhaForte123'),
    role=UserRole.ADMIN
)
db.add(user)
db.commit()
print('✅ Usuário admin criado: admin@example.com')
"
```

### Rodar Localmente

```bash
# Desenvolvimento (com reload)
python main.py

# Ou com uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Acessar documentação
open http://localhost:8000/docs
```

---

## Testes

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=. --cov-report=html

# Apenas testes de IA
pytest tests/test_ia_routes.py -v

# Apenas um teste
pytest tests/test_ia_routes.py::TestIAStatus::test_status_ia_authenticated -v
```

### Resultado Esperado

```
tests/test_ia_routes.py::TestIAStatus::test_status_ia_authenticated PASSED
tests/test_ia_routes.py::TestIATiposPeca::test_listar_tipos_peca_authenticated PASSED
tests/test_ia_routes.py::TestGerarPeca::test_gerar_peca_reclamatoria_trabalhista PASSED
...
======================== 50+ passed in 5.23s ========================
```

---

## Docker

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose (Desenvolvimento)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: painel
      POSTGRES_PASSWORD: senha123
      POSTGRES_DB: painel_juridico
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U painel"]
      interval: 10s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://painel:senha123@postgres:5432/painel_juridico
      SECRET_KEY: ${SECRET_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      DEBUG: "false"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

### Build e Deploy com Docker

```bash
# Build da imagem
docker build -t painel-juridico:latest .

# Rodar container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@host:5432/db \
  -e SECRET_KEY=sua-chave \
  painel-juridico:latest

# Com Docker Compose
docker-compose up -d
docker-compose logs -f api
docker-compose down
```

---

## AWS Deployment

### Opção 1: EC2 + RDS

#### 1. Criar RDS (PostgreSQL)

```bash
# Via AWS CLI
aws rds create-db-instance \
  --db-instance-identifier painel-juridico-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password "SenhaForte123!" \
  --allocated-storage 20 \
  --publicly-accessible false
```

#### 2. Criar EC2 Instance

```bash
# Launch EC2 com Ubuntu 22.04 LTS
# Security Group: Abrir porta 8000 (inbound)
# Key Pair: Criar e salvar .pem

# SSH into instance
ssh -i seu-key.pem ubuntu@seu-ec2-ip

# Install Python e dependências
sudo apt update
sudo apt install -y python3.11 python3-pip postgresql-client
python3 -m venv venv
source venv/bin/activate

# Clone repo
git clone https://github.com/seu-usuario/painel-juridico-v2.git
cd painel_juridico_v2/backend

# Install Python packages
pip install -r requirements.txt

# Configure .env
nano .env  # Adicionar DATABASE_URL do RDS

# Run migrations
alembic upgrade head

# Start server
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 3. Setup Reverse Proxy (Nginx)

```bash
sudo apt install -y nginx

# Criar arquivo de config
sudo nano /etc/nginx/sites-available/painel
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/painel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. SSL com Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d seu-dominio.com
```

#### 5. Systemd Service (Auto-restart)

```bash
sudo nano /etc/systemd/system/painel-juridico.service
```

```ini
[Unit]
Description=Painel Jurídico v2 API
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/painel_juridico_v2/backend
Environment="PATH=/home/ubuntu/painel_juridico_v2/backend/venv/bin"
ExecStart=/home/ubuntu/painel_juridico_v2/backend/venv/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable painel-juridico
sudo systemctl start painel-juridico
sudo systemctl status painel-juridico
```

### Opção 2: ECS + RDS (Container)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name painel-juridico

# 2. Build e push da imagem
docker build -t painel-juridico:latest .
docker tag painel-juridico:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/painel-juridico:latest
aws ecr get-login-password | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/painel-juridico:latest

# 3. Create ECS Cluster e Task Definition (via Console ou Terraform)
# 4. Create Service com Auto Scaling
```

---

## DigitalOcean

### Opção 1: App Platform (Mais fácil)

1. Conectar GitHub repository
2. Create App
3. Configure:
   ```yaml
   name: painel-juridico
   services:
   - name: api
     github:
       repo: seu-usuario/painel-juridico-v2
       branch: main
     build_command: "pip install -r requirements.txt && alembic upgrade head"
     run_command: "uvicorn main:app --host 0.0.0.0 --port 8080"
     envs:
     - key: DATABASE_URL
       scope: RUN_AND_BUILD_TIME
       value: ${db.username}:${db.password}@${db.host}:${db.port}/${db.name}
   databases:
   - name: db
     engine: PG
     version: "14"
   ```

### Opção 2: Droplet + PostgreSQL

```bash
# Criar Droplet (Ubuntu 22.04, 2GB RAM mínimo)
# SSH into droplet
ssh root@seu-ip

# Setup
apt update && apt upgrade -y
apt install -y python3.11 python3-pip postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE USER painel WITH PASSWORD 'senha123';
CREATE DATABASE painel_juridico OWNER painel;
\q

# Setup app (mesmo que EC2 acima)
git clone https://github.com/seu-usuario/painel-juridico-v2.git
# ... continuar com instalação
```

---

## Segurança

### Checklist de Segurança em Produção

- [ ] `SECRET_KEY` aleatório e seguro (32+ caracteres)
- [ ] `DEBUG=false` em produção
- [ ] HTTPS/SSL configurado
- [ ] CORS apenas com domínios permitidos
- [ ] Rate limiting implementado
- [ ] Firewall configurado (apenas ports 80, 443)
- [ ] Backups automáticos do banco
- [ ] Logs centralizados
- [ ] Monitoramento de segurança ativado
- [ ] Secrets em variáveis de ambiente (não em código)

### CORS em Produção

```python
# main.py
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### Rate Limiting

```bash
pip install slowapi

# Use no main.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/auth/login")
@limiter.limit("5/minute")
async def login(credentials: UserLogin):
    ...
```

---

## Monitoramento

### Logging Estruturado

```python
import logging
import json

# main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup():
    logger.info("🚀 API iniciada", extra={"version": "2.0.0"})
```

### Health Checks

```bash
# Verficar saúde da API
curl http://localhost:8000/health

# Resposta esperada:
{
  "status": "healthy",
  "database": "connected"
}
```

### Monitoramento com Sentry

```bash
pip install sentry-sdk

# main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()]
)
```

### Prometheus Metrics

```bash
pip install prometheus-client

# main.py (adicionar ao startup)
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('painel_requests_total', 'Total Requests')
REQUEST_LATENCY = Histogram('painel_request_latency_seconds', 'Request Latency')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return generate_latest()
```

---

## Troubleshooting Deployment

### Erro: "Connection refused" no banco

```bash
# Verificar conexão
psql -h seu-host -U user -d painel_juridico

# Verificar security groups (AWS)
# Ports 5432 (PostgreSQL) deve estar aberto para EC2
```

### Erro: "Secret Key too short"

```bash
# Gerar chave segura
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Erro: "Module not found"

```bash
# Verificar virtual environment está ativo
which python
# Deve apontar para venv/bin/python

# Reinstalar dependências
pip install -r requirements.txt
```

### Alta latência

```bash
# Aumentar workers gunicorn
gunicorn main:app --workers 8 --worker-class uvicorn.workers.UvicornWorker

# Aumentar pool connections PostgreSQL
# .env: CONNECTION_POOL_SIZE=20
```

---

## Checklist Final de Deploy

- [ ] Banco de dados configurado e acessível
- [ ] Migrations aplicadas (`alembic upgrade head`)
- [ ] Variáveis de ambiente definidas
- [ ] HTTPS/SSL configurado
- [ ] Testes passando (`pytest`)
- [ ] Health check respondendo
- [ ] Logs sendo gerados
- [ ] Backups automáticos configurados
- [ ] Monitoramento ativo
- [ ] Documentação atualizada

---

## Suporte

- Documentação API: `/docs`
- Issues: GitHub Issues
- Email: suporte@painel-juridico.com

**Versão**: 2.0.0
**Data**: 2026-05-19
