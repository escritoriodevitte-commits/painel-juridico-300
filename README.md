# Painel Estratégico Jurídico v2 — Software Desktop Python

## Visão Geral

Software desktop completo para gestão estratégica de processos trabalhistas, com interface gráfica (CustomTkinter), banco de dados local (SQLite), integração com OpenAI GPT-4.1 para geração de peças jurídicas e exportação em PDF via ReportLab.

**99 testes automatizados passando** — cobertura completa de todos os módulos.

## Estrutura do Projeto

```
painel_juridico_v2/
├── main.py                    # Interface gráfica principal (13 telas)
├── seed.py                    # 51 referências jurídicas pré-carregadas
├── requirements.txt           # Dependências
├── README.md
├── core/                      # Núcleo do sistema
│   ├── database.py            # 7 tabelas SQLite
│   └── services.py            # Serviços de negócio
├── modules/
│   ├── analytics/
│   │   └── engine.py          # Motor de análise estratégica
│   ├── calculadora/
│   │   └── calc.py            # Cálculo de verbas trabalhistas (CLT 2026)
│   ├── ia/
│   │   └── gerador.py         # 10 tipos de peça via GPT-4.1 + fallback
│   └── exports/
│       ├── pdf.py             # Exportação PDF (ReportLab)
│       ├── csv_export.py      # Exportação CSV
│       └── txt_export.py      # Exportação TXT
└── data/                      # Banco SQLite (criado automaticamente)
```

## Instalação

```bash
pip install -r requirements.txt
python main.py
```

## 13 Telas com Abas de Edição Manual

| Seção | Módulo | Edição Manual |
|-------|--------|---------------|
| Gestão | Dashboard — Métricas consolidadas | — |
| Gestão | Clientes — CRUD (CPF, telefone, email, endereço) | Cadastrar/Editar/Excluir |
| Gestão | Processos — Vinculado a clientes e juízes | Cadastrar/Editar/Excluir |
| Gestão | Magistrados — Perfil com posturas | Cadastrar/Editar/Excluir |
| Gestão | Acordos — Registro de resultados | Cadastrar/Editar/Excluir |
| Gestão | Biblioteca — 51 referências jurídicas | Cadastrar/Editar/Excluir |
| Gestão | Calculadora — Verbas rescisórias CLT 2026 | Todos os campos |
| Inteligência | Previsão — Score preditivo | — |
| Inteligência | Motor Teses — Ranking e provas | — |
| Inteligência | Radar Risco — Classificação por processo | — |
| Inteligência | Competitiva — KPIs e rankings | — |
| Inteligência | Gerar Peças — 3 abas (IA/Manual/Histórico) | Cadastro manual |
| Config | API OpenAI — Configurar chave | Editável |

## 10 Tipos de Peça Jurídica

1. Reclamatória Trabalhista
2. Contestação
3. Réplica
4. Alegações Finais
5. Rol de Perguntas
6. Recurso Ordinário
7. Impugnação
8. Manifestação
9. Pedido de Habilitação
10. Procuração

## Calculadora Trabalhista (CLT 2026)

- 8 tipos de rescisão (sem justa causa, pedido de demissão, justa causa, rescisão indireta, culpa recíproca, acordo mútuo 484-A, término contrato, falecimento)
- Aviso prévio proporcional (Lei 12.506/2011)
- INSS progressivo 4 faixas / IRRF com dependentes
- Horas extras 50%/100% + DSR (Súmula 172 TST)
- Adicional noturno, insalubridade, periculosidade, transferência
- Férias proporcionais/vencidas/em dobro + 1/3
- FGTS + multa 40%/20% / Multas art. 477 e 467 CLT
- Seguro-desemprego / Reflexos sobre 13º, férias e FGTS
- Fundamentação legal por verba

## Biblioteca Jurídica (51 referências)

18 temas: justa causa, acidente de trabalho, danos morais, horas extras, rescisão indireta, verbas rescisórias, terceirização, equiparação salarial, prescrição, honorários, aviso prévio, correção monetária, estabilidade, insalubridade, reforma trabalhista, rito sumaríssimo, salário, vínculo.

## Integração OpenAI

Para habilitar geração de peças via GPT-4.1:
1. Clique em "API OpenAI" na sidebar
2. Insira sua chave da API (sk-...)
3. O status mudará para "IA: Conectada (GPT-4.1)"

Sem a chave, o sistema usa templates locais estruturados.

## Exportação

- **PDF** — Peças jurídicas, relatórios estratégicos e cálculos de verbas
- **CSV** — Processos e clientes (separador ;, encoding UTF-8-BOM)
- **TXT** — Peças e relatórios em texto puro

Todos os arquivos são salvos em `exports_output/`.

## Testes

```bash
python test_final.py        # 99 testes (todos os módulos)
python test_calculadora.py  # Testes específicos da calculadora
```
