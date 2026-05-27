# Especificação do SaaS Jurídico Trabalhista

> Documento de **visão/produto**. Distingue **[ATUAL]** (o que existe no repo)
> de **[ALVO]** (objetivo do SaaS, ainda não implementado). Não trate itens
> [ALVO] como fato. Para orientação operacional da IA, ver `CLAUDE.md`.
>
> Direção do produto: SaaS para advogados trabalhistas que deve gerenciar
> clientes, controlar processos, gerar documentos, integrar IA, controlar
> audiências, organizar tarefas e emitir relatórios.
>
> **Implementação inicial:** uma base executável já existe em `backend/`
> (FastAPI + SQLAlchemy + JWT/RBAC). Ver `backend/README.md`.

# Especificação do sistema (12 tópicos)

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
  (agenda/prazos), (6) **organização de tarefas**, (7) **emissão de relatórios**.

## 4. Arquitetura

- **[ATUAL]** Monólito desktop: `main.py` (GUI CustomTkinter) chama diretamente
  os pacotes `core/` e `modules/` (ausentes do checkout). Wrapper web fino
  `app_web.py` (Flask) expõe parte da lógica como JSON.
- **[ALVO]** Arquitetura web cliente-servidor: API backend stateless + frontend
  web (SPA), banco gerenciado, workers assíncronos para tarefas pesadas. Multi-tenant
  com isolamento de dados por escritório. Base inicial entregue em `backend/`.

## 5. Segurança

- **[ATUAL]** Mínima: app local sem autenticação. `.pre-commit-config.yaml` roda
  TruffleHog. `.env` está versionado (com placeholders) apesar do `.gitignore`.
- **[ALVO]** Autenticação + RBAC, isolamento entre tenants, **LGPD**, criptografia
  em trânsito e repouso, segredos fora do repo, auditoria, e cuidado ao enviar
  dados a APIs de IA externas. Ver "Requisitos de segurança".

## 6. Banco de dados

- **[ATUAL]** SQLite local (`core/database.py`), ~7 tabelas, acesso direto por
  funções, monousuário.
- **[ALVO]** Banco relacional gerenciado (PostgreSQL), `tenant_id` em todas as
  tabelas, migrações versionadas, novas entidades (audiências, tarefas, financeiro).
  A base `backend/` usa SQLAlchemy (SQLite por padrão, troca para Postgres via env).

## 7. Escalabilidade

- **[ATUAL]** Não escala: desktop monousuário; geração de IA/PDF síncrona.
- **[ALVO]** API sem estado atrás de load balancer, pool de conexões, fila +
  workers (Celery/RQ) para IA/documentos/relatórios, cache para leituras frequentes.

## 8. Frontend

- **[ATUAL]** Desktop em CustomTkinter (`main.py`). Não há frontend web;
  `app_web.py` devolve só JSON.
- **[ALVO]** Aplicação web (SPA — React/Vue) consumindo a API, com telas de
  clientes, processos, agenda de audiências, tarefas, documentos e dashboards.

## 9. Backend

- **[ATUAL]** Lógica em `modules/`/`core/` (ausentes) + Flask `app_web.py`. Os
  arquivos `api.py`/`cli.py` são de **outro projeto** (AgenticSeek).
- **[ALVO]** API HTTP completa com autenticação, REST para todos os recursos e
  validação. Implementação inicial em `backend/` (FastAPI).

## 10. IA integrada

- **[ATUAL]** `modules/ia/gerador.py` (`GeradorPecas`) gera 10 tipos de peça via
  OpenAI GPT-4.1, com templates locais como fallback. `modules/api_bridge.py`
  (`LegalAIClient`) integra a um serviço externo.
- **[ALVO]** IA central ao produto, com chaves por tenant, controle de custo e
  privacidade (não enviar dados sensíveis sem necessidade). Ao construir novas
  integrações, prefira os modelos Claude mais recentes.

## 11. Deploy

- **[ATUAL]** Configurações conflitantes: `Procfile`/`railway.json`/`render.yaml`
  rodam `python main.py` (GUI, não roda headless); `docker-compose.yml` roda o
  Flask na 5000.
