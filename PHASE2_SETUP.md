# Fase 2: Preparação para Desenvolvimento

**Status**: Pronto para Iniciar  
**Data**: 2026-05-19  
**Duração Estimada**: 3-4 horas  
**Prioridade**: Alta  

---

## 🎯 Objetivo da Fase 2

Implementar melhorias de funcionalidade e validação de dados para tornar o Painel Jurídico v2 robusto e pronto para produção.

---

## 📋 Itens para Implementar

### 1. Módulo de Validadores (2 horas)

#### 1.1 Criar estrutura

```bash
# No projeto, criar:
mkdir -p modules/validators
touch modules/validators/__init__.py
touch modules/validators/date_validator.py
touch modules/validators/number_validator.py
touch modules/validators/document_validator.py
```

#### 1.2 Validador de Datas

**Arquivo**: `modules/validators/date_validator.py`

```python
from datetime import datetime
from typing import Tuple

class DateValidator:
    """Validador de datas no formato DD/MM/AAAA"""
    
    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, str]:
        """
        Valida uma data no formato DD/MM/AAAA
        
        Returns:
            (True, "") se válida
            (False, "motivo") se inválida
        """
        try:
            if not date_str or len(date_str) != 10:
                return False, "Formato deve ser DD/MM/AAAA"
            
            day, month, year = date_str.split('/')
            date_obj = datetime(int(year), int(month), int(day))
            return True, ""
        except ValueError as e:
            return False, f"Data inválida: {str(e)}"
    
    @staticmethod
    def validate_date_range(start_str: str, end_str: str) -> Tuple[bool, str]:
        """Valida que end_date > start_date"""
        valid_start, err_start = DateValidator.validate_date(start_str)
        if not valid_start:
            return False, f"Data início inválida: {err_start}"
        
        valid_end, err_end = DateValidator.validate_date(end_str)
        if not valid_end:
            return False, f"Data fim inválida: {err_end}"
        
        d1 = datetime.strptime(start_str, "%d/%m/%Y")
        d2 = datetime.strptime(end_str, "%d/%m/%Y")
        
        if d2 <= d1:
            return False, "Data fim deve ser posterior à data início"
        
        return True, ""
```

#### 1.3 Validador de Moeda

**Arquivo**: `modules/validators/number_validator.py`

```python
class NumberValidator:
    """Validador de valores numéricos"""
    
    @staticmethod
    def validate_currency(value: str) -> Tuple[bool, str]:
        """Valida formato de moeda brasileira (R$)"""
        try:
            # Remove R$ e espaços
            clean = value.replace("R$", "").strip()
            # Converte ponto e vírgula
            clean = clean.replace(".", "").replace(",", ".")
            float_value = float(clean)
            
            if float_value < 0:
                return False, "Valor não pode ser negativo"
            
            return True, ""
        except ValueError:
            return False, "Formato de moeda inválido"
    
    @staticmethod
    def validate_percentage(value: float) -> Tuple[bool, str]:
        """Valida percentual (0-100)"""
        try:
            if not (0 <= float(value) <= 100):
                return False, "Percentual deve estar entre 0 e 100"
            return True, ""
        except (ValueError, TypeError):
            return False, "Valor percentual inválido"
```

#### 1.4 Validador de Documentos

**Arquivo**: `modules/validators/document_validator.py`

```python
class DocumentValidator:
    """Validador de documentos brasileiros"""
    
    @staticmethod
    def validate_cpf(cpf: str) -> Tuple[bool, str]:
        """Valida CPF (123.456.789-09)"""
        cpf_clean = cpf.replace(".", "").replace("-", "")
        
        if len(cpf_clean) != 11 or not cpf_clean.isdigit():
            return False, "CPF deve ter 11 dígitos"
        
        # Validação simples de checksum
        if cpf_clean == cpf_clean[0] * 11:
            return False, "CPF inválido"
        
        return True, ""
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> Tuple[bool, str]:
        """Valida CNPJ (12.345.678/0001-90)"""
        cnpj_clean = cnpj.replace(".", "").replace("/", "").replace("-", "")
        
        if len(cnpj_clean) != 14 or not cnpj_clean.isdigit():
            return False, "CNPJ deve ter 14 dígitos"
        
        if cnpj_clean == cnpj_clean[0] * 14:
            return False, "CNPJ inválido"
        
        return True, ""
```

#### 1.5 Integração nos Formulários

**Em `main.py`**, modificar `_build_processo_form()`:

```python
from modules.validators.date_validator import DateValidator
from modules.validators.number_validator import NumberValidator

# Adicionar validação ao salvar:
def save():
    # ... código existente ...
    
    # Validar datas
    data_dist = fields['data_distribuicao'].get()
    valid, msg = DateValidator.validate_date(data_dist)
    if not valid:
        messagebox.showerror("Erro", f"Data inválida: {msg}")
        return
    
    # Validar valor
    valor = fields['valor_pedido'].get()
    valid, msg = NumberValidator.validate_currency(valor)
    if not valid:
        messagebox.showerror("Erro", f"Valor inválido: {msg}")
        return
    
    # ... rest of save logic ...
```

