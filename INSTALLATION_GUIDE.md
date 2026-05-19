# Guia de Instalação - Painel Jurídico v2

**Versão**: 1.0  
**Data**: 2026-05-19  
**Status**: Production Ready  

---

## 📋 Sumário

1. Pré-requisitos
2. Instalação do Ambiente
3. Configuração do Projeto
4. Verificação de Instalação
5. Execução da Aplicação
6. Troubleshooting
7. Estrutura de Diretórios

---

## 🔧 Pré-requisitos

### Requisitos do Sistema

- **SO**: Windows 10/11, macOS 10.14+, ou Linux Ubuntu 20.04+
- **RAM**: Mínimo 4GB (recomendado 8GB)
- **Espaço em Disco**: 500MB para instalação completa
- **Internet**: Necessário para download de dependências

### Software Obrigatório

- **Python**: 3.9 ou superior (testado com 3.14.5)
- **pip**: Gerenciador de pacotes Python
- **git**: Controle de versão (opcional, para clonar repo)

### Verificação de Pré-requisitos

```bash
# Verificar Python
python --version
# Esperado: Python 3.9+

# Verificar pip
pip --version
# Esperado: pip xx.x em /path/to/python

# Verificar git (opcional)
git --version
# Esperado: git version 2.x+
```

---

## 💻 Instalação do Ambiente

### Opção 1: Windows (PowerShell)

#### Passo 1: Criar Virtual Environment

```powershell
# Navegar para o diretório do projeto
cd "C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2"

# Criar venv
python -m venv venv

# Ativar venv
.\venv\Scripts\Activate.ps1
```

**Esperado**:
```
(venv) C:\Users\...\painel_juridico_v2>
```

#### Passo 2: Instalar Dependências

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Instalar requirements
pip install -r requirements.txt
```

**Dependências Principais**:
- customtkinter (UI)
- requests (HTTP)
- reportlab (PDF)
- python-dotenv (Config)

#### Passo 3: Inicializar Banco de Dados

```powershell
python -c "from core.database import init_db; init_db(); print('✓ Banco inicializado')"
```

---

### Opção 2: macOS (Bash/Zsh)

```bash
# Navegar para o projeto
cd ~/Downloads/painel_juridico_v2_final/painel_juridico_v2

# Criar venv
python3 -m venv venv

# Ativar venv
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Inicializar BD
python -c "from core.database import init_db; init_db()"
```

---

### Opção 3: Linux Ubuntu

```bash
# Instalar dependências do sistema
sudo apt-get update
sudo apt-get install python3-dev python3-tk python3-venv

# Navegar e criar venv
cd ~/painel_juridico_v2
python3 -m venv venv
source venv/bin/activate

# Instalar requirements
pip install --upgrade pip
pip install -r requirements.txt

# Inicializar
python -c "from core.database import init_db; init_db()"
```

---

## 🔍 Verificação de Instalação

### Script de Validação

```bash
# Ativar venv (se não estiver)
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

# Executar validação
python validate_deps.py
```

**Saída Esperada**:

```
============================================================
VALIDAÇÃO DE DEPENDÊNCIAS - PAINEL JURÍDICO v2
============================================================

✓ Python: 3.14.5

=== DEPENDÊNCIAS PRINCIPAIS ===

✓ customtkinter   UI Framework         (1.6.x)
✓ requests        HTTP Client          (2.34.2)
✓ sqlite3         Database             (versão 3.50.4)

=== MÓDULOS DO PROJETO ===

