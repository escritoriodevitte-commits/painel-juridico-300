"""
Teste end-to-end para validar o fluxo completo da aplicação
"""
import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from core import database as db
from modules.ia.gerador import GeradorPecas, TIPOS_PECA
from modules.ui.validation_integration import FormValidator

def test_database_initialization():
    """Testa inicialização do banco de dados"""
    print("=" * 70)
    print("TESTE 1: Inicialização do Banco de Dados")
    print("=" * 70)
    try:
        db.init_db()
        lawsuits = db.get_all_lawsuits()
        clients = db.get_all_clientes()
        judges = db.get_all_judges()
        refs = db.get_all_legal_references()
        
        print(f"✓ Banco de dados inicializado")
        print(f"  - Processos: {len(lawsuits)}")
        print(f"  - Clientes: {len(clients)}")
        print(f"  - Magistrados: {len(judges)}")
        print(f"  - Referências jurídicas: {len(refs)}")
        return True
    except Exception as e:
        print(f"✗ Erro ao inicializar banco: {str(e)}")
        return False

def test_gerador_initialization():
    """Testa inicialização do gerador de peças"""
    print("\n" + "=" * 70)
    print("TESTE 2: Inicialização do Gerador de Peças")
    print("=" * 70)
    try:
        gerador = GeradorPecas()
        
        # Validar atributos essenciais
        assert hasattr(gerador, 'api_key'), "Falta atributo 'api_key'"
        assert hasattr(gerador, 'model'), "Falta atributo 'model'"
        assert gerador.model == "gpt-4.1", f"Modelo incorreto: {gerador.model}"
        
        print(f"✓ Gerador inicializado com sucesso")
        print(f"  - API Key configurada: {'Sim' if gerador.api_key else 'Não'}")
        print(f"  - Modelo padrão: {gerador.model}")
        print(f"  - Cliente OpenAI disponível: {gerador.is_available()}")
        return True
    except Exception as e:
        print(f"✗ Erro ao inicializar gerador: {str(e)}")
        return False

def test_tipos_peca_structure():
    """Testa estrutura de TIPOS_PECA"""
    print("\n" + "=" * 70)
    print("TESTE 3: Estrutura de TIPOS_PECA")
    print("=" * 70)
    try:
        # Validar que TIPOS_PECA é um dicionário
        assert isinstance(TIPOS_PECA, dict), "TIPOS_PECA não é um dicionário"
        
        # Validar estrutura de cada tipo
        expected_keys = {
            'reclamatoria_trabalhista',
            'contestacao',
            'alegacoes_finais',
            'rol_perguntas',
            'recurso_ordinario',
            'impugnacao',
            'manifestacao',
            'pedido_habilitacao',
            'procuracao',
            'replica',
        }
        
        actual_keys = set(TIPOS_PECA.keys())
        assert actual_keys == expected_keys, f"Chaves incorretas: {actual_keys}"
        
        print(f"✓ TIPOS_PECA contém 10 tipos de peça:")
        for key, val in TIPOS_PECA.items():
            assert isinstance(val, dict), f"Valor de {key} não é dicionário"
            assert 'nome' in val, f"Falta 'nome' em {key}"
            print(f"  - {key:30} → {val['nome']}")
        
        return True
    except Exception as e:
        print(f"✗ Erro na validação de TIPOS_PECA: {str(e)}")
        return False

def test_gerador_update_configuration():
    """Testa atualização de configuração do gerador"""
    print("\n" + "=" * 70)
    print("TESTE 4: Atualização de Configuração do Gerador")
    print("=" * 70)
    try:
        gerador = GeradorPecas()
        
        # Testar atualização sem chave (None)
        gerador.atualizar_configuracao(None, "gpt-4o")
        assert gerador.model == "gpt-4o", f"Modelo não foi atualizado: {gerador.model}"
        assert gerador.api_key == "", "API Key deveria estar vazia"
        
        # Testar atualização com chave
        gerador.atualizar_configuracao("test_key_123", "gpt-3.5-turbo")
        assert gerador.api_key == "test_key_123", "API Key não foi atualizada"
        assert gerador.model == "gpt-3.5-turbo", "Modelo não foi atualizado"
        
        # Voltar ao padrão
        gerador.atualizar_configuracao(None, "gpt-4.1")
        assert gerador.model == "gpt-4.1", "Modelo não foi restaurado"
        
        print(f"✓ Configuração do gerador funciona corretamente")
        print(f"  - API Key: {gerador.api_key if gerador.api_key else '(vazia)'}")
        print(f"  - Modelo: {gerador.model}")
        return True
    except Exception as e:
        print(f"✗ Erro ao testar configuração: {str(e)}")
        return False

