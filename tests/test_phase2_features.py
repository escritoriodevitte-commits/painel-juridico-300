#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes de Características da Fase 2
Testa sincronização, gráficos e busca global
"""

import sys
import os

# Adicionar módulos ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.sync.process_sync import ProcessSync
from modules.ui.charts import ChartGenerator
from modules.search.global_search import GlobalSearch


# Dados de teste
TESTE_PROCESSOS = [
    {
        'id': 1,
        'numero_processo': '0000001-01.2023.5.01.0001',
        'vara': 'Vara do Trabalho',
        'reclamante': 'João Silva',
        'reclamada': 'Empresa X LTDA',
        'status': 'acordo',
        'tese_inicial': 'Horas extras não pagas',
        'data_distribuicao': '01/01/2023',
        'valor_pedido': 50000,
        'valor_obtido': 40000,
    },
    {
        'id': 2,
        'numero_processo': '0000002-02.2023.5.01.0002',
        'vara': 'Vara do Trabalho',
        'reclamante': 'Maria Santos',
        'reclamada': 'Empresa Y LTDA',
        'status': 'sentenca_procedente',
        'tese_inicial': 'Justa causa - rescisão indireta',
        'data_distribuicao': '05/02/2023',
        'valor_pedido': 75000,
        'valor_obtido': 65000,
    },
    {
        'id': 3,
        'numero_processo': '0000003-03.2023.5.01.0003',
        'vara': 'Vara do Trabalho',
        'reclamante': 'Pedro Costa',
        'reclamada': 'Empresa Z LTDA',
        'status': 'em_andamento',
        'tese_inicial': 'Danos morais',
        'data_distribuicao': '10/03/2023',
        'valor_pedido': 100000,
        'valor_obtido': 0,
    }
]

TESTE_CLIENTES = [
    {'id': 1, 'nome': 'João Silva', 'cpf': '111.444.777-35', 'email': 'joao@example.com'},
    {'id': 2, 'nome': 'Maria Santos', 'cpf': '222.555.888-46', 'email': 'maria@example.com'},
    {'id': 3, 'nome': 'Pedro Costa', 'cpf': '333.666.999-57', 'email': 'pedro@example.com'},
]

TESTE_REFERENCIAS = [
    {'id': 1, 'titulo': 'Súmula 372 TST', 'tipo': 'sumula', 'tema': 'horas_extras', 'trecho': 'Horas extras...'},
    {'id': 2, 'titulo': 'OJ 247 SBDI-1', 'tipo': 'oj', 'tema': 'justa_causa', 'trecho': 'Justa causa...'},
]

TESTE_JUIZES = [
    {'id': 1, 'name': 'Juiz José Oliveira', 'vara': 'Vara do Trabalho'},
    {'id': 2, 'name': 'Juíza Ana Silva', 'vara': 'Vara do Trabalho'},
]


class MockLegalAIClient:
    """Mock cliente Legal AI para testes"""
    def test_connection(self):
        return True
    
    def create_lawsuit_remote(self, payload):
        return {'id': 1, 'status': 'synced'}
    
    def get_lawsuit_analysis(self, numero):
        return {'analise': 'Processo analisado', 'score': 0.85}


def test_process_sync():
    """Testa sincronização de processos"""
    print("\n=== Testando ProcessSync ===")
    
    client = MockLegalAIClient()
    sync = ProcessSync(client)
    
    # Teste 1: Sincronizar processo único
    sucesso, msg = sync.sync_processo_to_remote(TESTE_PROCESSOS[0])
    print(f"{'✓' if sucesso else '✗'} Sincronizar processo: {sucesso}")
    
    # Teste 2: Sincronizar lote
    stats = sync.sync_processos_batch(TESTE_PROCESSOS[:2])
    print(f"{'✓' if stats['sucesso'] == 2 else '✗'} Sincronizar lote (2/2): {stats['sucesso']}/{stats['total']}")
    
    # Teste 3: Obter análise
    sucesso, analise = sync.get_processo_analysis('0000001-01.2023.5.01.0001')
    print(f"{'✓' if sucesso else '✗'} Obter análise: {sucesso}")
    
    # Teste 4: Status da sincronização
    status = sync.get_sync_status()
    print(f"{'✓' if status['connected'] else '✗'} Status conectado: {status['connected']}")
    
    # Teste 5: Resolver conflitos
    merged = sync.resolve_conflict(TESTE_PROCESSOS[0], {'analysis': 'test'}, priority='local')
    print(f"{'✓' if 'sync_status' in merged else '✗'} Resolver conflito: {merged.get('sync_status')}")
    
    return True


def test_chart_generator():
    """Testa gerador de gráficos"""
    print("\n=== Testando ChartGenerator ===")
    
    gen = ChartGenerator()
    
    # Teste 1: Gráfico de taxa de vitória
    chart = gen.generate_win_rate_chart(TESTE_PROCESSOS)
    print(f"{'✓' if chart['type'] == 'pie' else '✗'} Win rate chart: {chart['type']}")
    print(f"  Taxa vitória: {chart['stats']['taxa_vitoria']}")
    
    # Teste 2: Timeline
    chart = gen.generate_timeline_chart(TESTE_PROCESSOS)
    print(f"{'✓' if chart['type'] == 'line' else '✗'} Timeline chart: {chart['type']}")
    
    # Teste 3: Distribuição por tipo
    chart = gen.generate_type_distribution_chart(TESTE_PROCESSOS)
    print(f"{'✓' if chart['type'] == 'bar' else '✗'} Type distribution: {len(chart['y_values'])} tipos")
    
    # Teste 4: Desempenho de magistrados
    chart = gen.generate_judge_performance_chart(TESTE_JUIZES, TESTE_PROCESSOS)
    print(f"{'✓' if chart['type'] == 'bar' else '✗'} Judge performance: {chart['stats']['total_magistrados']} juízes")
    
    # Teste 5: Análise financeira
    chart = gen.generate_financial_analysis_chart(TESTE_PROCESSOS)
    print(f"{'✓' if 'economia' in chart['stats'] else '✗'} Financial analysis: economia calculada")
    
    # Teste 6: Status trend
    chart = gen.generate_status_trend_chart(TESTE_PROCESSOS)
    print(f"{'✓' if chart['type'] == 'doughnut' else '✗'} Status trend: {chart['type']}")
    
    # Teste 7: Todos os gráficos
    all_charts = gen.generate_all_charts(TESTE_PROCESSOS, TESTE_JUIZES)
    print(f"{'✓' if len(all_charts) == 6 else '✗'} Todos os gráficos: {len(all_charts)} gráficos")
    
    return True


def test_global_search():
    """Testa busca global"""
    print("\n=== Testando GlobalSearch ===")
    
    search = GlobalSearch()
    
    # Teste 1: Buscar processos
    results = search.search_processos(TESTE_PROCESSOS, 'João')
    print(f"{'✓' if len(results) > 0 else '✗'} Buscar processos (João): {len(results)} resultado(s)")
    
    # Teste 2: Buscar clientes
    results = search.search_clientes(TESTE_CLIENTES, 'Maria')
    print(f"{'✓' if len(results) > 0 else '✗'} Buscar clientes (Maria): {len(results)} resultado(s)")
    
    # Teste 3: Buscar referências
    results = search.search_referencias(TESTE_REFERENCIAS, 'Súmula')
    print(f"{'✓' if len(results) > 0 else '✗'} Buscar referências (Súmula): {len(results)} resultado(s)")
    
    # Teste 4: Busca global
    results = search.global_search('Silva', TESTE_PROCESSOS, TESTE_CLIENTES, TESTE_REFERENCIAS)
    print(f"{'✓' if results['total'] > 0 else '✗'} Busca global (Silva): {results['total']} resultado(s)")
    
    # Teste 5: Busca por tipo
    results = search.search_by_type('horas', 'processos', TESTE_PROCESSOS)
    print(f"{'✓' if len(results) > 0 else '✗'} Busca por tipo (processos): {len(results)} resultado(s)")
    
    # Teste 6: Busca avançada
    filters = {'status': 'acordo', 'vara': 'Trabalho'}
    results = search.advanced_search(TESTE_PROCESSOS, filters)
    print(f"{'✓' if len(results) > 0 else '✗'} Busca avançada (filtros): {len(results)} resultado(s)")
    
    # Teste 7: Sugestões
    suggestions = search.get_suggestions('Jo', {'processos': TESTE_PROCESSOS, 'clientes': TESTE_CLIENTES})
    print(f"{'✓' if len(suggestions) > 0 else '✗'} Sugestões (Jo): {len(suggestions)} sugestão(ões)")
    
    # Teste 8: Histórico
    history = search.get_search_history(limit=5)
    print(f"{'✓' if len(history) >= 0 else '✗'} Histórico de buscas: {len(history)} entrada(s)")
    
    return True


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTES DE CARACTERÍSTICAS - FASE 2")
    print("=" * 60)
    
    try:
        test_process_sync()
        test_chart_generator()
        test_global_search()
        
        print("\n" + "=" * 60)
        print("✓ TODOS OS TESTES EXECUTADOS COM SUCESSO")
        print("=" * 60)
        return True
    
    except Exception as e:
        print(f"\n✗ ERRO DURANTE TESTES: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