✓ core.database                  Database             ✓
✓ modules.api_bridge             API Bridge           ✓
✓ modules.calculadora.calc       Calculadora          ✓
✓ modules.analytics.engine       Analytics            ✓
✓ modules.ia.gerador             Gerador de Peças     ✓
✓ modules.exports.pdf            PDF Export           ✓
```

---

## 🚀 Execução da Aplicação

### Iniciar Painel Jurídico v2

```bash
# Com venv ativado
python main.py
```

**Interface Esperada**:
- Janela com tamanho 1400x850 pixels
- Tema escuro (dark mode)
- Menu lateral com 13 telas
- Dashboard visível por padrão

### Navegar para Integração Legal AI

1. Clique em **CONFIGURAÇÕES** (sidebar direita)
2. Selecione **Integração Legal AI**
3. Veja o status de conexão (será "Desconectado" se backend não está rodando)

---

## 🧪 Testes de Integração

### Teste Rápido

```bash
python test_api_bridge.py
```

**Esperado**: ✓ Conexão testada, métodos listados

### Teste Completo

```bash
python test_integration_full.py
```

**Esperado**: 5/6 testes passarem (83.3%)

---

## 📁 Estrutura de Diretórios

```
painel_juridico_v2/
├── venv/                          # Virtual environment
│   ├── Scripts/ (Windows)
│   ├── bin/ (macOS/Linux)
│   └── lib/
│
├── core/                          # Núcleo da aplicação
│   ├── database.py                # SQLite setup
│   ├── services.py                # Business logic
│   └── __init__.py
│
├── modules/                       # Funcionalidades modulares
│   ├── api_bridge/                # ✨ NOVO - Integração Legal AI
│   │   ├── __init__.py
│   │   └── client.py              # LegalAIClient
│   ├── calculadora/
│   │   ├── calc.py
│   │   └── __init__.py
│   ├── analytics/
│   │   ├── engine.py
│   │   └── __init__.py
│   ├── ia/
│   │   ├── gerador.py
│   │   └── __init__.py
│   ├── exports/
│   │   ├── pdf.py
│   │   ├── csv_export.py
│   │   └── __init__.py
│   └── __init__.py
│
├── main.py                        # Aplicação principal (1533 linhas)
├── seed.py                        # Dados iniciais
├── requirements.txt               # Dependências
│
├── .git/                          # Repositório Git
├── .gitignore                     # Arquivos ignorados
│
└── Documentação/
    ├── EXECUTIVE_SUMMARY.md       # Visão geral
    ├── INSTALLATION_GUIDE.md      # Este arquivo
    ├── INTEGRATION_GUIDE.md       # Como usar API
    ├── PHASE1_COMPLETE.md         # Fase 1 finalizada
    ├── TECHNICAL_SUMMARY.md       # Detalhes técnicos
    ├── PHASE2_ROADMAP.md          # Próximos passos
    ├── EXECUTION_REPORT.md        # Resultados de testes
    └── FILES_MANIFEST.md          # Listagem de mudanças
```

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

Criar arquivo `.env` (opcional):

```env
# Legal AI Backend
LEGAL_AI_URL=http://localhost:8000
LEGAL_AI_TIMEOUT=30

# OpenAI (para geração de peças)
OPENAI_API_KEY=sk-xxx

# Database
DATABASE_PATH=./core/database.db

# Logging
LOG_LEVEL=INFO
```

Carregar em `main.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()
LEGAL_AI_URL = os.getenv('LEGAL_AI_URL', 'http://localhost:8000')
```

### Configuração de Banco de Dados

```python
# Em core/database.py
DB_PATH = os.getenv('DATABASE_PATH', './core/database.db')
```

---

## 🐛 Troubleshooting

### Problema 1: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'customtkinter'
```

**Solução**:
```bash
# Verificar venv está ativado
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

# Reinstalar
pip install customtkinter
```

### Problema 2: Conexão Recusada (Legal AI)

```
ConnectionRefusedError: [Errno 111] Connection refused
```

**Solução**:
```bash
# Legal AI não está rodando. Iniciar em outro terminal:
cd C:\Users\Notebook\legal-ai\legal-app
python main.py

# Ou mudar URL em CONFIGURAÇÕES → Integração Legal AI
```

### Problema 3: Erro de Banco de Dados

```
sqlite3.OperationalError: database is locked
```

