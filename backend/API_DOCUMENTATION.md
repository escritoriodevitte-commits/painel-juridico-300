# 📚 Painel Jurídico v2 - Documentação da API FastAPI

API SaaS completa para gestão jurídica com suporte a autenticação JWT, multi-tenant, geração de peças via IA e integração com Mercado Pago.

## 🚀 Início Rápido

### Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env
cp .env.example .env

# Inicializar banco de dados
alembic upgrade head

# Rodar servidor
python main.py
```

Servidor rodará em `http://localhost:8000`
Documentação interativa: `http://localhost:8000/docs`

## 📋 Endpoints da API

### ✅ Autenticação (`/api/auth`)

#### Registrar novo usuário e tenant
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "admin@empresa.com",
  "full_name": "João Silva",
  "password": "SenhaForte123!",
  "tenant_name": "Empresa XYZ"
}

Response 200:
{
  "id": "uuid",
  "email": "admin@empresa.com",
  "full_name": "João Silva",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-05-19T03:30:00"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "admin@empresa.com",
  "password": "SenhaForte123!"
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Renovar access token
```http
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}

Response 200:
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 👥 Gerenciamento de Usuários (`/api/users`)

**Autenticação obrigatória em todos os endpoints**

#### Obter dados do usuário atual
```http
GET /api/users/me
Authorization: Bearer {access_token}

Response 200:
{
  "id": "uuid",
  "email": "admin@empresa.com",
  "full_name": "João Silva",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-05-19T03:30:00"
}
```

#### Listar todos os usuários do tenant (apenas ADMIN)
```http
GET /api/users?skip=0&limit=100
Authorization: Bearer {access_token}

Response 200:
[
  {
    "id": "uuid1",
    "email": "user1@empresa.com",
    "full_name": "Maria Santos",
    "role": "user",
    "is_active": true,
    "created_at": "2026-05-19T03:35:00"
  },
  {
    "id": "uuid2",
    "email": "user2@empresa.com",
    "full_name": "Pedro Costa",
    "role": "user",
    "is_active": true,
    "created_at": "2026-05-19T03:36:00"
  }
]
```

#### Criar novo usuário (apenas ADMIN)
```http
POST /api/users
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "email": "novousuario@empresa.com",
  "full_name": "Novo Usuário",
  "password": "SenhaForte123!"
}

Response 201:
{
  "id": "uuid",
  "email": "novousuario@empresa.com",
  "full_name": "Novo Usuário",
  "role": "user",
  "is_active": true,
  "created_at": "2026-05-19T03:40:00"
}
```

#### Atualizar usuário (apenas ADMIN)
```http
PUT /api/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "full_name": "Nome Atualizado",
  "role": "user",
  "is_active": true
}

Response 200:
{
  "id": "uuid",
  "email": "usuario@empresa.com",
  "full_name": "Nome Atualizado",
  "role": "user",
  "is_active": true,
  "created_at": "2026-05-19T03:40:00"
}
```

#### Deletar usuário (apenas ADMIN)
```http
DELETE /api/users/{user_id}
Authorization: Bearer {access_token}

Response 200:
{
  "message": "Usuário usuario@empresa.com deletado com sucesso",
  "user_id": "uuid"
}
```

#### Alterar senha
```http
POST /api/users/me/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "SenhaAntiga123!",
  "new_password": "SenhaNova456!"
}

Response 200:
{
  "message": "Senha alterada com sucesso"
}
```

---

### 🤖 Geração de Peças Jurídicas via IA (`/api/ia`)

**Autenticação obrigatória em todos os endpoints**

#### Verificar status da IA
```http
GET /api/ia/status
Authorization: Bearer {access_token}

