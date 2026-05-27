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