**Solução**:
```bash
# Fechar outras instâncias da aplicação
# Deletar lock file:
rm core/database.db-wal
rm core/database.db-shm

# Reiniciar:
python main.py
```

### Problema 4: Permissões no Windows

```
PermissionError: [Errno 13] Permission denied
```

**Solução**:
```powershell
# Executar PowerShell como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Depois ativar venv normalmente
.\venv\Scripts\Activate.ps1
```

---

## 🧹 Limpeza e Reinstalação

### Limpar Cache Python

```bash
# Windows
py.exe -B main.py

# macOS/Linux
python -B main.py

# Ou deletar __pycache__
find . -type d -name __pycache__ -exec rm -rf {} +
```

### Reinstalar Dependências

```bash
# Backup requirements atual
pip freeze > requirements_backup.txt

# Reinstalar limpo
pip install --force-reinstall -r requirements.txt
```

### Resetar Banco de Dados

```bash
# Deletar database.db
rm core/database.db

# Reinicializar
python -c "from core.database import init_db; init_db()"

# Recarregar seed
python seed.py
```

---

## 📊 Verificação de Sistema

### Script de Diagnóstico

```bash
python -c "
import sys
import platform

print('=== INFORMAÇÕES DO SISTEMA ===')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Arquitetura: {platform.machine()}')
print(f'Processadores: {sys.platform}')
"
```

---

## 🔐 Segurança na Instalação

### Proteção de Credenciais

1. **Nunca fazer commit de .env**:
   ```bash
   # Já incluso no .gitignore
   echo ".env" >> .gitignore
   ```

2. **Não compartilhar chaves API**:
   ```bash
   # Revisar antes de push
   git diff --cached
   ```

3. **Usar virtual environment**:
   ```bash
   # Isolado de pacotes do sistema
   python -m venv venv
   ```

---

## 📚 Próximos Passos Após Instalação

1. **Ler documentação**:
   - EXECUTIVE_SUMMARY.md (visão geral)
   - INTEGRATION_GUIDE.md (como usar)

2. **Testar aplicação**:
   ```bash
   python test_integration_full.py
   ```

3. **Explorar interface**:
   - Dashboard
   - Processos
   - Clientes
   - Integração Legal AI

4. **Configurar (opcional)**:
   - Adicionar OpenAI API key
   - Conectar Legal AI Backend
   - Importar dados

---

## 🤝 Suporte

### Documentação Disponível

| Documento | Conteúdo |
|-----------|----------|
| EXECUTIVE_SUMMARY.md | Visão geral do projeto |
| INTEGRATION_GUIDE.md | Como usar a integração |
| TECHNICAL_SUMMARY.md | Detalhes técnicos |
| PHASE2_ROADMAP.md | Próximas melhorias |
| EXECUTION_REPORT.md | Resultados de testes |

### Comandos Úteis

```bash
# Iniciar aplicação
python main.py

# Rodar testes
python test_integration_full.py
python test_api_bridge.py

# Validar dependências
python validate_deps.py

# Atualizar banco
python seed.py

# Ativar venv (Windows)
.\venv\Scripts\Activate.ps1

# Ativar venv (macOS/Linux)
source venv/bin/activate

# Desativar venv
deactivate
```

---

## ✅ Checklist de Instalação

- [ ] Python 3.9+ instalado
- [ ] pip funcionando
- [ ] Virtual environment criado
- [ ] Dependências instaladas
- [ ] Banco de dados inicializado
- [ ] Testes passando (5/6)
- [ ] Aplicação inicia sem erros
- [ ] Integração Legal AI visível

**Se todos os itens estão marcados**: ✅ Instalação completa!

---

**Desenvolvido por**: Oz Agent  
**Versão**: 1.0  
**Última Atualização**: 2026-05-19  
**Status**: Production Ready

---

## 🎯 Próxima Etapa

Leia **PHASE2_ROADMAP.md** para começar a Fase 2 (Melhorias de Funcionalidade).
