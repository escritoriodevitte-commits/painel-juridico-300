"""
Testes abrangentes da Calculadora de Verbas Trabalhistas v2
Testa todos os tipos de rescisão, adicionais, multas e cálculos
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from modules.calculadora.calc import (
    calcular_verbas, formatar_moeda, calcular_inss, calcular_irrf,
    calcular_tempo_servico, calcular_horas_extras, calcular_insalubridade,
    calcular_periculosidade, calcular_multa_fgts, estimar_seguro_desemprego,
    calcular_aviso_previo, calcular_13_proporcional, calcular_ferias_proporcionais,
    calcular_multa_477, calcular_multa_467, calcular_dsr_sobre_horas_extras,
    calcular_adicional_noturno, calcular_salario_familia, parse_data,
    SALARIO_MINIMO_2026
)
from datetime import date

passed = 0
failed = 0

def test(name, condition):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✅ {name}")
    else:
        failed += 1
        print(f"  ❌ {name}")

print("=" * 60)
print("TESTES DA CALCULADORA TRABALHISTA v2")
print("=" * 60)

# ===== 1. FUNÇÕES AUXILIARES =====
print("\n1. Funções Auxiliares")
test("formatar_moeda(1500.50) = R$ 1.500,50", formatar_moeda(1500.50) == "R$ 1.500,50")
test("formatar_moeda(0) = R$ 0,00", formatar_moeda(0) == "R$ 0,00")
test("formatar_moeda(1234567.89)", formatar_moeda(1234567.89) == "R$ 1.234.567,89")
test("formatar_moeda(None) = R$ 0,00", formatar_moeda(None) == "R$ 0,00")

dt = parse_data("2024-06-30")
test("parse_data AAAA-MM-DD", dt == date(2024, 6, 30))
dt2 = parse_data("15/01/2020")
test("parse_data DD/MM/AAAA", dt2 == date(2020, 1, 15))

tempo = calcular_tempo_servico(date(2020, 1, 15), date(2024, 6, 30))
test("tempo_servico anos=4", tempo['anos'] == 4)
test("tempo_servico meses=5", tempo['meses'] == 5)
test("tempo_servico total_meses >= 53", tempo['total_meses'] >= 53)

# ===== 2. INSS PROGRESSIVO =====
print("\n2. INSS Progressivo 2026")
inss_sm = calcular_inss(SALARIO_MINIMO_2026)
test(f"INSS salário mínimo ({SALARIO_MINIMO_2026}) > 0", inss_sm > 0)
test(f"INSS salário mínimo = {inss_sm:.2f} (7.5%)", abs(inss_sm - SALARIO_MINIMO_2026 * 0.075) < 0.01)

inss_3000 = calcular_inss(3000)
test("INSS R$ 3.000 > INSS salário mínimo", inss_3000 > inss_sm)
test("INSS R$ 3.000 é progressivo (não 9% flat)", inss_3000 < 3000 * 0.09)

inss_10000 = calcular_inss(10000)
test("INSS R$ 10.000 respeita teto", inss_10000 == calcular_inss(8157.41))

# ===== 3. IRRF =====
print("\n3. IRRF")
irrf_isento = calcular_irrf(2000)
test("IRRF R$ 2.000 = isento", irrf_isento == 0)
irrf_5000 = calcular_irrf(5000)
test("IRRF R$ 5.000 > 0", irrf_5000 > 0)
irrf_dep = calcular_irrf(5000, 2)
test("IRRF com dependentes < sem dependentes", irrf_dep < irrf_5000)

# ===== 4. AVISO PRÉVIO =====
print("\n4. Aviso Prévio (Lei 12.506/2011)")
aviso = calcular_aviso_previo(3000, 4, 'sem_justa_causa', 'indenizado')
test("Aviso prévio 4 anos = 42 dias", aviso['dias'] == 42)
test("Aviso prévio indenizado > 0", aviso['valor'] > 0)

aviso_20 = calcular_aviso_previo(3000, 20, 'sem_justa_causa', 'indenizado')
test("Aviso prévio 20 anos = máx 90 dias", aviso_20['dias'] == 90)

aviso_jc = calcular_aviso_previo(3000, 4, 'justa_causa_empregador', 'indenizado')
test("Justa causa: sem aviso prévio", aviso_jc['valor'] == 0)

aviso_acordo = calcular_aviso_previo(3000, 4, 'acordo_mutuo', 'indenizado')
test("Acordo mútuo: metade do aviso", aviso_acordo['valor'] < aviso['valor'])
test("Acordo mútuo: ~50% do valor", abs(aviso_acordo['valor'] - aviso['valor'] * 0.5) < 1)

aviso_pd = calcular_aviso_previo(3000, 4, 'pedido_demissao', 'indenizado')
test("Pedido demissão: aviso = 30 dias fixos", aviso_pd['dias'] == 30)

# ===== 5. 13º PROPORCIONAL =====
print("\n5. 13º Salário Proporcional")
dec13 = calcular_13_proporcional(3000, 6, 'sem_justa_causa')
test("13º proporcional 6 meses = R$ 1.500", abs(dec13 - 1500) < 0.01)

dec13_jc = calcular_13_proporcional(3000, 6, 'justa_causa_empregador')
test("13º justa causa = R$ 0", dec13_jc == 0)

dec13_cr = calcular_13_proporcional(3000, 6, 'culpa_reciproca')
test("13º culpa recíproca = metade", abs(dec13_cr - 750) < 0.01)

# ===== 6. FÉRIAS =====
print("\n6. Férias Proporcionais + 1/3")
ferias = calcular_ferias_proporcionais(3000, 6, 'sem_justa_causa')
test("Férias prop. 6 meses = R$ 1.500", abs(ferias['ferias'] - 1500) < 0.01)
test("1/3 férias = R$ 500", abs(ferias['terco'] - 500) < 0.01)

ferias_jc = calcular_ferias_proporcionais(3000, 6, 'justa_causa_empregador')
test("Férias justa causa = R$ 0", ferias_jc['ferias'] == 0)

# ===== 7. FGTS =====
print("\n7. FGTS e Multa")
multa = calcular_multa_fgts(15000, 240, 'sem_justa_causa')
test("Multa FGTS 40% sem justa causa", multa['percentual'] == 40)
test("Multa FGTS valor correto", abs(multa['valor'] - (15000 + 240) * 0.40) < 0.01)

multa_acordo = calcular_multa_fgts(15000, 240, 'acordo_mutuo')
test("Multa FGTS 20% acordo mútuo", multa_acordo['percentual'] == 20)

multa_jc = calcular_multa_fgts(15000, 240, 'justa_causa_empregador')
test("Multa FGTS 0% justa causa", multa_jc['percentual'] == 0)

# ===== 8. HORAS EXTRAS =====
print("\n8. Horas Extras e DSR")
he = calcular_horas_extras(15.0, 20, 8)
test("HE 50% = 15 * 1.5 * 20 = 450", abs(he['he_50'] - 450) < 0.01)
test("HE 100% = 15 * 2.0 * 8 = 240", abs(he['he_100'] - 240) < 0.01)
test("HE total = 690", abs(he['total'] - 690) < 0.01)

dsr = calcular_dsr_sobre_horas_extras(690, 26, 4)
test("DSR sobre HE > 0", dsr > 0)
test("DSR = (690/26)*4 ≈ 106.15", abs(dsr - 106.15) < 0.01)

# ===== 9. ADICIONAIS =====
print("\n9. Adicionais")
insalub = calcular_insalubridade('maximo')
test(f"Insalubridade máx = 40% SM = {insalub['valor']}", abs(insalub['valor'] - SALARIO_MINIMO_2026 * 0.40) < 0.01)

peric = calcular_periculosidade(3000, True)
test("Periculosidade 30% = R$ 900", abs(peric['valor'] - 900) < 0.01)

noturno = calcular_adicional_noturno(15.0, 120)
test("Adicional noturno 120h = 15*0.2*120 = 360", abs(noturno['valor'] - 360) < 0.01)

# ===== 10. MULTAS =====
print("\n10. Multas CLT")
m477 = calcular_multa_477(3000, True)
test("Multa 477 = 1 salário = R$ 3.000", abs(m477 - 3000) < 0.01)

m467 = calcular_multa_467(5000, True)
test("Multa 467 = 50% verbas = R$ 2.500", abs(m467 - 2500) < 0.01)

# ===== 11. SALÁRIO-FAMÍLIA =====
print("\n11. Salário-Família")
sf = calcular_salario_familia(1518, 2)
test("Sal. família 2 filhos > 0", sf['valor'] > 0)
sf_alto = calcular_salario_familia(5000, 2)
test("Sal. família salário alto = 0", sf_alto['valor'] == 0)

# ===== 12. SEGURO-DESEMPREGO =====
print("\n12. Seguro-Desemprego")
seg = estimar_seguro_desemprego(3000, 24, 0)
test("Seguro 24 meses = 5 parcelas", seg['parcelas'] == 5)
test("Valor parcela >= SM", seg['valor_parcela'] >= SALARIO_MINIMO_2026)

seg_curto = estimar_seguro_desemprego(3000, 5, 0)
test("Seguro < 12 meses 1ª vez = 0 parcelas", seg_curto['parcelas'] == 0)

# ===== 13. CÁLCULO COMPLETO =====
print("\n13. Cálculo Completo - Sem Justa Causa")
r = calcular_verbas({
    'salario_base': 3000,
    'data_admissao': '2020-01-15',
    'data_demissao': '2024-06-30',
    'tipo_rescisao': 'sem_justa_causa',
    'aviso_previo': 'indenizado',
    'saldo_fgts': 15000,
    'horas_extras_50': 10,
    'insalubridade_grau': 'medio',
    'multa_477': True,
    'num_dependentes': 1,
})
test("Resultado tem total_bruto > 0", r['total_bruto'] > 0)
test("Resultado tem total_liquido > 0", r['total_liquido'] > 0)
test("Resultado tem verbas", len(r['verbas']) > 0)
test("Resultado tem descontos", len(r['descontos']) > 0)
test("Resultado tem fundamentação", len(r['fundamentacao']) > 0)
test("Resultado tem dados_contrato", 'dados_contrato' in r)
test("Resultado tem detalhamento", 'detalhamento' in r)
test("Saldo salário > 0", r['verbas']['saldo_salario'] > 0)
test("Aviso prévio > 0", r['verbas']['aviso_previo'] > 0)
test("13º > 0", r['verbas']['decimo_terceiro_proporcional'] > 0)
test("Férias prop. > 0", r['verbas']['ferias_proporcionais'] > 0)
test("Multa FGTS > 0", r['verbas']['multa_fgts'] > 0)
test("Multa 477 > 0", r['verbas']['multa_art_477'] > 0)
test("Insalubridade > 0", r['verbas']['insalubridade'] > 0)
test("HE > 0", r['verbas']['horas_extras'] > 0)
test("INSS > 0", r['descontos']['inss'] > 0)
test("Seguro-desemprego parcelas > 0", r['seguro_desemprego']['parcelas'] > 0)

# ===== 14. JUSTA CAUSA =====
print("\n14. Cálculo - Justa Causa")
rjc = calcular_verbas({
    'salario_base': 3000,
    'data_admissao': '2020-01-15',
    'data_demissao': '2024-06-30',
    'tipo_rescisao': 'justa_causa_empregador',
    'aviso_previo': 'nenhum',
    'saldo_fgts': 15000,
})
test("JC: aviso prévio = 0", rjc['verbas']['aviso_previo'] == 0)
test("JC: 13º = 0", rjc['verbas']['decimo_terceiro_proporcional'] == 0)
test("JC: férias prop. = 0", rjc['verbas']['ferias_proporcionais'] == 0)
test("JC: multa FGTS = 0", rjc['verbas']['multa_fgts'] == 0)
test("JC: seguro = 0 parcelas", rjc['seguro_desemprego']['parcelas'] == 0)

# ===== 15. ACORDO MÚTUO (484-A) =====
print("\n15. Cálculo - Acordo Mútuo (art. 484-A)")
ram = calcular_verbas({
    'salario_base': 3000,
    'data_admissao': '2020-01-15',
    'data_demissao': '2024-06-30',
    'tipo_rescisao': 'acordo_mutuo',
    'aviso_previo': 'indenizado',
    'saldo_fgts': 15000,
})
test("Acordo: multa FGTS 20%", ram['detalhamento']['multa_fgts']['percentual'] == 20)
test("Acordo: aviso prévio = metade", ram['verbas']['aviso_previo'] < r['verbas']['aviso_previo'])

# ===== 16. PEDIDO DE DEMISSÃO =====
print("\n16. Cálculo - Pedido de Demissão")
rpd = calcular_verbas({
    'salario_base': 3000,
    'data_admissao': '2020-01-15',
    'data_demissao': '2024-06-30',
    'tipo_rescisao': 'pedido_demissao',
    'aviso_previo': 'trabalhado',
    'saldo_fgts': 15000,
})
test("PD: multa FGTS = 0", rpd['verbas']['multa_fgts'] == 0)
test("PD: seguro = 0", rpd['seguro_desemprego']['parcelas'] == 0)
test("PD: 13º > 0", rpd['verbas']['decimo_terceiro_proporcional'] > 0)
test("PD: férias > 0", rpd['verbas']['ferias_proporcionais'] > 0)

# ===== RESUMO =====
print("\n" + "=" * 60)
total = passed + failed
print(f"RESULTADO: {passed}/{total} testes passaram")
if failed > 0:
    print(f"⚠️  {failed} teste(s) falharam")
else:
    print("✅ TODOS OS TESTES PASSARAM!")
print("=" * 60)
