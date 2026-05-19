# Guia de Integração - Painel Jurídico v2 ↔ Legal AI

## 🎯 Objetivo

Conectar o Painel Jurídico v2 (aplicativo desktop) com o Legal AI Backend (API REST) para:
- Sincronizar processos
- Executar análises NLP remotas
- Compartilhar documentos
- Gerar relatórios consolidados

## 🚀 Quick Start

### Passo 1: Verificar Pré-requisitos

**Painel v2**
```bash
cd C:\Users\Notebook\Downloads\painel_juridico_v2_final\painel_juridico_v2
python main.py
```

**Legal AI Backend** (em outro terminal)
```bash
cd C:\Users\Notebook\legal-ai\legal-app
python main.py
```

### Passo 2: Acessar Integração no Painel

1. Abra o Painel Jurídico v2
2. Vá para **CONFIGURAÇÕES** (sidebar)
3. Clique em **Integração Legal AI**

### Passo 3: Configurar Conexão

1. **Verifique a URL**: Padrão é `http://localhost:8000`
2. **Clique em "Testar Conexão"**
3. Você verá:
   - ✓ Conectado ao Legal AI (sucesso)
   - ✗ Desconectado do Legal AI (erro)

### Passo 4: Usar Funcionalidades

Uma vez conectado, você pode:

| Funcionalidade | Como Usar |
|---|---|
| 📄 Análise NLP | Texto → Legal AI → Entidades, Classificação, Sentimento |
| 📊 Sincronizar Processos | Criar localmente → Legal AI recebe cópia |
| 🔍 Busca Full-Text | Buscar em todos os documentos do Legal AI |
| 📋 Upload de Documentos | Enviar PDFs/Word para análise remota |
| 📈 Relatórios | Gerar relatórios consolidados em PDF |

## 📋 Métodos Disponíveis

### Conexão
```python
client.test_connection()        # Testa se servidor está online
client.get_health()             # Status do servidor
client.get_server_info()        # Versão e modelos disponíveis
client.update_server_url(url)   # Muda URL dinâmicamente
```

### Processos
```python
client.create_lawsuit_remote(data)      # Cria processo remoto
client.get_lawsuits_remote()            # Lista processos do Legal AI
client.get_lawsuit_by_number(numero)    # Busca por número
client.sync_lawsuit(lawsuit_id)         # Sincroniza um processo
```

### Documentos
```python
client.upload_document(file, process_id)    # Envia arquivo
client.get_lawsuit_documents(lawsuit_id)    # Lista documentos
client.get_document_analysis(doc_id)        # Análise de documento
```

### NLP e Análises
```python
client.analyze_text(text)              # Análise genérica
client.extract_entities(text)          # Extração de entidades
client.classify_document(text)         # Classificação
client.analyze_sentiment(text)         # Sentimento
client.summarize_text(text)            # Resumo
client.search_documents(query)         # Busca full-text
```

### Relatórios
```python
client.get_process_report(process_id)      # Relatório do processo
client.export_to_pdf(report_id, path)      # Exportar em PDF
```

## 🧪 Testes

Executar testes de integração:
```bash
python test_api_bridge.py
```

Saída esperada:
```
✓ LegalAIClient instanciado
✓ URL Base: http://localhost:8000
✓ Timeout: 30s
✓ 20+ métodos disponíveis
```

## ⚙️ Configuração Avançada

### Mudar URL do Servidor

Na aba de integração:
1. Altere a URL (ex: `http://seu-servidor.com:8000`)
2. Clique em "Testar Conexão"

### Aumentar Timeout

```python
from modules.api_bridge import LegalAIClient
client = LegalAIClient()
client.set_timeout(60)  # 60 segundos
```

### Usar em Scripts

```python
from modules.api_bridge import LegalAIClient

client = LegalAIClient(url="http://seu-servidor.com:8000")

# Testar conexão
if client.test_connection():
    print("Conectado ao Legal AI!")
    
    # Criar processo
    process_data = {
        "numero_processo": "0012345-67.2024.8.00.0000",
        "vara": "10ª Vara do Trabalho",
        "reclamante": "João Silva",
        "reclamada": "Empresa XYZ"
    }
    result = client.create_lawsuit_remote(process_data)
else:
    print("Servidor não disponível")
```

## 🔧 Troubleshooting

### Erro: "Desconectado do Legal AI"

**Causas Possíveis:**
1. Legal AI Backend não está rodando
2. URL incorreta
3. Firewall bloqueando porta 8000

**Solução:**
```bash
# Verifique se Legal AI está rodando
cd C:\Users\Notebook\legal-ai\legal-app
python main.py

# Verifique a URL (deve estar acessível)
# Padrão: http://localhost:8000
```

### Erro: "Timeout"

O servidor demorou muito para responder. Aumente o timeout:
```python
client.set_timeout(60)  # 60 segundos ao invés de 30
```

### Erro: "Connection Refused"

Firewall pode estar bloqueando. Teste:
```bash
# Windows PowerShell
Test-NetConnection -ComputerName localhost -Port 8000
```

## 📚 Exemplos de Uso

### Exemplo 1: Sincronizar Processo

```python
# Criar localmente
lawsuit = {
    "numero_processo": "0001234-56.2024.8.00.0000",
    "vara": "5ª Vara do Trabalho",
    "reclamante": "Maria Santos",
    "reclamada": "Empresa ABC"
}

# Sincronizar com Legal AI
client.sync_lawsuit(lawsuit)
print("Processo sincronizado!")
```

### Exemplo 2: Análise NLP

```python
texto = "O reclamante alega justa causa por atraso de salários"

# Extrair entidades
entities = client.extract_entities(texto)
# Resultado: ['reclamante', 'justa causa', 'atraso', 'salários']

# Classificar
classificacao = client.classify_document(texto)
# Resultado: 'trabalhista'

# Sentimento
sentimento = client.analyze_sentiment(texto)
# Resultado: 'negativo'
```

### Exemplo 3: Upload e Análise de Documento

```python
# Enviar arquivo para análise
file_path = "contrato.pdf"
analysis = client.upload_document(file_path, process_id=123)

# Obter resultado
doc_analysis = client.get_document_analysis(analysis['doc_id'])
print(f"Temas identificados: {doc_analysis['themes']}")
print(f"Riscos: {doc_analysis['risks']}")
```

## 🔐 Segurança

- URL sensível? Use HTTPS: `https://seu-servidor.com:8443`
- Credenciais? Implemente auth no Legal AI Backend
- Dados sensíveis? Use VPN para comunicação

## 📈 Próximas Melhorias

- [ ] Suporte a autenticação (Bearer Token)
- [ ] Cache de respostas
- [ ] Sincronização automática em background
- [ ] Logging detalhado de requisições
- [ ] Suporte a múltiplos servidores

## 📞 Suporte

Para dúvidas ou issues:
1. Verifique `PHASE1_COMPLETE.md`
2. Execute `test_api_bridge.py`
3. Consulte logs do Legal AI Backend

---

**Versão**: 1.0  
**Última Atualização**: 2026-05-19  
**Status**: ✓ Production Ready
