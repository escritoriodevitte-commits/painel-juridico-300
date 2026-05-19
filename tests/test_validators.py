#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes para os módulos de validação
Testa DateValidator, NumberValidator e DocumentValidator
"""

import sys
import os

# Adicionar módulos ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.validators.date_validator import DateValidator
from modules.validators.number_validator import NumberValidator
from modules.validators.document_validator import DocumentValidator


def test_date_validator():
    """Testa DateValidator"""
    print("\n=== Testando DateValidator ===")
    validator = DateValidator()
    
    # Test validate_date
    tests = [
        ("25/12/2023", True, "Data válida"),
        ("31/02/2023", False, "Data inválida - fevereiro não tem 31"),
        ("32/01/2023", False, "Dia inválido"),
        ("25/13/2023", False, "Mês inválido"),
    ]
    
    for date, expected, desc in tests:
        result, msg = validator.validate_date(date, allow_future=False)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc}: {date} -> {result}")
    
    result, msg = validator.validate_date("25/12/2050", allow_future=False)
    print(f"{'✓' if not result else '✗'} Data futura bloqueada: 25/12/2050 -> {result}")
    
    result, msg = validator.validate_date("25/12/2050", allow_future=True)
    print(f"{'✓' if result else '✗'} Data futura permitida: 25/12/2050 -> {result}")
    
    # Test date_range
    result, msg = validator.validate_date_range("01/01/2023", "31/12/2023")
    print(f"{'✓' if result else '✗'} Range válido: 01/01/2023 - 31/12/2023")
    
    result, msg = validator.validate_date_range("31/12/2023", "01/01/2023")
    print(f"{'✓' if not result else '✗'} Range inválido (invertido)")
    
    return True


def test_number_validator():
    """Testa NumberValidator"""
    print("\n=== Testando NumberValidator ===")
    validator = NumberValidator()
    
    # Test validate_currency
    tests = [
        ("R$ 1.000,00", True, "Moeda brasileira válida"),
        ("R$ 100,50", True, "Moeda com decimais"),
        ("R$ 1000,00", True, "Moeda sem separador de milhares"),
        ("1.000,00", True, "Moeda sem símbolo R$"),
    ]
    
    for currency, expected, desc in tests:
        result, msg = validator.validate_currency(currency)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc}: {currency} -> {result}")
    
    # Test parse_currency
    result = validator.parse_currency("R$ 1.234,56")
    print(f"{'✓' if result == 1234.56 else '✗'} Parse R$ 1.234,56 -> {result}")
    
    # Test format_currency
    result = validator.format_currency(1234.56)
    print(f"{'✓' if result == 'R$ 1.234,56' else '✗'} Format 1234.56 -> {result}")
    
    # Test validate_percentage
    tests_pct = [
        (50, True, "Porcentagem válida"),
        (150, False, "Porcentagem > 100"),
        (-10, False, "Porcentagem negativa"),
    ]
    
    for pct, expected, desc in tests_pct:
        result, msg = validator.validate_percentage(pct)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc}: {pct}% -> {result}")
    
    return True


def test_document_validator():
    """Testa DocumentValidator"""
    print("\n=== Testando DocumentValidator ===")
    validator = DocumentValidator()
    
    # CPF válido
    valid_cpf = "111.444.777-35"
    result, msg = validator.validate_cpf(valid_cpf)
    print(f"{'✓' if result else '✗'} CPF válido: {valid_cpf} -> {result}")
    
    # CPF inválido
    invalid_cpf = "000.000.000-00"
    result, msg = validator.validate_cpf(invalid_cpf)
    print(f"{'✓' if not result else '✗'} CPF inválido (sequência igual): {invalid_cpf} -> {result == False}")
    
    # CPF inválido por dígito verificador
    wrong_cpf = "12345678901"  # Sem formatação
    result, msg = validator.validate_cpf(wrong_cpf)
    print(f"{'✓' if not result else '✗'} CPF inválido por dígito: {wrong_cpf} -> {result}")
    
    # CNPJ válido
    test_cnpj = "11.222.333/0001-81"
    result, msg = validator.validate_cnpj(test_cnpj)
    print(f"{'✓' if result else '✗'} CNPJ válido: {test_cnpj} -> {result}")
    
    # CNPJ inválido
    invalid_cnpj = "00.000.000/0000-00"
    result, msg = validator.validate_cnpj(invalid_cnpj)
    print(f"{'✓' if not result else '✗'} CNPJ inválido (sequência igual): {invalid_cnpj} -> {result == False}")
    
    # Test formatting
    cpf_fmt = validator.format_cpf("12345678909")
    print(f"{'✓' if cpf_fmt == '123.456.789-09' else '✗'} Format CPF: {cpf_fmt}")
    
    cnpj_fmt = validator.format_cnpj("12345678000190")
    print(f"{'✓' if cnpj_fmt == '12.345.678/0001-90' else '✗'} Format CNPJ: {cnpj_fmt}")
    
    return True


def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("TESTES DE VALIDADORES - FASE 2")
    print("=" * 60)
    
    try:
        test_date_validator()
        test_number_validator()
        test_document_validator()
        
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
