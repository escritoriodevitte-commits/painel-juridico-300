"""Teste headless de todos os módulos do Painel Jurídico v2"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_database():
    print("=== Testando core/database.py ===")
    from core.database import (init_db, create_cliente, get_all_clientes, search_clientes,
                                create_lawsuit, get_all_lawsuits, create_judge, get_all_judges,
                                create_legal_reference, get_all_legal_references)
    init_db()
    # Cliente
    create_cliente({"nome": "Teste Silva", "cpf": "123.456.789-00", "telefone": "(11) 99999-0000", "email": "teste@test.com"})
    clientes = get_all_clientes()
    assert len(clientes) >= 1, f"Esperava >= 1 cliente, got {len(clientes)}"
    found = search_clientes("Teste")
    assert len(found) >= 1, "Busca de cliente falhou"
    print(f"  Clientes: {len(clientes)} | Busca 'Teste': {len(found)}")

    # Juiz
    create_judge({"name": "Juiz Teste", "vara": "1ª Vara de Teste"})
    judges = get_all_judges()
    assert len(judges) >= 1
    print(f"  Magistrados: {len(judges)}")

    # Processo
    create_lawsuit({"numero_processo": "0000001-00.2025.5.02.0001", "reclamante": "Reclamante Teste",
                     "reclamada": "Reclamada Teste", "vara": "1ª Vara", "status": "em_andamento",
                     "valor_pedido": 50000, "valor_obtido": 0, "tese_defesa": "Defesa teste",
                     "judge_id": judges[0]['id'], "cliente_id": clientes[0]['id']})
    lawsuits = get_all_lawsuits()
    assert len(lawsuits) >= 1
    print(f"  Processos: {len(lawsuits)}")

    # Referências
    refs = get_all_legal_references()
    print(f"  Referências jurídicas: {len(refs)}")
    print("  OK\n")

def test_services():
    print("=== Testando core/services.py ===")
    from core.services import ClienteService, ProcessoService
    from core.database import get_all_clientes
    clientes = get_all_clientes()
    if clientes:
        resumo = ClienteService.resumo_cliente(clientes[0]['id'])
        assert 'total_processos' in resumo
        print(f"  Resumo cliente: {resumo}")
    stats = ProcessoService.estatisticas_gerais()
    assert 'total' in stats
    print(f"  Estatísticas: {stats}")
    print("  OK\n")

def test_calculadora():
    print("=== Testando modules/calculadora ===")
    from modules.calculadora import calcular_verbas, formatar_moeda
    resultado = calcular_verbas({
        'salario_base': 3000, 'data_admissao': '2020-01-15', 'data_demissao': '2024-06-30',
        'tipo_rescisao': 'sem_justa_causa', 'aviso_previo': 'indenizado', 'saldo_fgts': 15000,
    })
    assert resultado['total_bruto'] > 0, f"Total bruto deveria ser > 0, got {resultado['total_bruto']}"
    assert resultado['total_liquido'] > 0
    print(f"  Total Bruto: {formatar_moeda(resultado['total_bruto'])}")
    print(f"  Total Líquido: {formatar_moeda(resultado['total_liquido'])}")
    print("  OK\n")

def test_analytics():
    print("=== Testando modules/analytics ===")
    from modules.analytics import AnalyticsEngine as analytics
    metrics = analytics.get_dashboard_metrics()
    assert 'total_processos' in metrics
    print(f"  Dashboard: {metrics['total_processos']} processos, {metrics['taxa_exito']}% êxito")

    pred = analytics.get_prediction()
    assert 'scores' in pred
    print(f"  Previsão score final: {pred['scores']['final']}/10")

    teses = analytics.suggest_theses()
    assert 'teses' in teses
    assert 'provas' in teses
    print(f"  Teses: {len(teses['teses'])} | Provas: {len(teses['provas'])}")

    risks = analytics.get_risk_overview()
    print(f"  Riscos: {len(risks)} processos avaliados")

    comp = analytics.get_competitive_dashboard()
    assert 'taxa_exito_geral' in comp
    print(f"  Competitiva: {comp['taxa_exito_geral']}% êxito")
    print("  OK\n")

def test_gerador():
    print("=== Testando modules/ia/gerador.py ===")
    from modules.ia import GeradorPecas
    gerador = GeradorPecas(api_key="")  # Sem API key = template local
    # Sem key válida, não deve estar disponível para IA
    print(f"  IA disponível: {gerador.is_available()}")

    from core.database import get_all_lawsuits, get_all_judges, get_all_legal_references
    lawsuits = get_all_lawsuits()
    if lawsuits:
        lawsuit = lawsuits[0]
        judge = get_all_judges()[0] if get_all_judges() else None
        refs = get_all_legal_references()
        conteudo = gerador.gerar_peca(lawsuit, judge, refs, "contestacao", "Teste de instrução")
        assert len(conteudo) > 100, f"Peça muito curta: {len(conteudo)} chars"
        print(f"  Peça gerada (template): {len(conteudo)} caracteres")
    print("  OK\n")

def test_exports():
    print("=== Testando modules/exports ===")
    from modules.exports import PDFExporter, CSVExporter, TXTExporter
    from core.database import get_all_lawsuits, get_all_clientes

    # TXT
    filepath = TXTExporter.export_piece("Teste de exportação", "teste")
    assert os.path.exists(filepath)
    print(f"  TXT exportado: {filepath}")

    # CSV
    lawsuits = get_all_lawsuits()
    if lawsuits:
        filepath = CSVExporter.export_lawsuits(lawsuits)
        assert os.path.exists(filepath)
        print(f"  CSV processos: {filepath}")

    clientes = get_all_clientes()
    if clientes:
        filepath = CSVExporter.export_clientes(clientes)
        assert os.path.exists(filepath)
        print(f"  CSV clientes: {filepath}")

    # PDF
    if PDFExporter.is_available():
        filepath = PDFExporter.export_peca("Teste de peça PDF\n\nI - DOS FATOS\nTeste de conteúdo.", "teste", "0000001")
        assert os.path.exists(filepath)
        print(f"  PDF peça: {filepath}")
    else:
        print("  PDF: ReportLab não disponível, fallback TXT")
    print("  OK\n")

def test_seed():
    print("=== Testando seed.py ===")
    from seed import run_seed
    run_seed()  # Deve ser idempotente
    from core.database import get_all_legal_references
    refs = get_all_legal_references()
    assert len(refs) >= 20, f"Esperava >= 20 refs, got {len(refs)}"
    print(f"  Biblioteca: {len(refs)} referências")
    print("  OK\n")

if __name__ == "__main__":
    print("=" * 60)
    print("  TESTES DO PAINEL JURÍDICO v2")
    print("=" * 60 + "\n")

    # Limpar banco de teste
    db_path = os.path.join(os.path.dirname(__file__), "data", "painel_juridico.db")
    if os.path.exists(db_path):
        os.remove(db_path)

    tests = [test_database, test_services, test_calculadora, test_analytics, test_gerador, test_exports, test_seed]
    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  FALHOU: {e}\n")
            failed += 1

    print("=" * 60)
    print(f"  RESULTADO: {passed} passaram, {failed} falharam de {len(tests)} testes")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)
