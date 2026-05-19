# Fase 2: Melhorias de Funcionalidade - Roadmap

**Data**: 2026-05-19  
**Status**: Planejado  
**Timeline Estimado**: 3-4 horas  
**Prioridade**: Alta  

## 📋 Visão Geral

Após a conclusão bem-sucedida da **Fase 1 (Integração com Legal AI)**, a Fase 2 focará em melhorias críticas de funcionalidade, validação de dados, e novas features.

## 🎯 Objetivos Principais

1. **Validação de Dados** - Implementar validações robustas em formulários
2. **Sincronização Bidirecional** - Permitir troca de dados com Legal AI
3. **Visualizações** - Adicionar gráficos e charts
4. **Backup/Restore** - Implementar proteção de dados
5. **Busca/Filtro** - Melhorar UX em telas principais

## 📊 Tarefas Prioritizadas

### 1️⃣ Validação de Dados (2 horas)

#### 1.1 Validação de Datas
**Arquivo**: `modules/validators/date_validator.py` (NOVO)
**Tarefa**: Criar módulo de validação de datas (DD/MM/AAAA)

```python
class DateValidator:
    @staticmethod
    def validate_date(date_str: str) -> bool:
        # Validar formato DD/MM/AAAA
        # Validar se data é válida
        # Validar se data não é futura (para admissão)
    
    @staticmethod
    def validate_date_range(start_date, end_date) -> bool:
        # Validar que end_date > start_date
```

**Onde Usar**:
- `build_processo_form()` - Datas distribuição/encerramento
- `build_calculadora()` - Datas admissão/demissão

#### 1.2 Validação de Números
**Arquivo**: `modules/validators/number_validator.py` (NOVO)

```python
class NumberValidator:
    @staticmethod
    def validate_currency(value: str) -> bool:
        # Validar formato R$
        # Validar valores positivos
    
    @staticmethod
    def validate_percentage(value: float) -> bool:
        # Validar valores 0-100%
```

#### 1.3 Validação de Documentos
**Arquivo**: `modules/validators/document_validator.py` (NOVO)

```python
class DocumentValidator:
    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        # Validar CPF
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        # Validar CNPJ
```

**Integração**: Aplicar em `_build_cliente_form()` e processos

---

### 2️⃣ Sincronização Bidirecional (1.5 horas)

#### 2.1 Sync de Processos
**Arquivo**: `modules/sync/process_sync.py` (NOVO)

```python
class ProcessSync:
    def __init__(self, client: LegalAIClient):
        self.client = client
    
    def sync_local_to_remote(self, lawsuit_id: int) -> bool:
        # Enviar processo local para Legal AI
        process = db.get_lawsuit_by_id(lawsuit_id)
        return self.client.sync_lawsuit(process)
    
    def sync_remote_to_local(self, remote_id: str) -> bool:
        # Importar processo do Legal AI
        remote = self.client.get_lawsuit_by_number(remote_id)
        return db.create_lawsuit(remote)
    
    def sync_all() -> Dict:
        # Sincronizar todos os processos pendentes
        # Retornar relatório de sucesso/falha
```

#### 2.2 UI para Sincronização
**Arquivo**: `main.py` - Novo método
**Localização**: Nova aba em "Processos" → "Sincronizar com Legal AI"

```python
def build_processos_sync_tab(self):
    # UI com 3 seções:
    # 1. Status de sincronização
    # 2. Botão "Sincronizar Tudo"
    # 3. Histórico de sincronizações
```

---

### 3️⃣ Visualizações e Gráficos (1 hora)

#### 3.1 Dashboard com Charts
**Arquivo**: `modules/ui/charts.py` (NOVO)
**Dependência**: matplotlib ou plotly

```python
class DashboardCharts:
    @staticmethod
    def plot_lawsuit_status_distribution():
        # Gráfico: % de processos por status
    
    @staticmethod
    def plot_settlement_trend():
        # Gráfico: Acordos ao longo do tempo
    
    @staticmethod
    def plot_judge_performance():
        # Gráfico: Taxa de sucesso por juiz
```

#### 3.2 Integração no Dashboard
**Arquivo**: `main.py` - Modificar `build_dashboard()`

Adicionar:
- Gráfico de status de processos (pie chart)
- Gráfico de tendência de acordos (line chart)
- Gráfico de juízes mais bem-sucedidos (bar chart)

---

### 4️⃣ Backup e Restore (1 hora)

#### 4.1 Funções de Backup
**Arquivo**: `core/database.py` - Adicionar métodos

```python
def backup_database(output_path: str) -> bool:
    # Copiar database.db para arquivo .backup
    # Timestamp: backup_YYYYMMDD_HHMMSS.db
    # Retornar caminho do backup

def restore_database(backup_path: str) -> bool:
    # Restaurar database.db de um backup
    # Validar integridade
    # Fazer rollback em caso de erro
```

#### 4.2 UI para Backup/Restore
**Arquivo**: `main.py` - CONFIGURAÇÕES → "Backup e Dados"

```python
def build_backup_config(self, parent):
    # Seção 1: Último Backup
    # Seção 2: Botão "Fazer Backup Agora"
    # Seção 3: Listar backups disponíveis
    # Seção 4: Botão "Restaurar"
```

---

### 5️⃣ Busca e Filtro (0.5 horas)

