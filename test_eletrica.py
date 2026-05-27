#!/usr/bin/env python3
"""Testes da ferramenta de cálculos elétricos para painéis industriais."""
import math

from modules.eletrica.calc import (
    corrente_nominal,
    corrente_motor,
    potencia_trifasica,
    dimensionar_disjuntor,
    dimensionar_contator,
    corrente_curto_circuito,
    dimensionar_condutor,
    queda_tensao,
    secao_minima_por_queda,
    corrigir_fator_potencia,
)


def quase_igual(a, b, tol=0.01):
    return abs(a - b) <= tol * max(1.0, abs(b))


def test_corrente_nominal():
    # 380 V trifásico, fp 1, 10 kW -> I = 10000 / (raiz3*380) ≈ 15.19 A
    i = corrente_nominal(10000, 380, trifasico=True, fator_potencia=1.0)
    assert quase_igual(i, 10000 / (math.sqrt(3) * 380)), i
    # monofásico 220 V, fp 1, 2200 W -> 10 A
    i = corrente_nominal(2200, 220, trifasico=False, fator_potencia=1.0)
    assert quase_igual(i, 10.0), i


def test_corrente_motor():
    r = corrente_motor(10, 380, trifasico=True, rendimento=0.88, fator_potencia=0.85)
    assert quase_igual(r["potencia_mecanica_w"], 7355), r
    # potência elétrica = 7355 / 0.88 ≈ 8358 W
    assert quase_igual(r["potencia_eletrica_w"], 7355 / 0.88), r
    esperado = (7355 / 0.88) / (math.sqrt(3) * 380 * 0.85)
    assert quase_igual(r["corrente_nominal_a"], esperado), r


def test_potencia_trifasica():
    r = potencia_trifasica(380, 15.19, fator_potencia=0.92)
    assert r["potencia_aparente_va"] > r["potencia_ativa_w"] > 0
    # S² = P² + Q²
    s2 = r["potencia_ativa_w"] ** 2 + r["potencia_reativa_var"] ** 2
    assert quase_igual(math.sqrt(s2), r["potencia_aparente_va"], tol=0.02)


def test_dimensionar_disjuntor():
    # 20 A * 1.25 = 25 A -> disjuntor de 25 A
    r = dimensionar_disjuntor(20)
    assert r["disjuntor_a"] == 25, r
    # 20 A * 1.25 = 25 -> exatamente 25 atende; 21 A -> 26.25 -> 32 A
    assert dimensionar_disjuntor(21)["disjuntor_a"] == 32


def test_dimensionar_contator():
    assert dimensionar_contator(20)["contator_ac3_a"] == 25
    assert dimensionar_contator(9)["contator_ac3_a"] == 9


def test_corrente_curto_circuito():
    # trafo 500 kVA, 380 V, Z 4.5%
    r = corrente_curto_circuito(500, 380, 4.5)
    in_a = 500000 / (math.sqrt(3) * 380)
    assert quase_igual(r["corrente_nominal_trafo_a"], in_a), r
    assert quase_igual(r["icc_simetrica_a"], in_a / 0.045, tol=0.01), r
    assert quase_igual(r["icc_simetrica_ka"], (in_a / 0.045) / 1000, tol=0.01)


def test_dimensionar_condutor():
    # 76 A cabe em 16 mm² (ampacidade 76 A) sem fator de correção
    r = dimensionar_condutor(76)
    assert r["secao_mm2"] == 16, r
    # com fator 0.8 -> corrente corrigida 95 A -> precisa de 25 mm² (101 A)
    r = dimensionar_condutor(76, fator_correcao=0.8)
    assert r["secao_mm2"] == 25, r


def test_queda_tensao():
    # trifásico, cobre, 30 A, 50 m, 6 mm², 380 V
    r = queda_tensao(30, 50, 6, 380, trifasico=True, material="cobre")
    esperado = math.sqrt(3) * 0.0178 * 50 * 30 / 6
    assert quase_igual(r["queda_v"], esperado, tol=0.02), r
    assert quase_igual(r["tensao_no_uso_v"], 380 - r["queda_v"], tol=0.02)
    assert isinstance(r["dentro_limite"], bool)


def test_secao_minima_por_queda():
    r = secao_minima_por_queda(30, 50, 380, queda_max_percent=4.0)
    # a seção comercial escolhida deve, de fato, respeitar o limite
    verificacao = queda_tensao(30, 50, r["secao_comercial_mm2"], 380)
    assert verificacao["queda_percent"] <= 4.0, (r, verificacao)


def test_corrigir_fator_potencia():
    # 50 kW, fp 0.78 -> 0.92
    r = corrigir_fator_potencia(50000, 0.78, 0.92)
    esperado = 50000 * (math.tan(math.acos(0.78)) - math.tan(math.acos(0.92))) / 1000
    assert quase_igual(r["potencia_reativa_capacitiva_kvar"], esperado, tol=0.02), r


def _rodar():
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    falhas = 0
    for t in testes:
        try:
            t()
            print(f"  ✓ {t.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f"  ✗ {t.__name__}: {e}")
    print("=" * 60)
    if falhas:
        print(f"{falhas} de {len(testes)} testes FALHARAM")
        return 1
    print(f"✓ TODOS OS {len(testes)} TESTES PASSARAM")
    return 0


if __name__ == "__main__":
    import sys
    print("=" * 60)
    print("TESTES — FERRAMENTA ELETRICISTA DE PAINEL INDUSTRIAL")
    print("=" * 60)
    sys.exit(_rodar())
