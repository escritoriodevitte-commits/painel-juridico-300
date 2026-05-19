#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes de Integração de Validadores com Formulários
Testa FormValidator e validações de campos de formulários
"""

import sys
import os

# Adicionar módulos ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.ui.validation_integration import FormValidator


def test_processo_validation():
    """Testa validação de processo"""
    print("\n=== Testando Validação de Processo ===")
    
    # Válido
    data = {
        'numero_processo': '0000001-01.2023.5.01.0001',
        'vara': 'Vara do Trabalho',
        'reclamante': 'João Silva',
        'reclamada': 'Empresa X LTDA',
        'data_distribuicao': '01/01/2023',
        'data_encerramento': '31/12/2023',
        'valor_pedido': '10000,00',
        'valor_obtido': '8000,00',
    }
    result, msg = FormValidator.validate_processo_fields(data)
    print(f"{'✓' if result else '✗'} Processo válido: {result}")
    
    # Falta obrigatórios
    data_invalid = {
        'numero_processo': '0000001-01.2023.5.01.0001',
        'vara': 'Vara do Trabalho',
    }
    result, msg = FormValidator.validate_processo_fields(data_invalid)
    print(f"{'✓' if not result else '✗'} Processo inválido (faltam campos): {result}")
    
    # Data inválida
    data_bad_date = {
        'numero_processo': '0000001-01.2023.5.01.0001',
        'vara': 'Vara do Trabalho',
        'reclamante': 'João Silva',
        'reclamada': 'Empresa X LTDA',
        'data_distribuicao': '32/01/2023',  # Inválido
    }
    result, msg = FormValidator.validate_processo_fields(data_bad_date)
    print(f"{'✓' if not result else '✗'} Data inválida bloqueada: {result}")
    
    # Datas invertidas
    data_inverted = {
        'numero_processo': '0000001-01.2023.5.01.0001',
        'vara': 'Vara do Trabalho',
        'reclamante': 'João Silva',
        'reclamada': 'Empresa X LTDA',
        'data_distribuicao': '31/12/2023',
        'data_encerramento': '01/01/2023',  # Antes da distribuição
    }
    result, msg = FormValidator.validate_processo_fields(data_inverted)
    print(f"{'✓' if not result else '✗'} Datas invertidas bloqueadas: {result}")
    
    return True


def test_cliente_validation():
    """Testa validação de cliente"""
    print("\n=== Testando Validação de Cliente ===")
    
    # Válido
    data = {
        'nome': 'João da Silva',
        'cpf': '111.444.777-35',
        'email': 'joao@example.com',
        'telefone': '11987654321',
    }
    result, msg = FormValidator.validate_cliente_fields(data)
    print(f"{'✓' if result else '✗'} Cliente válido: {result}")
    
    # Falta nome
    data_invalid = {
        'cpf': '111.444.777-35',
    }
    result, msg = FormValidator.validate_cliente_fields(data_invalid)
    print(f"{'✓' if not result else '✗'} Cliente sem nome bloqueado: {result}")
    
    # CPF inválido
    data_bad_cpf = {
        'nome': 'João da Silva',
        'cpf': '000.000.000-00',
    }
    result, msg = FormValidator.validate_cliente_fields(data_bad_cpf)
    print(f"{'✓' if not result else '✗'} CPF inválido bloqueado: {result}")
    
    # Email inválido
    data_bad_email = {
        'nome': 'João da Silva',
        'email': 'email_invalido',
    }
    result, msg = FormValidator.validate_cliente_fields(data_bad_email)
    print(f"{'✓' if not result else '✗'} Email inválido bloqueado: {result}")
    
    return True


def test_acordo_validation():
    """Testa validação de acordo"""
    print("\n=== Testando Validação de Acordo ===")
    
    # Válido
    data = {
        'tipo': 'acordo',
        'valor_pedido': '10000,00',
        'valor_obtido': '8000,00',
        'data_homologacao': '15/06/2023',
    }
    result, msg = FormValidator.validate_acordo_fields(data)
    print(f"{'✓' if result else '✗'} Acordo válido: {result}")
    
    # Falta tipo
    data_invalid = {
        'valor_pedido': '10000,00',
    }
    result, msg = FormValidator.validate_acordo_fields(data_invalid)
    print(f"{'✓' if not result else '✗'} Acordo sem tipo bloqueado: {result}")
    
    # Valor obtido > pedido
    data_bad_value = {
        'tipo': 'acordo',
        'valor_pedido': '8000,00',
        'valor_obtido': '10000,00',  # Maior que pedido
    }
    result, msg = FormValidator.validate_acordo_fields(data_bad_value)
    print(f"{'✓' if not result else '✗'} Valor obtido > pedido bloqueado: {result}")
    
    return True


def test_field_validation():
    """Testa validação de campos individuais"""
    print("\n=== Testando Validação de Campos Individuais ===")
    
    # Data válida
    result, msg = FormValidator.validate_field('date', '25/12/2023')
    print(f"{'✓' if result else '✗'} Data válida: {result}")
    
    # Moeda válida
    result, msg = FormValidator.validate_field('currency', 'R$ 1.000,00')
    print(f"{'✓' if result else '✗'} Moeda válida: {result}")
    
    # CPF válido
    result, msg = FormValidator.validate_field('cpf', '111.444.777-35')
    print(f"{'✓' if result else '✗'} CPF válido: {result}")
    
    # Email válido
    result, msg = FormValidator.validate_field('email', 'teste@example.com')
    print(f"{'✓' if result else '✗'} Email válido: {result}")
    
    # Telefone válido
    result, msg = FormValidator.validate_field('phone', '11987654321')
    print(f"{'✓' if result else '✗'} Telefone válido: {result}")
    
    return True


def test_field_formatting():
    """Testa formatação de campos"""
    print("\n=== Testando Formatação de Campos ===")
    
    # Moeda
    result = FormValidator.format_for_display('currency', '1000.50')
    expected = 'R$ 1.000,50'
    print(f"{'✓' if result == expected else '✗'} Moeda formatada: {result}")
    
    # CPF
    result = FormValidator.format_for_display('cpf', '12345678909')
    expected = '123.456.789-09'
    print(f"{'✓' if result == expected else '✗'} CPF formatado: {result}")
    
    # CNPJ
    result = FormValidator.format_for_display('cnpj', '12345678000190')
    expected = '12.345.678/0001-90'
    print(f"{'✓' if result == expected else '✗'} CNPJ formatado: {result}")
    
    return True


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTES DE INTEGRAÇÃO - FASE 2")
    print("=" * 60)
    
    try:
        test_processo_validation()
        test_cliente_validation()
        test_acordo_validation()
        test_field_validation()
        test_field_formatting()
        
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