- **[ALVO]** Deploy da API web em container (não a GUI desktop). Padronizar os
  arquivos de deploy nesse entry point.

## 12. Futuro / crescimento

- **Controle de audiências** — agenda, prazos processuais, lembretes.
- **Organização de tarefas** — to-dos, atribuição a usuários, status.
- **Relatórios** — relatórios consolidados.
- **Módulo financeiro** — honorários, faturamento e relatórios financeiros.
- **Plataforma SaaS** — multi-tenant, autenticação/RBAC, migração SQLite → Postgres,
  frontend web, processamento assíncrono e conformidade LGPD.

---

# Módulos do SaaS

## Autenticação
- Login com e-mail/senha; senhas com hash forte (bcrypt). [implementado em `backend/`]
- **JWT** (access curto + refresh). [implementado]
- Recuperação de senha por token de uso único com expiração. [implementado]
- Permissões por papel (RBAC) sobre os 4 perfis. [implementado]

## Clientes
- Cadastro (CPF/CNPJ, contato, endereço). [implementado]
- Documentos anexados ao cliente. [alvo]
- Histórico de interações e vínculo com processos. [parcial — vínculo implementado]

## Processos
- Número do processo e tribunal/vara. [implementado]
- Andamento (movimentações/timeline). [implementado]
- **Audiências** vinculadas ao processo (data, tipo, local). [implementado]
- Anexos (peças, documentos, provas). [alvo]

## Financeiro
- Honorários (lançamento, status de pagamento). [implementado]
- Contratos (geração e gestão). [alvo]
- Boletos / cobrança. [alvo]
- Relatórios financeiros. [parcial] Acessível ao perfil **Financeiro**.

## IA
- Gerar petições — endpoint `backend/` usando a **API da Claude (Anthropic)**, com
  fallback de template local quando não há chave. Modelo via `CLAUDE_MODEL`. [implementado]
- Resumir PDFs. [alvo]
- Responder perguntas jurídicas. [alvo]
- Analisar contratos. [alvo]
- Considerações: chave/uso por tenant, controle de custo, e **não enviar dados
  pessoais sensíveis a APIs externas sem necessidade** (LGPD).

---

# Requisitos de segurança

> Padrões para o SaaS. Itens marcados [ok] têm base no `backend/`; os demais são alvo.

- **OWASP Top 10** — checklist de referência em todo o desenvolvimento.
- **JWT seguro** [ok parcial] — segredo forte fora do repo; expiração curta no
  access; refresh separado; validar `exp`; nunca `alg: none`. (Revogação de
  refresh ainda é alvo.)
- **Rate limiting** [alvo] — em login e endpoints sensíveis.
- **Criptografia** — TLS em trânsito; dados em repouso criptografados; segredos
  via env/cofre (lembrar: `.env` está versionado — corrigir).
- **LGPD** — base legal, minimização, direito de exclusão, cautela com IA externa.
- **Logs** [ok parcial] — eventos relevantes sem vazar segredos.
- **Auditoria** [ok] — `AuditLog` por usuário/tenant no `backend/`.
- **Backup** [alvo] — rotina de backup/restauração do banco.
- **SQL Injection** [ok] — uso exclusivo de ORM/queries parametrizadas (SQLAlchemy).
- **XSS** [alvo — frontend] — escape/sanitização de saída; CSP.
- **CSRF** [alvo — frontend] — APIs com JWT em header são menos expostas; validar
  conforme estratégia do frontend.

---

# Desenho técnico

## Modelagem de dados

Alvo multi-tenant — toda tabela com `tenant_id` (escritório). Entidades:

- **Tenant (escritório)** 1—N **Usuário** (admin/advogado/cliente/financeiro).
- **Cliente** 1—N **Processo**; **Cliente** 1—N **Documento**.
- **Processo** (número, tribunal/vara, status) 1—N **Andamento**, 1—N **Audiência**,
  1—N **Anexo**, 1—N **Peça gerada**.
- **Magistrado** 1—N **Processo**; **Acordo** 1—1 **Processo**.
- **Tarefa** (responsável, prazo, status) vinculada a processo/cliente.
- Financeiro: **Honorário**, **Contrato**, **Boleto/Cobrança**.
- **AuditLog** (usuário, ação, entidade, timestamp) — transversal.

