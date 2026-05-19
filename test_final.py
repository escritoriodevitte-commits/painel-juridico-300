"""Teste final abrangente do Painel Jurídico Python v2"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
os.environ['DISPLAY'] = ''

passed = 0
failed = 0


def assert_(condition, msg="Assertion failed"):
    if not condition:
        raise AssertionError(msg)


def test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  [OK] {name}")
        passed += 1
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        failed += 1


print("=" * 60)
print("TESTE FINAL - PAINEL JURÍDICO PYTHON v2")
print("=" * 60)

# Limpar banco de teste
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "juridico.db")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# 1. Database
print("\n1. DATABASE")
from core.database import (
    init_db, create_cliente, get_all_clientes, get_cliente_by_id,
    update_cliente, delete_cliente, search_clientes,
    create_judge, get_all_judges, get_judge_by_id, update_judge, delete_judge,
    create_lawsuit, get_all_lawsuits, get_lawsuit_by_id, update_lawsuit, delete_lawsuit,
    get_lawsuits_by_judge, get_lawsuits_by_cliente,
    create_settlement, get_all_settlements, get_settlement_by_id, update_settlement, delete_settlement,
    create_legal_reference, get_all_legal_references, get_legal_reference_by_id,
    update_legal_reference, delete_legal_reference,
    save_generated_piece, get_generated_pieces, delete_generated_piece,
    create_negotiation_param, get_all_negotiation_params, delete_negotiation_param
)

test("init_db", lambda: init_db())

# Clientes
test("create_cliente", lambda: assert_(
    create_cliente({"nome": "Empresa Teste Ltda", "cpf": "12.345.678/0001-90",
                    "telefone": "(11) 99999-0000", "email": "teste@empresa.com",
                    "endereco": "Rua Teste, 100", "observacoes": "Cliente teste"}) >= 1))
test("get_all_clientes", lambda: assert_(len(get_all_clientes()) >= 1))
test("get_cliente_by_id", lambda: assert_(get_cliente_by_id(1) is not None))
test("update_cliente", lambda: update_cliente(1, {"nome": "Empresa Atualizada Ltda"}))
test("search_clientes", lambda: assert_(len(search_clientes("Atualizada")) >= 1))
test("delete_cliente (temp)", lambda: (
    create_cliente({"nome": "Temp"}),
    delete_cliente(2)
))

# Magistrados (coluna = name, não nome)
test("create_judge", lambda: assert_(
    create_judge({"name": "Dr. Teste Silva", "vara": "1ª Vara do Trabalho",
                  "comarca": "São Paulo", "postura_justa_causa": "Rigorosa",
                  "postura_danos_morais": "Conservadora", "observacoes": "Juiz teste"}) >= 1))
test("get_all_judges", lambda: assert_(len(get_all_judges()) >= 1))
test("get_judge_by_id", lambda: assert_(get_judge_by_id(1) is not None))
test("update_judge", lambda: update_judge(1, {"name": "Dr. Teste Atualizado"}))

# Processos
test("create_lawsuit", lambda: assert_(
    create_lawsuit({"numero_processo": "0001234-56.2025.5.02.0001", "reclamante": "João Teste",
                    "reclamada": "Empresa Teste Ltda", "vara": "1ª Vara", "status": "em_andamento",
                    "tese_inicial": "verbas_rescisorias,horas_extras", "resultado": "pendente",
                    "valor_pedido": 50000, "valor_obtido": 0,
                    "judge_id": 1, "cliente_id": 1}) >= 1))
test("get_all_lawsuits", lambda: assert_(len(get_all_lawsuits()) >= 1))
test("get_lawsuit_by_id", lambda: assert_(get_lawsuit_by_id(1) is not None))
test("update_lawsuit", lambda: update_lawsuit(1, {"status": "acordo", "valor_obtido": 15000}))
test("get_lawsuits_by_judge", lambda: assert_(len(get_lawsuits_by_judge(1)) >= 1))
test("get_lawsuits_by_cliente", lambda: assert_(len(get_lawsuits_by_cliente(1)) >= 1))

# Acordos (colunas = valor_pedido, valor_obtido)
test("create_settlement", lambda: assert_(
    create_settlement({"lawsuit_id": 1, "tipo": "acordo", "valor_pedido": 50000,
                       "valor_obtido": 15000, "parcelas": 3,
                       "data_homologacao": "2025-03-15", "observacoes": "Acordo teste"}) >= 1))
test("get_all_settlements", lambda: assert_(len(get_all_settlements()) >= 1))
test("get_settlement_by_id", lambda: assert_(get_settlement_by_id(1) is not None))
test("update_settlement", lambda: update_settlement(1, {"valor_obtido": 16000}))

# Biblioteca
test("create_legal_reference", lambda: assert_(
    create_legal_reference({"tipo": "sumula", "tema": "justa_causa", "titulo": "Súmula Teste",
                            "fonte": "TST", "trecho": "Texto teste da súmula", "ano": 2025}) >= 1))
test("get_all_legal_references", lambda: assert_(len(get_all_legal_references()) >= 1))
test("get_legal_reference_by_id", lambda: assert_(get_legal_reference_by_id(1) is not None))
test("update_legal_reference", lambda: update_legal_reference(1, {"titulo": "Súmula Teste Atualizada"}))
test("filter_by_tipo", lambda: assert_(len(get_all_legal_references(tipo="sumula")) >= 1))
test("filter_by_tema", lambda: assert_(len(get_all_legal_references(tema="justa_causa")) >= 1))

# Peças geradas
test("save_generated_piece", lambda: assert_(
    save_generated_piece(1, "contestacao", "Conteúdo teste da peça", "manual") >= 1))
test("get_generated_pieces", lambda: assert_(len(get_generated_pieces()) >= 1))
test("get_pieces_by_lawsuit", lambda: assert_(len(get_generated_pieces(lawsuit_id=1)) >= 1))
test("delete_generated_piece", lambda: (
    save_generated_piece(1, "replica", "Temp", "manual"),
    delete_generated_piece(2)
))

# Parâmetros de negociação
test("create_negotiation_param", lambda: assert_(
    create_negotiation_param({"judge_id": 1, "tema_processual": "justa_causa",
                              "valor_inicial_sugerido": 20000, "faixa_fechamento_min": 10000,
                              "faixa_fechamento_max": 30000, "estrategia_recomendada": "Acordo"}) >= 1))
test("get_all_negotiation_params", lambda: assert_(len(get_all_negotiation_params()) >= 1))
test("delete_negotiation_param", lambda: delete_negotiation_param(1))

# Delete cascata
test("delete_settlement", lambda: delete_settlement(1))
test("delete_lawsuit", lambda: delete_lawsuit(1))
test("delete_judge", lambda: delete_judge(1))
test("delete_legal_reference", lambda: delete_legal_reference(1))

# 2. Seed
print("\n2. SEED")
os.remove(DB_PATH)
init_db()
from seed import seed_legal_references
test("seed_legal_references", lambda: seed_legal_references())
refs = get_all_legal_references()
test(f"seed_count >= 50 (got {len(refs)})", lambda: assert_(len(refs) >= 50))

# Verificar temas
temas = set(r['tema'] for r in refs)
test("seed_tem_justa_causa", lambda: assert_("justa_causa" in temas))
test("seed_tem_danos_morais", lambda: assert_("danos_morais" in temas))
test("seed_tem_horas_extras", lambda: assert_("horas_extras" in temas))
test("seed_tem_verbas_rescisorias", lambda: assert_("verbas_rescisorias" in temas))
test("seed_tem_acidente_trabalho", lambda: assert_("acidente_trabalho" in temas))

# Verificar tipos
tipos = set(r['tipo'] for r in refs)
test("seed_tem_sumula", lambda: assert_("sumula" in tipos))
test("seed_tem_jurisprudencia", lambda: assert_("jurisprudencia" in tipos))

# 3. Services
print("\n3. SERVICES")
from core.services import ClienteService, ProcessoService

cs = ClienteService()
ps = ProcessoService()
test("ClienteService.criar_cliente", lambda: assert_(
    cs.criar_cliente("Teste Svc", "111.222.333-44", "(11) 1234-5678", "svc@test.com") >= 1))
test("ClienteService.buscar_por_cpf", lambda: assert_(cs.buscar_por_cpf("111.222.333-44") is not None))
test("ClienteService.resumo_cliente", lambda: assert_(cs.resumo_cliente(1) is not None))
test("ProcessoService.estatisticas_gerais", lambda: assert_(ps.estatisticas_gerais() is not None))

# 4. Analytics
print("\n4. ANALYTICS")
from modules.analytics.engine import AnalyticsEngine

# Criar dados para analytics
create_judge({"name": "Dr. Analytics", "vara": "2ª Vara", "comarca": "SP"})
for i in range(5):
    create_lawsuit({
        "numero_processo": f"000{i}-00.2025.5.02.0001", "reclamante": f"Reclamante {i}",
        "reclamada": "Empresa X", "vara": "2ª Vara", "status": "acordo",
        "tese_inicial": "verbas_rescisorias", "valor_pedido": 50000, "valor_obtido": 10000,
        "judge_id": 1, "cliente_id": 1
    })

engine = AnalyticsEngine()
test("get_dashboard_metrics", lambda: assert_(engine.get_dashboard_metrics() is not None))
test("get_prediction", lambda: assert_(engine.get_prediction(1) is not None))
test("suggest_theses", lambda: assert_(engine.suggest_theses() is not None))
test("get_risk_overview", lambda: assert_(engine.get_risk_overview() is not None))
test("get_competitive_dashboard", lambda: assert_(engine.get_competitive_dashboard() is not None))
test("get_judge_ranking", lambda: assert_(engine.get_judge_ranking() is not None))
test("get_thesis_ranking", lambda: assert_(engine.get_thesis_ranking() is not None))

# 5. Calculadora
print("\n5. CALCULADORA")
from modules.calculadora.calc import calcular_verbas, formatar_moeda

test("calc_sem_justa_causa", lambda: (
    r := calcular_verbas({"salario": 3000, "data_admissao": "2020-01-15", "data_demissao": "2025-03-20",
                          "tipo_rescisao": "sem_justa_causa"}),
    assert_(r['total_bruto'] > 0, f"Bruto: {r['total_bruto']}")
))
test("calc_pedido_demissao", lambda: (
    r := calcular_verbas({"salario": 2500, "data_admissao": "2022-06-01", "data_demissao": "2025-01-15",
                          "tipo_rescisao": "pedido_demissao"}),
    assert_(r['total_bruto'] > 0)
))
test("calc_acordo_mutuo", lambda: (
    r := calcular_verbas({"salario": 4000, "data_admissao": "2019-03-10", "data_demissao": "2025-02-28",
                          "tipo_rescisao": "acordo_mutuo"}),
    assert_(r['total_bruto'] > 0)
))
test("calc_justa_causa", lambda: (
    r := calcular_verbas({"salario": 2000, "data_admissao": "2023-01-01", "data_demissao": "2025-04-01",
                          "tipo_rescisao": "justa_causa"}),
    assert_(r['total_bruto'] >= 0)
))
test("calc_rescisao_indireta", lambda: (
    r := calcular_verbas({"salario": 3500, "data_admissao": "2021-05-01", "data_demissao": "2025-03-15",
                          "tipo_rescisao": "rescisao_indireta"}),
    assert_(r['total_bruto'] > 0)
))
test("calc_com_horas_extras", lambda: (
    r := calcular_verbas({"salario": 3500, "data_admissao": "2021-05-01", "data_demissao": "2025-03-15",
                          "tipo_rescisao": "sem_justa_causa", "horas_extras_50": 20, "horas_extras_100": 5}),
    assert_(r['total_bruto'] > 0)
))
test("calc_com_insalubridade", lambda: (
    r := calcular_verbas({"salario": 3000, "data_admissao": "2020-01-01", "data_demissao": "2025-01-01",
                          "tipo_rescisao": "sem_justa_causa", "insalubridade_grau": "medio"}),
    assert_(r['total_bruto'] > 0)
))
test("calc_com_periculosidade", lambda: (
    r := calcular_verbas({"salario": 3000, "data_admissao": "2020-01-01", "data_demissao": "2025-01-01",
                          "tipo_rescisao": "sem_justa_causa", "periculosidade": True}),
    assert_(r['total_bruto'] > 0)
))
test("formatar_moeda", lambda: assert_(formatar_moeda(1234.56) == "R$ 1.234,56"))

# 6. Gerador de Peças
print("\n6. GERADOR DE PEÇAS (10 tipos)")
from modules.ia.gerador import GeradorPecas, TIPOS_PECA

gerador = GeradorPecas()
test("gerador_init", lambda: assert_(gerador is not None))
test("TIPOS_PECA_10_tipos", lambda: assert_(len(TIPOS_PECA) == 10, f"Got {len(TIPOS_PECA)}"))

# Verificar tipos obrigatórios
for tipo_key in ["contestacao", "reclamatoria_trabalhista", "manifestacao",
                 "pedido_habilitacao", "procuracao", "replica", "alegacoes_finais",
                 "rol_perguntas", "recurso_ordinario", "impugnacao"]:
    test(f"tipo_{tipo_key}_existe", lambda tk=tipo_key: assert_(tk in TIPOS_PECA, f"{tk} não encontrado"))

processo_teste = {"numero_processo": "0001234-56.2025.5.02.0001", "reclamante": "João Silva",
                  "reclamada": "Empresa ABC Ltda", "vara": "1ª Vara do Trabalho de SP",
                  "tese_inicial": "verbas_rescisorias,horas_extras", "valor_pedido": 50000}
juiz_teste = {"name": "Dr. Teste", "vara": "1ª Vara", "postura_justa_causa": "Rigorosa",
              "postura_danos_morais": "Conservadora"}

for tipo in TIPOS_PECA:
    test(f"gerar_{tipo}", lambda t=tipo: (
        r := gerador.gerar_peca(processo_teste, juiz_teste, refs, t),
        assert_(len(r) > 100, f"Peça muito curta: {len(r)} chars")
    ))

# 7. Exportadores
print("\n7. EXPORTADORES")
from modules.exports.pdf import PDFExporter
from modules.exports.csv_export import CSVExporter

test("PDFExporter_available", lambda: assert_(PDFExporter.is_available()))
test("CSVExporter_processos", lambda: CSVExporter.exportar_processos(
    [{"id": 1, "numero_processo": "001", "reclamante": "João", "reclamada": "Emp",
      "vara": "1ª", "status": "acordo", "valor_pedido": 50000, "valor_obtido": 10000}],
    "/tmp/test_proc.csv"))
test("CSVExporter_clientes", lambda: CSVExporter.exportar_clientes(
    [{"id": 1, "nome": "Teste", "cpf": "111", "telefone": "11", "email": "t@t.com"}],
    "/tmp/test_cli.csv"))

pdf = PDFExporter()
test("PDF_exportar_peca", lambda: pdf.exportar_peca(
    "EXCELENTÍSSIMO SENHOR DOUTOR JUIZ DO TRABALHO\n\nConteúdo de teste da peça jurídica trabalhista "
    "com fundamentação legal e argumentação estratégica conforme CLT e jurisprudência do TST.",
    "contestacao",
    {"numero_processo": "001", "reclamante": "João", "reclamada": "Empresa"},
    "/tmp/test_peca.pdf"))
test("PDF_exportar_calculo", lambda: pdf.exportar_calculo(
    {"totais": {"total_bruto": 10000, "total_descontos": 500, "total_liquido": 9500, "total_fgts": 3200},
     "verbas": [{"descricao": "Saldo Salário", "valor": 2000, "fundamento": "Art. 462 CLT"}],
     "descontos": [{"descricao": "INSS", "valor": 500}]},
    "/tmp/test_calculo.pdf"))

# Verificar arquivos gerados
test("CSV_proc_exists", lambda: assert_(os.path.exists("/tmp/test_proc.csv")))
test("CSV_cli_exists", lambda: assert_(os.path.exists("/tmp/test_cli.csv")))
test("PDF_peca_exists", lambda: assert_(os.path.exists("/tmp/test_peca.pdf")))
test("PDF_calculo_exists", lambda: assert_(os.path.exists("/tmp/test_calculo.pdf")))

# 8. Syntax check main.py
print("\n8. MAIN.PY")
import ast
test("main.py_syntax_ok", lambda: ast.parse(open(
    os.path.join(os.path.dirname(__file__), 'main.py')).read()))

# Resumo
print("\n" + "=" * 60)
total = passed + failed
print(f"RESULTADO: {passed}/{total} passaram ({failed} falharam)")
print("=" * 60)

if failed > 0:
    sys.exit(1)
else:
    print("\n✅ TODOS OS TESTES PASSARAM!")
