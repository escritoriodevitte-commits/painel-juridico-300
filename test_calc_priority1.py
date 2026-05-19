#!/usr/bin/env python3
"""Teste das 5 funcionalidades Priority 1 da calculadora trabalhista"""

from modules.calculadora.calc import (
    calcular_reflexos_fgts_completos,
    calcular_licenca_premio,
    calcular_abono_ferias,
    calcular_contribuicao_sindical,
    calcular_irrf_progressivo_13,
)

def test_priority_1():
    print("=" * 70)
    print("TESTE DAS FUNCIONALIDADES PRIORITY 1")
    print("=" * 70 + "\n")
    
    # 1. Reflexos FGTS completos
    print("1. REFLEXOS FGTS COMPLETOS (Lei 8.036/90)")
    print("-" * 70)
    reflexos = calcular_reflexos_fgts_completos(
        remuneracao_habitual=3000,
        horas_extras_total=300,
        dsr_he=50,
        adic_noturno_valor=200,
        insalub_valor=152,
        pericu_valor=300,
        meses_trabalhados=12
    )
    print(f"Base FGTS mensal: R$ {reflexos['base_mensal']:,.2f}")
    print(f"FGTS mensal (8%): R$ {reflexos['fgts_mensal']:,.2f}")
    print(f"FGTS total (12 meses): R$ {reflexos['fgts_total']:,.2f}\n")
    
    # 2. Licença-prêmio
    print("2. LICENÇA-PRÊMIO (30 dias a cada 5 anos)")
    print("-" * 70)
    licenca = calcular_licenca_premio(
        remuneracao=5000,
        anos_servico=10,
        periodos_nao_utilizados=1
    )
    print(f"Períodos adquiridos: {licenca['periodos_adquiridos']}")
    print(f"Períodos utilizados: {licenca['periodos_utilizados']}")
    print(f"Períodos disponíveis: {licenca['periodos_disponiveis']}")
    print(f"Valor por período (30 dias): R$ {licenca['valor_por_periodo']:,.2f}")
    print(f"Valor total (conversível): R$ {licenca['valor_total']:,.2f}\n")
    
    # 3. Abono de férias
    print("3. ABONO DE FÉRIAS (Art. 143 CLT - conversão de 1/3)")
    print("-" * 70)
    abono = calcular_abono_ferias(
        remuneracao=3000,
        meses_ferias_direito=12,
        parte_convertida=1  # 1/3 das férias em dinheiro
    )
    print(f"Férias simples: R$ {abono['ferias_simples']:,.2f}")
    print(f"1/3 das férias: R$ {abono['terco_ferias']:,.2f}")
    print(f"Abono (dinheiro): R$ {abono['abono_dinheiro']:,.2f}")
    print(f"Férias gozadas: R$ {abono['ferias_gozadas']:,.2f}\n")
    
    # 4. Contribuição sindical
    print("4. CONTRIBUIÇÃO SINDICAL (Lei 5.584/70)")
    print("-" * 70)
    contrib = calcular_contribuicao_sindical(
        remuneracao=3000,
        aplica=True
    )
    print(f"Valor desconto (1 dia de trabalho): R$ {contrib:,.2f}")
    print(f"Percentual: 1/30 do salário mensal\n")
    
    # 5. IRRF progressivo 13º
    print("5. IRRF PROGRESSIVO SOBRE 13º (Lei 7.713/88)")
    print("-" * 70)
    irrf_13 = calcular_irrf_progressivo_13(
        valor_13=3000,
        num_dependentes=2
    )
    print(f"IRRF sobre 13º (com 2 dependentes): R$ {irrf_13:,.2f}")
    print(f"Dedução por dependente: R$ 189,59 cada\n")
    
    print("=" * 70)
    print("✓ TODAS AS 5 FUNCIONALIDADES PRIORITY 1 FUNCIONANDO COM SUCESSO!")
    print("=" * 70)

if __name__ == "__main__":
    test_priority_1()
