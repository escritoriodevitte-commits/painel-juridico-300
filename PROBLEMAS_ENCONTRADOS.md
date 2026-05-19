# 🔴 Problemas Encontrados - Testes Locais

## Data: 2026-05-19
## Status: IDENTIFICADOS E PRONTOS PARA CORREÇÃO

---

## 📋 Resumo dos Problemas

| # | Problema | Severidade | Arquivo | Linha |
|---|----------|-----------|---------|-------|
| 1 | bcrypt incompatibilidade em testes | 🔴 CRÍTICO | `tests/conftest.py` | 79, 97 |
| 2 | Execução SQL inválida no health check | 🔴 CRÍTICO | `main.py` | 88 |
| 3 | Falta de dependência: `dependencies.py` | 🔴 CRÍTICO | `api/routes/*.py` | imports |
| 4 | `database/__init__.py` não importa modelos | 🟠 ALTO | `database/__init__.py` | - |
| 5 | Endpoint `/me` duplicado em users.py | 🟠 ALTO | `api/routes/users.py` | 51, 227 |
| 6 | Router GET `/` conflita com HEAD | 🟠 ALTO | `api/routes/users.py` | 22 |

---

## 🔴 PROBLEMA 1: bcrypt Incompatibilidade em Testes

### Descrição
Erro ao executar `pytest`: `ValueError: password cannot be longer than 72 bytes`

### Root Cause
- A senha `"TestPass123"` (12 caracteres) é válida
- Mas `passlib[bcrypt]` com versões incompatíveis causa erro de inicialização
- Erro real: `AttributeError: module 'bcrypt' has no attribute '__about__'`

### Arquivos Afetados
- `tests/conftest.py` - linhas 79, 97 (hash_password)

### Solução
Usar pré-hash ou mock do bcrypt:

```python
# Opção 1: Usar hash pré-computado para testes
PRESET_PASSWORD_HASH = "$2b$12$abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrs"

# Opção 2: Criar função de hash de teste
def hash_password_test(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

# Opção 3: Mock bcrypt (recomendado)
from unittest.mock import patch
```

---

## 🔴 PROBLEMA 2: Execução SQL Inválida no Health Check

### Descrição
Erro ao chamar `GET /health`:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.ProgrammingError) not a name...
```

### Root Cause
```python
# main.py, linha 88 - INCORRETO:
db.execute("SELECT 1")
```

SQLAlchemy 2.x exige `text()` para SQL strings:

```python
# CORRETO:
from sqlalchemy import text
db.execute(text("SELECT 1"))
```

### Arquivos Afetados
- `main.py` - linha 88

---

## 🔴 PROBLEMA 3: Arquivo `dependencies.py` Não Existe

### Descrição
Importações em rotas falam:
```python
from dependencies import get_current_user, get_current_tenant, require_admin
```

Mas arquivo **não existe** no projeto.

### Arquivos Que Precisam
- `api/routes/ia_gerador.py` - linha 12
- `api/routes/users.py` - linha 14
- `api/routes/auth.py` - (não importa, mas deveria)

### Solução
Criar `backend/dependencies.py` com:
```python
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from main import get_db
from database import User, Tenant, UserRole
from auth import decode_access_token
from fastapi import Request

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    # Extrair token do header
    # Decodificar e buscar usuário
    pass

def get_current_tenant(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Tenant:
    # Buscar tenant do usuário
    pass

def require_admin(user: User = Depends(get_current_user)) -> User:
    # Validar role ADMIN
    pass
```

---

## 🟠 PROBLEMA 4: `database/__init__.py` Não Importa Modelos

### Descrição
Em `conftest.py` temos:
```python
from database import Base, Tenant, User, UserRole  # NÃO FUNCIONA
```

Mas `database/__init__.py` está vazio ou não importa.

### Solução
Criar/atualizar `database/__init__.py`:
```python
from database.models import Base, Tenant, User, Subscription, Payment, AuditLog, UserRole

__all__ = ["Base", "Tenant", "User", "Subscription", "Payment", "AuditLog", "UserRole"]
```

---

## 🟠 PROBLEMA 5: Rota `/me` Duplicada

### Descrição
Em `api/routes/users.py`:
- Linha 51: `@router.get("/me", ...)` - obter usuário atual
- Linha 227: `@router.post("/me/change-password", ...)` - alterar senha

O endpoint GET `/users/me` funciona, mas POST `/users/me/change-password` conflita.

### Solução
Mover `change_password` para sua própria rota ou usar Query String:
```python
# CORRETO:
@router.post("/me/change-password")  # Fica bem
# OU:
@router.post("/change-password", ...)  # Se quiser sem /me
```

Não há conflito real, apenas design ruim.

---

## 🟠 PROBLEMA 6: Router GET `/` Conflita com HEAD

### Descrição
`api/routes/users.py` tem:
```python
@router.get("")  # Linha 22
```

Mas `main.py` já tem:
```python
@app.get("/")    # Linha 75
```

Como o router `users` tem prefix `/api/users`, isso fica:
- `GET /api/users/` vs `GET /`

Sem conflito, mas confuso. Deveria ser `GET /api/users`.

---

## ✅ Soluções Recomendadas

### Ordem de Prioridade

1. **IMEDIATO** - Corrigir `main.py` linha 88 (health check)
   ```python
   from sqlalchemy import text
   db.execute(text("SELECT 1"))
   ```

2. **IMEDIATO** - Criar `backend/dependencies.py`
   - Implementar `get_current_user()`
   - Implementar `get_current_tenant()`
   - Implementar `require_admin()`

3. **IMEDIATO** - Atualizar `database/__init__.py`
   - Importar todos modelos e Base
   - Exportar no `__all__`

4. **LOGO** - Corrigir `tests/conftest.py`
   - Usar mock ou pré-hash para bcrypt
   - Ou atualizar `requirements.txt` com versões compatíveis

5. **OPCIONAL** - Melhorar estrutura de rotas
   - Remover GET `/` de users
   - Ou renomear para GET `/api/users` consistentemente

---

## 🧪 Teste Rápido Após Correções

```bash
# 1. Instalar dependências
cd backend
pip install -r requirements.txt

# 2. Rodar testes
pytest tests/test_ia_routes.py -v

# 3. Iniciar servidor
python main.py

# 4. Testar endpoints
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Pass123","full_name":"Test","tenant_name":"Test"}'
```

---

## 📝 Status das Correções

- [ ] main.py - health check
- [ ] Criar dependencies.py
- [ ] Atualizar database/__init__.py
- [ ] Corrigir conftest.py para bcrypt
- [ ] Rodar testes novamente
- [ ] Testar endpoints localmente

---

**Próximo passo**: Aplicar correções em orden de prioridade.