Response 200:
{
  "ia_status": {
    "ia_disponivel": false,
    "modelo": "gpt-4.1",
    "api_key_configurada": false,
    "tipos_peca_disponiveis": 10
  },
  "tenant": "Empresa XYZ",
  "mensagem": "Configure OPENAI_API_KEY para usar geração via IA. Sem ela, usa templates locais."
}
```

#### Listar tipos de peça disponíveis
```http
GET /api/ia/tipos-peca
Authorization: Bearer {access_token}

Response 200:
{
  "tipos_peca": {
    "reclamatoria_trabalhista": "RECLAMATÓRIA TRABALHISTA",
    "contestacao": "CONTESTAÇÃO TRABALHISTA",
    "alegacoes_finais": "ALEGAÇÕES FINAIS",
    "rol_perguntas": "ROL DE PERGUNTAS PARA TESTEMUNHAS",
    "recurso_ordinario": "RECURSO ORDINÁRIO",
    "impugnacao": "IMPUGNAÇÃO AOS CÁLCULOS DE LIQUIDAÇÃO",
    "manifestacao": "MANIFESTAÇÃO",
    "pedido_habilitacao": "PEDIDO DE HABILITAÇÃO",
    "procuracao": "PROCURAÇÃO AD JUDICIA",
    "replica": "RÉPLICA À CONTESTAÇÃO"
  },
  "total": 10,
  "descricao": "Tipos de peças jurídicas que podem ser geradas"
}
```

#### Gerar peça jurídica
```http
POST /api/ia/gerar-peca
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "tipo_peca": "reclamatoria_trabalhista",
  "dados_processo": {
    "numero_processo": "0001234-56.2026.5.01.0000",
    "vara": "1ª Vara do Trabalho",
    "reclamante": "João da Silva",
    "reclamada": "Empresa XYZ Ltda",
    "valor_pedido": 50000.00,
    "tese_inicial": "Demissão sem justa causa",
    "tese_defesa": null,
    "status": "EM TRAMITAÇÃO"
  },
  "dados_juiz": {
    "nome": "Juiz José Santos",
    "tendencia_conciliatoria": "Alta"
  },
  "jurisprudencia": [
    {
      "tipo": "sumula",
      "titulo": "Súmula 21 do TST",
      "tema": "Adicional de insalubridade",
      "fonte": "TST",
      "trecho": "O adicional de insalubridade integra o cálculo da...  "
    }
  ],
  "instrucoes_adicionais": "Foque em violação de direitos fundamentais"
}

Response 200:
{
  "sucesso": true,
  "conteudo": "EXCELENTÍSSIMO(A) SENHOR(A) JUIZ(A) DO TRABALHO...",
  "tipo_peca": "reclamatoria_trabalhista",
  "tipo_nome": "RECLAMATÓRIA TRABALHISTA",
  "gerado_por_ia": false,
  "aviso": "⚠️ OpenAI API não configurada. Usando template local como fallback.",
  "timestamp": "2026-05-19T03:45:00.000000"
}
```

#### Configurar chave da OpenAI (apenas ADMIN)
```http
POST /api/ia/configurar-openai
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "api_key": "sk-proj-..."
}

Response 200:
{
  "mensagem": "Chave da OpenAI configurada com sucesso",
  "ia_disponivel": true,
  "modelo": "gpt-4.1",
  "aviso": "⚠️ Guarde a chave com segurança. Esta chave tem acesso a sua conta OpenAI."
}
```

---

## 🔐 Autenticação

### Headers de Requisição

Todos os endpoints protegidos (exceto `/api/auth`) requerem:

```
Authorization: Bearer {access_token}
```

### Roles de Usuário

- **ADMIN**: Acesso total ao tenant (gerenciar usuários, configurar IA)
- **USER**: Acesso limitado (visualizar dados próprios, gerar peças)

---

## 🏗️ Arquitetura Multi-tenant

- Cada tenant é uma organização isolada
- Usuários pertencem a um tenant específico
- Dados são isolados por tenant (SQL)
- JWT token contém tenant_id para validação

### Fluxo de Registro

1. Novo usuário registra com `/api/auth/register`
2. Sistema cria automaticamente um novo Tenant
3. Primeiro usuário é criado como ADMIN
4. Próximos usuários podem ser criados pelo ADMIN

---

## 🗄️ Banco de Dados

### Modelos Principais

- **Tenant**: Organização
- **User**: Usuário (vinculado a Tenant)
- **Subscription**: Plano pago (vinculado a Tenant)
- **Payment**: Pagamento (vinculado a Tenant e Subscription)
- **AuditLog**: Log de auditoria

### Migrations

```bash
# Ver status
alembic current