---

### 2. Sincronização Bidirecional (1.5 horas)

#### 2.1 Criar módulo de sincronização

```bash
mkdir -p modules/sync
touch modules/sync/__init__.py
touch modules/sync/process_sync.py
```

#### 2.2 Implementar ProcessSync

**Arquivo**: `modules/sync/process_sync.py`

```python
from modules.api_bridge import LegalAIClient
from core.database import get_lawsuit_by_id, create_lawsuit
import json

class ProcessSync:
    """Sincronização de processos com Legal AI"""
    
    def __init__(self, client: LegalAIClient):
        self.client = client
    
    def sync_local_to_remote(self, lawsuit_id: int) -> bool:
        """Envia processo local para Legal AI"""
        try:
            process = get_lawsuit_by_id(lawsuit_id)
            if not process:
                return False
            
            result = self.client.sync_lawsuit(process)
            return result is not None
        except Exception as e:
            print(f"Erro ao sincronizar: {e}")
            return False
    
    def sync_remote_to_local(self, remote_numero: str) -> bool:
        """Importa processo do Legal AI"""
        try:
            remote = self.client.get_lawsuit_by_number(remote_numero)
            if not remote:
                return False
            
            create_lawsuit(remote)
            return True
        except Exception as e:
            print(f"Erro ao importar: {e}")
            return False
```

#### 2.3 UI para sincronização

**Em `main.py`**, adicionar aba em Processos:

```python
def _build_processos_sync_tab(self, parent):
    """Aba de sincronização com Legal AI"""
    
    # Status de sincronização
    status_frame = ctk.CTkFrame(parent, fg_color=COLORS['bg_card'])
    status_frame.pack(fill="x", padx=20, pady=10)
    
    # ... implementar UI ...
```

---

### 3. Gráficos e Visualizações (1 hora)

#### 3.1 Criar módulo de gráficos

```bash
mkdir -p modules/ui
touch modules/ui/__init__.py
touch modules/ui/charts.py
pip install matplotlib  # ou plotly
```

#### 3.2 Implementar gráficos

**Arquivo**: `modules/ui/charts.py`

```python
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class DashboardCharts:
    """Gráficos para o dashboard"""
    
    @staticmethod
    def plot_lawsuit_status_distribution(lawsuits):
        """Gráfico de pizza: distribuição por status"""
        # Contar por status
        # Criar pie chart
        # Retornar figura
        pass
    
    @staticmethod
    def plot_settlement_trend(settlements):
        """Gráfico de linha: acordos ao longo do tempo"""
        pass
    
    @staticmethod
    def plot_judge_performance(lawsuits):
        """Gráfico de barras: performance dos juízes"""
        pass
```

#### 3.3 Integrar no Dashboard

**Modificar `build_dashboard()` em `main.py`**

---

### 4. Backup e Restore (1 hora)

#### 4.1 Adicionar funções em database.py

```python
import shutil
from datetime import datetime

def backup_database(output_dir="backups") -> str:
    """Cria backup do banco de dados"""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{output_dir}/backup_{timestamp}.db"
    shutil.copy(DB_PATH, backup_file)
    return backup_file

def restore_database(backup_path: str) -> bool:
    """Restaura banco de um backup"""
    try:
        shutil.copy(backup_path, DB_PATH)
        return True
    except Exception as e:
        print(f"Erro ao restaurar: {e}")
        return False

def list_backups(backup_dir="backups") -> list:
    """Lista backups disponíveis"""
    if not os.path.exists(backup_dir):
        return []
    return sorted([f for f in os.listdir(backup_dir) if f.startswith("backup_")])
```

#### 4.2 UI para Backup

**Novo método em `main.py`**:

```python
def build_backup_config(self, parent):
    """Aba de backup e restauração"""
    # Mostrar último backup
    # Botão "Fazer Backup"
    # Listar backups disponíveis
    # Botão "Restaurar"
    pass
```

---

### 5. Busca e Filtro (0.5 horas)

#### 5.1 Módulo de busca global

```bash
mkdir -p modules/search
touch modules/search/__init__.py
touch modules/search/global_search.py
```

#### 5.2 Implementar busca

```python
class GlobalSearch:
    """Busca global em processos, clientes, magistrados"""
    
    @staticmethod
    def search_processes(query: str):
        """Busca em processos"""
        lawsuits = get_all_lawsuits()
        query_lower = query.lower()
        return [
            l for l in lawsuits
            if query_lower in str(l).lower()
        ]
    
    @staticmethod
    def search_clients(query: str):
        """Busca em clientes"""
        clients = get_all_clientes()
        query_lower = query.lower()
        return [
            c for c in clients
            if query_lower in c.get('nome', '').lower()
            or query_lower in c.get('cpf', '').lower()
        ]
```