def test_form_validation():
    """Testa validação de formulários"""
    print("\n" + "=" * 70)
    print("TESTE 5: Validação de Formulários")
    print("=" * 70)
    try:
        # Teste validação de processo
        valid_processo = {
            'numero_processo': '0001234-56.2023.5.15.0098',
            'vara': 'Vara Trabalhista',
            'reclamante': 'João Silva',
            'reclamada': 'Empresa XYZ',
        }
        is_valid, msg = FormValidator.validate_processo_fields(valid_processo)
        assert is_valid, f"Processo válido foi rejeitado: {msg}"
        
        # Teste validação de cliente
        valid_cliente = {'nome': 'João da Silva'}
        is_valid, msg = FormValidator.validate_cliente_fields(valid_cliente)
        assert is_valid, f"Cliente válido foi rejeitado: {msg}"
        
        # Teste validação com dados inválidos
        invalid_processo = {'numero_processo': '', 'vara': ''}
        is_valid, msg = FormValidator.validate_processo_fields(invalid_processo)
        assert not is_valid, "Processo inválido foi aceito"
        
        print(f"✓ Validação de formulários funciona corretamente")
        print(f"  - Validação de processo: OK")
        print(f"  - Validação de cliente: OK")
        print(f"  - Rejeição de dados inválidos: OK")
        return True
    except Exception as e:
        print(f"✗ Erro na validação: {str(e)}")
        return False

def test_gerar_peca_template():
    """Testa geração de peça com template (sem OpenAI)"""
    print("\n" + "=" * 70)
    print("TESTE 6: Geração de Peça com Template Local")
    print("=" * 70)
    try:
        gerador = GeradorPecas()  # Sem chave OpenAI
        
        # Dados de exemplo
        lawsuit = {
            'numero_processo': '0001234-56.2023.5.15.0098',
            'vara': 'Vara Trabalhista do TRT-15',
            'reclamante': 'João Silva',
            'reclamada': 'Empresa XYZ Ltda',
            'valor_pedido': 50000.00,
        }
        
        judge = {
            'name': 'Juiz Carlos Santos',
            'vara': 'Vara Trabalhista',
            'tendencia_conciliatoria': 'média',
        }
        
        refs = [
            {
                'tipo': 'sumula',
                'titulo': 'Súmula 373 TST',
                'trecho': 'Texto da súmula...',
                'fonte': 'TST',
                'tema': 'justa_causa',
            }
        ]
        
        # Testar cada tipo de peça
        tipos_teste = ['reclamatoria_trabalhista', 'contestacao', 'manifestacao']
        
        for tipo in tipos_teste:
            conteudo = gerador.gerar_peca(lawsuit, judge, refs, tipo)
            assert isinstance(conteudo, str), f"Conteúdo não é string para {tipo}"
            assert len(conteudo) > 100, f"Conteúdo muito curto para {tipo}"
            print(f"  ✓ {tipo:30} - {len(conteudo)} caracteres")
        
        print(f"\n✓ Geração de peças com template funciona corretamente")
        return True
    except Exception as e:
        print(f"✗ Erro ao gerar peça: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("\n" + "=" * 70)
    print("TESTE END-TO-END - PAINEL JURÍDICO v2")
    print("=" * 70)
    
    tests = [
        test_database_initialization,
        test_gerador_initialization,
        test_tipos_peca_structure,
        test_gerador_update_configuration,
        test_form_validation,
        test_gerar_peca_template,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Teste falhou com exceção: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # Resumo
    print("\n" + "=" * 70)
    print("RESUMO DOS TESTES")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Testes passou: {passed}/{total}")
    
    if passed == total:
        print("\n✓ TODOS OS TESTES PASSARAM COM SUCESSO!")
        return 0
    else:
        print(f"\n✗ {total - passed} teste(s) falharam")
        return 1

if __name__ == "__main__":
    exit(main())
