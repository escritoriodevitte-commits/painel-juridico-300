# Painel Jurídico v2 - Backend FastAPI

Backend API para plataforma SaaS de gestão jurídica com suporte a autenticação, multi-tenant e integração com Mercado Pago.

## Estrutura do Projeto

```
backend/
├── main.py                 # Aplicação FastAPI principal
├── auth.py                 # Autenticação (JWT, password hashing)
├── schemas.py              # Schemas Pydantic para validação
├── requirements.txt        # Dependências do projeto
├── .env.example            # Exemplo de variáveis de ambiente
├── database/
│   ├── __init__.py
│   └── models.py           # Modelos SQLAlchemy (Tenant, User, Subscription, Payment)
├── api/
│   ├── __init__.py
│   └── routes/
│       ├── __init__.py
│       ├── auth.py         # Endpoints de autenticação (login, register, refresh)
│       ├── users.py        # Endpoints de usuários
│       ├── subscriptions.py # Endpoints de assinaturas
│       └── payments.py      # Endpoints de pagamentos
├── migrations/             # Alembic migrations (será criado com alembic init)
└── tests/
    ├── __init__.py
    ├── test_auth.py
    ├── test_users.py
    ├── test_subscriptions.py
    └── test_payments.py
```

## Configuração Rápida

### 1. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 2. Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e preencha os valores:

```bash
cp .env.example .env
```

**Valores necessários:**
- `DATABASE_URL`: URL do PostgreSQL
- `SECRET_KEY`: Chave secreta para JWT (mínimo 32 caracteres)
- `MERCADO_PAGO_TOKEN`: Token do Mercado Pago
- `MERCADO_PAGO_PUBLIC_KEY`: Chave pública do Mercado Pago

### 3. Banco de Dados

#### PostgreSQL Local (Desenvolvimento)

```bash
# Criar banco de dados
createdb painel_juridico

# Ou via psql
psql -c "CREATE DATABASE painel_juridico;"
```

#### Docker (Alternativa)

```bash
docker run --name postgres-painel \
  -e POSTGRES_PASSWORD=senha123 \
  -e POSTGRES_DB=painel_juridico \
  -p 5432:5432 \
  -d postgres:15
```

### 4. Migrations com Alembic

```bash
# Inicializar Alembic (primeira vez)
alembic init migrations

# Criar migration automática
alembic revision --autogenerate -m "Initial migration"

# Aplicar migrations
alembic upgrade head
```

### 5. Executar Aplicação

```bash
# Desenvolvimento (com reload automático)
python main.py

# Ou com uvicorn direto
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

## Documentação da API

A documentação interativa está disponível em:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints Principais

### Autenticação

- `POST /api/auth/register` - Registrar novo usuário/tenant
- `POST /api/auth/login` - Login
- `POST /api/auth/refresh` - Renovar token de acesso
- `POST /api/auth/logout` - Logout

### Usuários

- `GET /api/users/me` - Dados do usuário atual
- `PUT /api/users/me` - Atualizar perfil
- `GET /api/users` - Listar usuários (admin)
- `PUT /api/users/{user_id}` - Atualizar usuário (admin)
- `DELETE /api/users/{user_id}` - Deletar usuário (admin)

### Assinaturas

- `GET /api/subscriptions` - Listar assinaturas do tenant
- `POST /api/subscriptions` - Criar assinatura
- `GET /api/subscriptions/{sub_id}` - Detalhes da assinatura
- `PUT /api/subscriptions/{sub_id}` - Atualizar assinatura
- `DELETE /api/subscriptions/{sub_id}` - Cancelar assinatura

### Pagamentos

- `GET /api/payments` - Listar pagamentos do tenant
- `POST /api/payments` - Criar pagamento
- `GET /api/payments/{payment_id}` - Detalhes do pagamento
- `POST /api/webhooks/mercado-pago` - Webhook do Mercado Pago

## Arquitetura

### Multi-tenant

O sistema usa schema de isolamento por tenant:
- Cada tenant tem seus próprios usuários, assinaturas e pagamentos
- Os dados são isolados no nível do banco de dados
- O tenant_id é extraído do token JWT

### Autenticação

- JWT (JSON Web Tokens) com HS256
- Access tokens com validade de 30 minutos
- Refresh tokens com validade de 7 dias
- Passwords hasheados com bcrypt

### Banco de Dados

- PostgreSQL
- ORM: SQLAlchemy
- Migrations: Alembic

## Testes

```bash
# Rodar todos os testes
pytest

# Com cobertura
pytest --cov=.

# Teste específico
pytest tests/test_auth.py -v
```

## Desenvolvimento

### Debug

Ativar modo debug no `.env`:

```
DEBUG=true
```

Isso ativa SQL logging e reload automático.

### Adicionando novos endpoints

1. Criar arquivo em `api/routes/`
2. Definir schemas em `schemas.py`
3. Importar em `main.py`
4. Incluir router: `app.include_router(router, prefix="/api")`

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### AWS/DigitalOcean

Usar Docker com CI/CD pipeline. Ver documentação principal do projeto.

## Troubleshooting

### Erro de conexão com PostgreSQL

```
Verifique:
1. PostgreSQL está rodando: psql -U postgres
2. DATABASE_URL está correto
3. Credenciais estão corretas
```

### JWT não validando

```
Verifique:
1. SECRET_KEY é a mesma em todas as instâncias
2. Token não expirou
3. Token está no header: Authorization: Bearer <token>
```

### Alembic não encontra models

```bash
# Ensure current directory is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
alembic revision --autogenerate -m "Migration"
```

## Próximas Etapas

- [ ] Implementar endpoints de autenticação
- [ ] Configurar Alembic migrations
- [ ] Adicionar testes unitários
- [ ] Integração Mercado Pago
- [ ] Admin dashboard endpoints
- [ ] Logging estruturado
- [ ] Rate limiting
- [ ] CORS configuration

## Contribuindo

1. Criar branch feature
2. Fazer commits com mensagens claras
3. Rodar testes localmente
4. Criar PR para review

## Licença

Proprietary - Painel Jurídico v2