# Criar nova migration
alembic revision --autogenerate -m "Descrição"

# Aplicar migrations
alembic upgrade head

# Reverter
alembic downgrade -1
```

---

## 📝 Variáveis de Ambiente

```env
# Banco de dados
DATABASE_URL=sqlite:///./painel_juridico.db

# Segurança JWT
SECRET_KEY=sua-chave-secreta-minimo-32-caracteres
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (opcional para IA)
OPENAI_API_KEY=sk-proj-...

# Mercado Pago (para pagamentos)
MERCADO_PAGO_TOKEN=...
MERCADO_PAGO_PUBLIC_KEY=...

# Frontend
FRONTEND_URL=http://localhost:3000

# Debug
DEBUG=false
```

---

## 🧪 Testes

```bash
# Rodar testes
pytest

# Com cobertura
pytest --cov=.

# Teste específico
pytest tests/test_auth.py -v
```

---

## 🚢 Deployment

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables em Produção

Sempre use variáveis de ambiente seguras:
- `SECRET_KEY`: Chave aleatória forte
- `DATABASE_URL`: URL do PostgreSQL (não SQLite)
- `OPENAI_API_KEY`: Chave da OpenAI
- `MERCADO_PAGO_TOKEN`: Token do Mercado Pago

---

## 🔄 Fluxo de Uso Típico

1. **Registrar** (novo usuario + tenant)
   ```bash
   POST /api/auth/register
   ```

2. **Login**
   ```bash
   POST /api/auth/login
   → Recebe access_token e refresh_token
   ```

3. **Criar usuários no tenant** (como ADMIN)
   ```bash
   POST /api/users
   ```

4. **Gerar peça jurídica**
   ```bash
   POST /api/ia/gerar-peca
   → Retorna peça com templates ou gerado por IA
   ```

5. **Renovar token** (quando expirar)
   ```bash
   POST /api/auth/refresh
   ```

---

## 🆘 Troubleshooting

### "Token inválido ou expirado"
- Verifique se está usando o header correto: `Authorization: Bearer {token}`
- Renove o token com `/api/auth/refresh`
- Verifique se `SECRET_KEY` é a mesma

### "OpenAI API não disponível"
- Configure `OPENAI_API_KEY` no `.env`
- O sistema usará templates locais como fallback
- Endpoint `/api/ia/configurar-openai` permite configurar em runtime

### Erro de banco de dados
```bash
# Resetar banco (CUIDADO - deleta tudo)
rm painel_juridico.db
alembic upgrade head
```

---

## 📊 Status da Implementação

✅ **Completo (4/7 tarefas)**:
1. ✅ Estrutura base FastAPI
2. ✅ Banco de dados + Migrations
3. ✅ Autenticação JWT
4. ✅ Endpoints CRUD + IA

⏳ **Próximos passos**:
5. ⏳ Integração Mercado Pago
6. ⏳ Sistema Multi-tenant (base já implementada)
7. ⏳ Testes unitários e E2E

---

## 📞 Suporte

Para questões sobre a API:
1. Verifique a documentação interativa em `/docs`
2. Consulte o README.md principal
3. Verifique os arquivos de teste em `tests/`

---

**Versão**: 2.0.0
**Última atualização**: 2026-05-19
**Autor**: Oz AI Agent
