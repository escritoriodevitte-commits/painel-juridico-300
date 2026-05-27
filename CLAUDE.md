# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Critical context: read this first

This repository is in an inconsistent state. Two unrelated codebases are mixed
together, and the application source packages are **not committed**. Verify
assumptions before trusting any file.

### 1. The application source packages are missing

The intended app is **Painel Estratégico Jurídico v2** — a Brazilian
labor-law (Justiça do Trabalho) case-management tool. Its entry points
(`main.py`, `app_web.py`), all `test_*.py` files, `seed.py`, `verify_setup.py`,
and `validate_deps.py` import from `core/` and `modules/` packages:

- `core.database`, `core.services`
- `modules.calculadora.calc`, `modules.analytics.engine`, `modules.ia.gerador`
- `modules.exports.{pdf,csv_export,txt_export}`, `modules.api_bridge`, `modules.ui.validation_integration`

**None of these directories exist in the checkout.** They are not gitignored
(`.gitignore` only excludes `core/database.db`) — they were simply never
committed. As a result, `python main.py`, `python app_web.py`, and every test
fail immediately with `ModuleNotFoundError: No module named 'modules'` / `core`.
Confirm a package actually exists before editing or referencing it.

### 2. Leftover files from an unrelated project (AgenticSeek)

`api.py`, `cli.py`, `setup.py`, `pyproject.toml`, `config.ini`, `.env`,
`.env.example`, and `uv.lock` belong to a **different** project — "AgenticSeek"
(an LLM agent framework, see `pyproject.toml` `name = "agenticseek"` and
`setup.py` author Fosowl). They import a `sources/` package that also does not
exist. These files are unrelated to the legal app; do not treat
`pyproject.toml`/`config.ini`/`.env` as configuration for Painel Jurídico.

When asked to work on "the project," assume the legal app unless told otherwise.

## What the legal app actually is

A desktop application for managing labor-litigation strategy, built with:

- **CustomTkinter** — desktop GUI (`main.py`, ~13 screens, dark theme, sidebar nav)
- **SQLite** — local database (`core/database.py`, 7 tables: clients, lawsuits,
  judges, agreements, legal references, generated pieces, etc.)
- **OpenAI GPT-4.1** — generates 10 types of legal documents (`modules/ia/gerador.py`),
  with structured local templates as fallback when no API key is configured
- **ReportLab** — PDF export (`modules/exports/pdf.py`); also CSV/TXT export
- **Flask** — a thin web/JSON API alternative (`app_web.py`, port 5000) exposing
  dashboard, processos, clientes, calcular, and gerar-peca endpoints