---

## 📅 Cronograma de Implementação

| Dia | Tarefa | Tempo | Dependências |
|-----|--------|-------|---|
| 1 | Validadores (1.1-1.5) | 2h | Python 3.9+ |
| 2 | Sincronização (2.1-2.3) | 1.5h | API Bridge ✓ |
| 2 | Gráficos (3.1-3.3) | 1h | matplotlib/plotly |
| 3 | Backup (4.1-4.2) | 1h | sqlite3 ✓ |
| 3 | Busca (5.1-5.2) | 0.5h | database.py ✓ |
| **Total** | | **~6h** | |

---

## ✅ Checklist de Preparação

- [ ] Ler PHASE1_COMPLETE.md
- [ ] Ler PHASE2_ROADMAP.md
- [ ] Revisar TECHNICAL_SUMMARY.md
- [ ] Ter ambiente Python pronto
- [ ] Executar testes básicos (test_api_bridge.py)
- [ ] Backup do código atual
- [ ] Criar branch git para Fase 2 (opcional)

---

## 🔧 Ferramentas Necessárias

### Bibliotecas Python

```bash
# Já instaladas (no requirements.txt)
pip install requests sqlite3

# Novos (adicionar a requirements.txt)
pip install matplotlib>=3.5.0
pip install python-dotenv>=0.19.0

# Alternativos para gráficos
pip install plotly>=5.0.0  # Mais interativo que matplotlib
```

### Estrutura de Arquivos a Criar

```
modules/
├── validators/           [NOVO]
│   ├── __init__.py
│   ├── date_validator.py
│   ├── number_validator.py
│   └── document_validator.py
├── sync/                 [NOVO]
│   ├── __init__.py
│   └── process_sync.py
├── search/              [NOVO]
│   ├── __init__.py
│   └── global_search.py
└── ui/                  [NOVO]
    ├── __init__.py
    └── charts.py

tests/                   [NOVO]
├── test_validators.py
├── test_sync.py
└── test_search.py
```

---

## 📝 Testes para Fase 2

### Unit Tests (Exemplo)

```python
# tests/test_validators.py
from modules.validators.date_validator import DateValidator

def test_validate_date_valid():
    valid, msg = DateValidator.validate_date("19/05/2026")
    assert valid == True
    
def test_validate_date_invalid():
    valid, msg = DateValidator.validate_date("32/13/2026")
    assert valid == False
```

---

## 🚀 Como Começar

### Passo 1: Preparar Ambiente

```bash
# Ativar venv
.\venv\Scripts\Activate.ps1  # Windows
# ou
source venv/bin/activate     # macOS/Linux

# Verificar que tudo funciona
python test_api_bridge.py
python validate_deps.py
```

### Passo 2: Criar Branch (Opcional)

```bash
git checkout -b feature/phase2-improvements
git pull origin master
```

### Passo 3: Iniciar Implementação

```bash
# Criar estrutura
mkdir -p modules/validators modules/sync modules/search modules/ui

# Começar com validadores (tarefa 1)
touch modules/validators/__init__.py
# ... criar date_validator.py, etc
```

### Passo 4: Testar Regularmente

```bash
# Após cada módulo
python test_validators.py
python test_sync.py
python test_search.py

# Teste completo
python test_integration_full.py
```

### Passo 5: Fazer Commits

```bash
git add modules/validators
git commit -m "Adicionar módulo de validadores - Fase 2

- date_validator.py: validação de datas DD/MM/AAAA
- number_validator.py: validação de moeda e percentuais
- document_validator.py: validação de CPF/CNPJ

Co-Authored-By: Oz <oz-agent@warp.dev>"
```

---

## 💡 Dicas para Desenvolvimento

1. **Comece simples**: Implemente uma tarefa por vez
2. **Teste frequentemente**: Após cada mudança
3. **Documente**: Adicione docstrings nos métodos
4. **Revise**: Leia código antes de commitar
5. **Integre**: Teste com a UI após implementar

---

## 📚 Referências

- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - O que foi feito na Fase 1
- [PHASE2_ROADMAP.md](PHASE2_ROADMAP.md) - Detalhes de cada tarefa
- [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md) - Arquitetura do projeto
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Como usar API Bridge

---

## ❓ FAQ

**P: Por onde começar?**
R: Leia PHASE2_ROADMAP.md, depois comece com validadores.

**P: Preciso fazer git branch?**
R: Não é obrigatório, mas é recomendado para organização.

**P: Como testar meu código?**
R: Crie um arquivo test_[feature].py e use assert.

**P: Quando fazer commit?**
R: Após cada tarefa ou funcionalidade completa.

---

**Status**: Pronto para Começar ✅  
**Próxima Etapa**: Implementar Validadores (Tarefa 1.1)  
**Desenvolvido por**: Oz Agent  
**Data**: 2026-05-19