Implementado em `backend/models.py`: Tenant, User, Cliente, Processo, Andamento,
Audiencia, Tarefa, Honorario, AuditLog.

## APIs

- REST versionada (`/api/v1/...`), JSON, autenticada por JWT (Bearer), com escopo
  de tenant **derivado do token** (nunca do payload do cliente).
- Recursos: `auth`, `clientes`, `processos` (+ `andamentos`, `audiencias`),
  `tarefas`, `financeiro`, `ia`.
- Validação Pydantic, paginação em listagens, rate limiting (alvo), erros padronizados.
- Operações longas (IA/PDF/relatórios) idealmente assíncronas.

## Testes

- **pytest** com banco isolado (SQLite em memória) e fixtures por tenant.
- Cobrir: autenticação/RBAC (cada papel só acessa o que deve), isolamento entre
  tenants, contratos de API, e mock das chamadas de IA.
- Rodar em CI a cada push/PR (workflow de testes ainda é alvo).
- Suíte inicial em `backend/tests/`.

---

# Custo e deploy (barato)

Estratégia para manter custo baixo no início e escalar só quando houver receita.

**Recomendado (mais barato e rápido): Fly.io + SQLite em volume.** Ver `fly.toml`.
- 1 container pequeno (`shared-cpu-1x`, 256MB) com SQLite num **volume persistente**
  (`/data/app.db`), sem banco gerenciado (US$0 de banco).
- **Escala a zero** quando ocioso (`min_machines_running = 0`): paga ~nada parado e
  acorda em poucos segundos na 1ª requisição.
- `WEB_CONCURRENCY=1` (consistente com SQLite e com o rate limit em memória).
  SQLite roda em WAL + `busy_timeout` (ver `backend/database.py`) para concorrência.

**Alternativa: Render** (`render.yaml`). Web service free + Postgres free, mas o
disco free é efêmero (por isso Postgres) e o Postgres free expira em 90 dias
(~US$7/mês depois). Mais caro que o Fly para começar.

Independente do host:
- **Banco**: troca SQLite → Postgres só mudando `DATABASE_URL` (normalizado no
  `config.py`); sem mudança de código.
- **IA**: custo só quando `OPENAI_API_KEY` está configurada; sem ela, usa template
  local (R$ 0). Controlar uso/custo por tenant é alvo.
- **Escala**: ao crescer, aumentar a VM, ir para Postgres, subir `WEB_CONCURRENCY`
  e mover o rate limit para Redis (hoje é em memória, 1 instância).

Deploy portátil: `backend/Dockerfile` (build a partir da raiz do repo) roda em
Fly, VPS ou qualquer plataforma de containers; aplica `alembic upgrade head` no start.

# Billing / assinatura (desenho — não implementado)

Modelo SaaS por assinatura de escritório (tenant). **Recomendação: Stripe.**

- **Planos**: ex.: Free (1 usuário, N processos), Pro (mensal por escritório),
  por assento (preço × nº de usuários). Definir limites por plano.
- **Entidades a adicionar**: `Subscription` (tenant_id, plano, status,
  `current_period_end`, `stripe_customer_id`, `stripe_subscription_id`) e,
  opcionalmente, `Plan`/`PriceTier`.
- **Fluxo Stripe**:
  1. Ao criar o tenant, criar um *Customer* no Stripe.
  2. *Stripe Checkout* (ou *Billing Portal*) para o admin assinar/gerenciar.
  3. **Webhook** (`/api/v1/billing/webhook`) tratando `checkout.session.completed`,
     `customer.subscription.updated/deleted`, `invoice.payment_failed` para
     atualizar `Subscription.status`.
  4. Validar a assinatura do webhook com o *signing secret* (segredo via env).
- **Enforcement**: uma dependência (ex.: `require_active_subscription`) que
  bloqueia escrita quando a assinatura não está ativa, e checagem de limites por
  plano. Leitura pode permanecer liberada (somente-leitura) em estado inadimplente.
- **Segurança/fiscal**: nunca armazenar dados de cartão (Stripe cuida disso);
  emitir nota fiscal conforme a legislação (integração fiscal é alvo separado).