#### 5.1 Busca Global
**Arquivo**: `modules/search/global_search.py` (NOVO)

```python
class GlobalSearch:
    def search_processes(query: str) -> List:
        # Buscar por número, vara, partes
    
    def search_clients(query: str) -> List:
        # Buscar por nome, CPF, telefone
    
    def search_judges(query: str) -> List:
        # Buscar por nome, vara
```

#### 5.2 Filtros em Telas
**Arquivo**: `main.py` - Modificar:
- `build_processos()` - Adicionar filtro por status/vara/juiz
- `build_clientes()` - Adicionar filtro por região/tipo
- `build_magistrados()` - Adicionar filtro por vara/tendência

---

## 📅 Cronograma Sugerido

| Dia | Tarefa | Tempo | Status |
|-----|--------|-------|--------|
| 1 | Validação de Dados | 2h | ⭕ TODO |
| 2 | Sincronização | 1.5h | ⭕ TODO |
| 2 | Gráficos | 1h | ⭕ TODO |
| 3 | Backup/Restore | 1h | ⭕ TODO |
| 3 | Busca/Filtro | 0.5h | ⭕ TODO |
| 3 | Testes e Polish | 0.5h | ⭕ TODO |
| **Total** | | **~6h** | |

## 🔧 Dependências a Instalar

```bash
pip install matplotlib>=3.5.0    # Para gráficos
# ou
pip install plotly>=5.0.0        # Alternativa interativa
```

Verificar requirements.txt e atualizar.

## 🧪 Testes Necessários

### Unit Tests (test_validators.py)
```python
def test_validate_date_valid():
    assert DateValidator.validate_date("19/05/2026") == True

def test_validate_date_invalid():
    assert DateValidator.validate_date("32/13/2026") == False

def test_validate_cpf_valid():
    assert DocumentValidator.validate_cpf("123.456.789-09") == True
```

### Integration Tests (test_sync.py)
```python
def test_sync_process_to_legal_ai():
    # Criar processo local
    # Syncronizar com Legal AI
    # Validar que foi criado remotamente

def test_sync_process_from_legal_ai():
    # Criar processo no Legal AI (mock)
    # Importar para local
    # Validar integridade de dados
```

## 📝 Documentação a Atualizar

- [ ] README.md - Adicionar seção de validação e backup
- [ ] INTEGRATION_GUIDE.md - Adicionar seção de sincronização
- [ ] Criar VALIDATORS_GUIDE.md para documentar regras de validação
- [ ] Criar SYNC_DOCUMENTATION.md para sincronização

## 🚀 Arquivos a Criar

```
modules/
├── validators/                    [NOVO]
│   ├── __init__.py
│   ├── date_validator.py
│   ├── number_validator.py
│   └── document_validator.py
├── sync/                          [NOVO]
│   ├── __init__.py
│   └── process_sync.py
├── search/                        [NOVO]
│   ├── __init__.py
│   └── global_search.py
└── ui/                            [NOVO]
    ├── __init__.py
    └── charts.py

tests/
├── test_validators.py             [NOVO]
├── test_sync.py                   [NOVO]
└── test_search.py                 [NOVO]
```

## ✅ Checklist de Implementação

### Validação
- [ ] Criar módulo validators com 3 classes
- [ ] Integrar em formulários de processo
- [ ] Integrar em formulários de cliente
- [ ] Integrar em calculadora
- [ ] Testes unitários (100% cobertura)

### Sincronização
- [ ] Criar módulo sync
- [ ] Implementar sync local→remote
- [ ] Implementar sync remote→local
- [ ] UI com status e histórico
- [ ] Testes de integração

### Gráficos
- [ ] Escolher biblioteca (matplotlib/plotly)
- [ ] Criar módulo charts
- [ ] 3 gráficos no dashboard
- [ ] Atualizar em tempo real

### Backup/Restore
- [ ] Funções de backup em database.py
- [ ] UI em CONFIGURAÇÕES
- [ ] Listar backups anteriores
- [ ] Testes de restauração

### Busca/Filtro
- [ ] Módulo global_search
- [ ] Filtro em Processos
- [ ] Filtro em Clientes
- [ ] Filtro em Magistrados
- [ ] UI intuitiva

## 🎓 Recursos de Referência

- [Python datetime validation](https://docs.python.org/3/library/datetime.html)
- [Matplotlib Tutorial](https://matplotlib.org/stable/tutorials/index.html)
- [SQLite Backup Best Practices](https://www.sqlite.org/backup.html)
- [REST API Sync Patterns](https://www.oreilly.com/library/view/restful-web-services/9780596529260/)

## 🤝 Próximos Passos

1. **Revisar** este roadmap
2. **Escolher** bibliotecas de gráficos
3. **Criar** estrutura de validadores
4. **Implementar** uma tarefa por vez
5. **Testar** integrações
6. **Documentar** mudanças
7. **Commit** ao Git regularmente

## 📞 Contato/Dúvidas

Se tiver dúvidas durante a implementação:
- Consulte TECHNICAL_SUMMARY.md para arquitetura
- Revise test_final.py para padrões existentes
- Teste localmente antes de commit

---

**Próxima Fase**: Fase 3 (Deploy com PyInstaller)  
**Desenvolvido por**: Oz Agent  
**Data de Criação**: 2026-05-19  
**Versão**: 1.0  
**Status**: Ready for Implementation
