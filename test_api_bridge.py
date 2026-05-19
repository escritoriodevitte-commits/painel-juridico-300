#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de teste para validar a integração da API bridge com Legal AI
Testa os métodos principais do LegalAIClient
"""

import sys
import os

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(__file__))

from modules.api_bridge import LegalAIClient

def test_api_bridge():
    """Testa a integração da API bridge"""
    print("=" * 60)
    print("TESTE DA INTEGRAÇÃO - PAINEL JURÍDICO v2 COM LEGAL AI")
    print("=" * 60)
    
    # Criar cliente
    client = LegalAIClient()
    print(f"\n✓ LegalAIClient instanciado")
    print(f"  URL Base: {client.base_url}")
    print(f"  Timeout: {client.timeout}s")
    
    # Teste 1: Testar conexão
    print("\n[1] Testando conexão com servidor Legal AI...")
    try:
        connected = client.test_connection()
        if connected:
            print("  ✓ Conexão estabelecida com sucesso!")
        else:
            print("  ✗ Servidor não respondeu. Certifique-se de que Legal AI Backend está rodando em:")
            print(f"    {client.base_url}")
    except Exception as e:
        print(f"  ✗ Erro ao testar conexão: {e}")
        return False
    
    # Teste 2: Health check (se conectado)
    if connected:
        print("\n[2] Obtendo informações de saúde do servidor...")
        try:
            health = client.get_health()
            print(f"  ✓ Health Status: {health.get('status', 'desconhecido')}")
        except Exception as e:
            print(f"  ✗ Erro ao obter health: {e}")
    
    # Teste 3: Server info (se conectado)
    if connected:
        print("\n[3] Obtendo informações do servidor...")
        try:
            info = client.get_server_info()
            print(f"  ✓ Versão: {info.get('version', 'desconhecida')}")
            print(f"  ✓ Modelos Disponíveis:")
            for model in info.get('models', []):
                print(f"    - {model}")
        except Exception as e:
            print(f"  ✗ Erro ao obter info: {e}")
    
    # Teste 4: Atualizar URL
    print("\n[4] Testando mudança de URL...")
    original_url = client.base_url
    client.update_server_url("http://localhost:9000")
    print(f"  ✓ URL atualizada para: {client.base_url}")
    # Reverter
    client.update_server_url(original_url)
    print(f"  ✓ URL revertida para: {client.base_url}")
    
    # Teste 5: Listando métodos disponíveis
    print("\n[5] Métodos disponíveis no LegalAIClient:")
    methods = [m for m in dir(client) if not m.startswith('_')]
    for method in methods:
        attr = getattr(client, method)
        if callable(attr):
            print(f"  • {method}()")
    
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    print(f"Conexão com Legal AI: {'✓ OK' if connected else '✗ FALHOU'}")
    print("\nPróximos passos:")
    print("1. Iniciar Legal AI Backend (se ainda não estiver rodando)")
    print("2. Usar a aba 'Integração Legal AI' no Painel para testar funcionalidades")
    print("3. Implementar sincronização de dados conforme necessário")
    print("=" * 60)
    
    return connected

if __name__ == "__main__":
    success = test_api_bridge()
    sys.exit(0 if success else 1)
