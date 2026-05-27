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

## Notas de segurança / próximos passos

Implementado: hash de senha (bcrypt), JWT com `exp` e algoritmo explícito (sem
`alg:none`), escopo de tenant derivado do token, ORM parametrizado (anti-SQLi),
trilha de auditoria (`AuditLog`).

A construir (ver `ESPECIFICACAO_SAAS.md`): rate limiting, revogação de refresh
token, migrações Alembic, envio de e-mail no reset (hoje o token volta na
resposta para facilitar dev), CORS/CSP, e conformidade LGPD.
