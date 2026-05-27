# Backend — SaaS Jurídico Trabalhista

API multi-tenant (FastAPI + SQLAlchemy) com autenticação JWT e RBAC para quatro
papéis: **admin**, **advogado**, **cliente**, **financeiro**. É a base executável
do SaaS descrito em `../ESPECIFICACAO_SAAS.md`. Independente da app desktop legada
na raiz do repositório.

## Instalação

```bash
pip install -r backend/requirements.txt
```

## Executar

```bash
export SECRET_KEY="um-segredo-forte"            # ver backend/.env.example
uvicorn backend.main:app --reload               # http://localhost:8000
```

Documentação interativa (OpenAPI/Swagger): `http://localhost:8000/docs`.
O banco (SQLite por padrão) é criado automaticamente no startup. Para Postgres,
defina `DATABASE_URL`.

## Testes

```bash
pytest backend/tests -v
```

Os testes usam SQLite em memória e cobrem autenticação, RBAC e isolamento entre
tenants. Nenhuma chamada externa de IA é feita.

## Fluxo de uso (cURL)

```bash
# 1. registrar escritório + admin
curl -X POST localhost:8000/api/v1/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"tenant_nome":"Meu Escritório","nome":"Ana","email":"ana@x.com","senha":"senha12345"}'

# 2. login (form urlencoded; username = e-mail)
curl -X POST localhost:8000/api/v1/auth/login \
  -d 'username=ana@x.com&password=senha12345'
# -> {"access_token":"...","refresh_token":"...","token_type":"bearer"}

# 3. usar o access_token
curl localhost:8000/api/v1/clientes -H 'Authorization: Bearer <ACCESS_TOKEN>'
```

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `config.py` | Configuração via variáveis de ambiente |
| `database.py` | Engine/sessão SQLAlchemy (SQLite/Postgres) |
| `models.py` | Modelos ORM multi-tenant (`tenant_id` em tudo) |
| `schemas.py` | Schemas Pydantic (validação) |
| `security.py` | Hash bcrypt + JWT HS256 |
| `deps.py` | `get_current_user`, `require_roles`, auditoria |
| `routers/auth.py` | register, login, refresh, me, users, reset de senha |
| `routers/clientes.py` | CRUD de clientes |
| `routers/processos.py` | CRUD de processos + andamentos + audiências |
| `routers/tarefas.py` | CRUD de tarefas |
| `routers/financeiro.py` | Honorários + relatório (perfil financeiro) |
| `routers/ia.py` | Geração de petição (OpenAI ou template local) |

## Matriz de permissões (RBAC)

| Recurso | admin | advogado | financeiro | cliente |
|---|---|---|---|---|
| Clientes (escrita) | ✔ | ✔ | — | — |
| Clientes/Processos (leitura) | ✔ | ✔ | ✔ | ✔ |
| Processos/Andamentos/Audiências (escrita) | ✔ | ✔ | — | — |
| Tarefas (escrita) | ✔ | ✔ | — | — |
| Honorários (escrita) | ✔ | — | ✔ | — |
| Financeiro (leitura) | ✔ | ✔ | ✔ | — |
| IA / petições | ✔ | ✔ | — | — |
| Criar usuários | ✔ | — | — | — |
| Excluir cliente/processo | ✔ | — | — | — |

## Migrações (Alembic)

O schema é versionado com Alembic (`alembic.ini` na raiz, scripts em
`backend/migrations/`). A URL vem de `DATABASE_URL` (lida em `migrations/env.py`).

```bash
alembic upgrade head                          # aplica todas as migrações
alembic revision --autogenerate -m "mudança"  # gera nova migração ao alterar models.py
```

Em produção defina `AUTO_CREATE_TABLES=0` (o schema passa a ser responsabilidade
do Alembic). Em dev/SQLite, `AUTO_CREATE_TABLES=1` (padrão) cria as tabelas no
startup, sem precisar rodar migração.

## Deploy

**Recomendado — Fly.io + SQLite em volume (mais barato).** Ver `fly.toml` na raiz.

```bash
fly launch --no-deploy                       # ou ajuste "app" no fly.toml
fly volumes create saas_data --size 1 --region gru
fly secrets set SECRET_KEY=$(openssl rand -hex 32)
fly deploy
```

1 container pequeno com SQLite num volume persistente (`/data/app.db`), sem banco
gerenciado, **escalando a zero** quando ocioso. SQLite em WAL + `busy_timeout`
(`database.py`) para concorrência; `WEB_CONCURRENCY=1`.

**Alternativa — Render** (`render.yaml`): web service free + Postgres free. Mais
caro: disco free é efêmero (exige Postgres) e o Postgres free expira em 90 dias
(~US$7/mês depois).

Os dois aplicam `alembic upgrade head` no start. Imagem portátil:
`docker build -f backend/Dockerfile -t saas-juridico .` (a partir da raiz).

Ao crescer, trocar SQLite → Postgres é só mudar `DATABASE_URL` (sem mudar código)
e subir `WEB_CONCURRENCY`.

## Segurança implementada

- Hash de senha (bcrypt) e JWT com `exp` + algoritmo explícito (sem `alg:none`).
- Escopo de tenant derivado do token (nunca do payload do cliente).
- ORM parametrizado (anti-SQL injection).
- Trilha de auditoria (`AuditLog`).
- **Rate limiting** em `/auth/login` e `/auth/password-reset/request` (em memória,
  janela fixa; configurável por `LOGIN_RATE_MAX`/`LOGIN_RATE_WINDOW_SEC`).
- Cabeçalhos de segurança (`X-Frame-Options`, `X-Content-Type-Options`,
  `Referrer-Policy`, CSP) e CORS configurável (`CORS_ORIGINS`).

## Próximos passos (ver `ESPECIFICACAO_SAAS.md`)

Revogação de refresh token, rate limit distribuído (Redis) para múltiplos workers,
envio de e-mail no reset (hoje o token volta na resposta p/ dev), billing/assinatura
(Stripe), conformidade LGPD, e frontend web.