Real dependencies are minimal — see `requirements.txt`:
`customtkinter`, `reportlab`, `openai` (plus stdlib `sqlite3`). Ignore the large
dependency list in `pyproject.toml`/`setup.py` (those are AgenticSeek's).

Core domain logic lives in `modules/calculadora/calc.py`: Brazilian labor
severance calculations under CLT 2026 (8 termination types, progressive INSS/IRRF,
overtime + DSR, vacation, FGTS + penalties, notice period per Lei 12.506/2011).
`seed.py` populates ~51 pre-loaded legal references on first run.

## Commands

Once the `core/` and `modules/` packages are present, the project uses Python
3.10+ and these workflows:

```bash
pip install -r requirements.txt   # install the 3 real deps

python main.py        # launch desktop GUI (requires a display; will fail headless)
python app_web.py     # launch Flask JSON API on :5000 (PORT env overrides)
```

### Tests

Tests are **standalone scripts with a custom pass/fail harness — not pytest**.
Run each directly; there is no test runner config:

```bash
python test_final.py           # broad suite across all modules ("99 tests")
python test_calculadora.py     # calculator-specific (CLT calculations)
python test_modules.py         # headless module smoke test (database, etc.)
python test_e2e.py             # end-to-end flow
python test_integration_full.py # Legal AI / api_bridge integration
python test_calc_priority1.py
python test_api_bridge.py
```

Diagnostics (also depend on the missing packages):

```bash
python verify_setup.py    # verifies db/calc/generator/analytics init
python validate_deps.py   # checks installed deps + local module imports
```

There is no lint or type-check configuration in the repo.

## Conventions

- **Language**: Code, comments, UI strings, and most docs are in **Portuguese
  (pt-BR)**. Match this when editing the legal app.
- **Currency**: format via `formatar_moeda()` (BR style: `R$ 1.234,56`).
  This helper is duplicated in `main.py` and `app_web.py`.
- **Secret scanning**: `.pre-commit-config.yaml` runs TruffleHog on commit and
  push. Do not commit secrets. Note `.env` is currently tracked (with placeholder
  keys) despite being listed in `.gitignore`.

## Deployment notes (inconsistent)

Multiple deploy targets are configured and they disagree on the entry point:

- `Procfile`, `railway.json`, `render.yaml` all run `python main.py` — but that
  is the GUI and will not run on a headless server. The web-deployable entry
  point is `app_web.py` (Flask, used by `docker-compose.yml` → port 5000).
- `Dockerfile` vs `Dockerfile.backend` and the many `*.ps1` / `deploy.*` scripts
  target different setups.

There are dozens of `.md` files (deployment guides, push instructions, status
reports, translated READMEs) — most are redundant historical artifacts. Treat
`README.md` as the canonical description of the legal app and ignore the rest
unless specifically relevant.

---

# Especificação do sistema (12 tópicos)

> Esta seção descreve o sistema em duas camadas:
> **[ATUAL]** = o que de fato existe no repositório hoje.
> **[ALVO]** = a visão de produto declarada pelo dono do projeto: um **SaaS
> jurídico para advogados trabalhistas**. Itens marcados como [ALVO] são
> objetivos/propostas — ainda não implementados. Não os trate como fato.
>
> Direção do produto (declarada): SaaS para advogados trabalhistas que deve
> gerenciar clientes, controlar processos, gerar documentos, integrar IA,
> controlar audiências, organizar tarefas e emitir relatórios.

## 1. Objetivo do sistema

- **[ATUAL]** Aplicação **desktop** monousuário (CustomTkinter + SQLite local)
  para gestão estratégica de processos trabalhistas: cadastro de clientes,
  processos, magistrados e acordos; calculadora de verbas rescisórias (CLT 2026);
  biblioteca jurídica; geração de peças com IA; exportação em PDF/CSV/TXT.
- **[ALVO]** Evoluir para um **SaaS multi-tenant** (web, multiusuário) para
  escritórios de advocacia trabalhista, com as sete capacidades acima.

## 2. Usuários

- **[ATUAL]** Um único operador local; não há autenticação, contas nem perfis.
- **[ALVO]** Multiusuário com isolamento por escritório (tenant) e quatro papéis
  (RBAC), exigindo login e auditoria por usuário:
  - **Administrador** — gestão do escritório, usuários, permissões e configurações.
  - **Advogado** — acesso operacional pleno: clientes, processos, audiências,
    tarefas, documentos e relatórios dos seus casos.
  - **Cliente** — acesso restrito e somente-leitura aos próprios processos,
    documentos e andamentos.
  - **Financeiro** — gestão de honorários, faturamento, acordos e relatórios
    financeiros; sem acesso ao mérito jurídico dos processos.

## 3. Funcionalidades

- **[ATUAL]** Gestão de clientes/processos/magistrados/acordos; calculadora
  trabalhista; biblioteca (~51 referências via `seed.py`); geração de 10 tipos
  de peça (`modules/ia/gerador.py`); módulos de "inteligência" (previsão, motor
  de teses, radar de risco, análise competitiva via `modules/analytics/engine.py`);
  exportação PDF/CSV/TXT.
- **[ALVO]** Sete pilares: (1) gestão de clientes, (2) controle de processos,
  (3) geração de documentos, (4) IA integrada, (5) **controle de audiências**
  (agenda/prazos — não existe hoje), (6) **organização de tarefas** (não existe
  hoje), (7) **emissão de relatórios** (hoje só exportações pontuais).
  Audiências, tarefas e relatórios consolidados são lacunas a construir.

## 4. Arquitetura

- **[ATUAL]** Monólito desktop: `main.py` (GUI CustomTkinter, ~13 telas) chama
  diretamente os pacotes `core/` e `modules/`. Existe ainda um wrapper web fino
  `app_web.py` (Flask) que expõe parte da lógica como JSON. **Lembre-se:** os
  pacotes `core/`/`modules/` não estão commitados (ver "Critical context").
- **[ALVO]** Arquitetura web cliente-servidor: API backend stateless + frontend
  web (SPA), banco gerenciado, workers assíncronos para tarefas pesadas (geração
  de IA, PDFs, relatórios). Multi-tenant com isolamento de dados por escritório.

## 5. Segurança

- **[ATUAL]** Mínima: app local sem autenticação. Único segredo é a chave OpenAI.
  `.pre-commit-config.yaml` roda TruffleHog (commit/push) para detectar segredos.
  Atenção: `.env` está versionado (com placeholders) apesar de listado no `.gitignore`.
- **[ALVO]** Como SaaS jurídico, segurança é crítica e ainda inexistente:
  autenticação + RBAC, isolamento entre tenants, **conformidade com a LGPD**
  (dados pessoais sensíveis de clientes/processos), criptografia em trânsito e em
  repouso, gestão de segredos fora do repo, trilha de auditoria, e cuidado ao
  enviar dados de processos a APIs de IA externas (OpenAI).

## 6. Banco de dados

- **[ATUAL]** SQLite local (`core/database.py`, arquivo `core/database.db`
  ignorado pelo git), ~7 tabelas (clientes, processos, magistrados, acordos,
  referências jurídicas, peças geradas, etc.). Acesso direto via funções
  (`get_all_lawsuits`, `create_cliente`, ...). Adequado a um único usuário.
- **[ALVO]** Banco relacional gerenciado (PostgreSQL é o caminho natural —
  `docker-compose.yml` já tem um stub comentado), com coluna/escopo de tenant em
  todas as tabelas, migrações versionadas e novas entidades para audiências,
  tarefas e relatórios.

## 7. Escalabilidade

- **[ATUAL]** Não escala: desktop monousuário; o Flask (`app_web.py`) chama
  `db.init_db()` no import e a geração de IA/PDF é síncrona.
- **[ALVO]** API sem estado atrás de load balancer, pool de conexões ao banco,
  fila + workers (ex.: Celery/RQ) para IA e geração de documentos/relatórios,
  e cache para leituras frequentes.

## 8. Frontend

- **[ATUAL]** Desktop em **CustomTkinter** (`main.py`). Não há frontend web:
  `app_web.py` devolve apenas JSON, sem templates/HTML; não há `templates/` nem
  `static/`.
- **[ALVO]** Aplicação web (SPA — ex.: React/Vue) consumindo a API, com telas
  de clientes, processos, agenda de audiências, tarefas, geração de documentos
  e dashboards/relatórios.

## 9. Backend

- **[ATUAL]** Lógica de negócio nos pacotes `modules/` e `core/` (ausentes do
  checkout). Exposição web limitada via Flask `app_web.py` (endpoints: dashboard
  `/`, `/api/processos`, `/api/clientes`, `/api/calcular`, `/api/gerar-peca`,
  `/health`). Os arquivos `api.py`/`cli.py` na raiz são de **outro projeto**
  (AgenticSeek) e não fazem parte do backend deste sistema.
- **[ALVO]** API HTTP completa (Flask ou FastAPI) com autenticação, endpoints
  REST para todos os recursos, validação de entrada e os módulos atuais
  reaproveitados como camada de serviço.

## 10. IA integrada

- **[ATUAL]** `modules/ia/gerador.py` (`GeradorPecas`) gera 10 tipos de peça
  jurídica via **OpenAI GPT-4.1**; sem chave de API, usa templates locais
  estruturados como fallback. `modules/api_bridge.py` (`LegalAIClient`) integra
  com um serviço externo de "Legal AI". A chave é configurada pela UI/`.env`.
- **[ALVO]** Manter a IA central ao produto, com chaves por tenant/escritório,
  controle de custo/uso, e atenção a privacidade (não enviar dados sensíveis sem
  necessidade). Ao trabalhar em recursos de IA neste repo, prefira os modelos
  Claude mais recentes quando construir novas integrações.

## 11. Deploy

- **[ATUAL]** Configurações conflitantes (ver "Deployment notes" acima):
  `Procfile`/`railway.json`/`render.yaml` rodam `python main.py` (GUI — não roda
  headless em servidor), enquanto `docker-compose.yml` roda o Flask `app_web.py`
  na porta 5000. Dois `Dockerfile`s e vários scripts `*.ps1`/`deploy.*` apontam
  para setups diferentes.
- **[ALVO]** Para um SaaS, o alvo de deploy deve ser **`app_web.py`/a API web**
  em container, não a GUI desktop. Padronizar os arquivos de deploy nesse
  entry point e remover os que apontam para `main.py`.

## 12. Futuro / crescimento

Lacunas declaradas como objetivo e ainda não implementadas:

- **Controle de audiências** — agenda, prazos processuais, lembretes.
- **Organização de tarefas** — to-dos, atribuição a usuários, status.
- **Relatórios** — relatórios consolidados (hoje há apenas exportações pontuais
  de PDF/CSV/TXT).
- **Módulo financeiro** — honorários, faturamento e relatórios financeiros
  (implícito pelo perfil "Financeiro"); inexistente hoje.
- **Plataforma SaaS** — multi-tenant, autenticação/RBAC, migração SQLite → Postgres,
  frontend web, processamento assíncrono e conformidade LGPD.

> Pré-requisito técnico para qualquer evolução: os pacotes `core/` e `modules/`
> precisam ser commitados ao repositório — sem eles o sistema não executa nem
> roda os testes.
