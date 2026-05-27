#!/usr/bin/env python3
"""Testes da calculadora de periculosidade do eletricista (cálculo trabalhista)."""

from modules.periculosidade.calc import (
    calcular_adicional,
    calcular_reflexos,
    calcular_retroativo,
    PERCENTUAL_PERICULOSIDADE,
    PRESCRICAO_MESES,
)


def quase_igual(a, b, tol=0.01):
    return abs(a - b) <= tol


def test_adicional():
    # 30% de 2500 = 750
    assert calcular_adicional(2500) == 750.0
    assert calcular_adicional(0) == 0.0
    # percentual customizado
    assert calcular_adicional(1000, percentual=0.30) == 300.0


def test_adicional_invalido():
    try:
        calcular_adicional(-1)
        assert False, "deveria lançar ValueError"
    except ValueError:
        pass


def test_reflexos():
    adic = calcular_adicional(2500)  # 750/mês
    r = calcular_reflexos(adic, incluir_fgts=True)
    assert r["adicional_ano"] == 9000.0, r          # 750 * 12
    assert r["decimo_terceiro"] == 750.0, r
    assert r["ferias"] == 750.0, r
    assert quase_igual(r["terco_ferias"], 250.0), r  # 750/3
    # FGTS 8% sobre (9000 + 750 + 750 + 250) = 10750 -> 860
    assert quase_igual(r["fgts"], 860.0), r
    assert quase_igual(r["subtotal_anual"], 11610.0), r


def test_reflexos_sem_fgts():
    adic = calcular_adicional(2500)
    r = calcular_reflexos(adic, incluir_fgts=False)
    assert r["fgts"] == 0.0
    assert quase_igual(r["subtotal_anual"], 9000 + 750 + 750 + 250)


def test_retroativo_dentro_prescricao():
    r = calcular_retroativo(2500, 36)
    assert r["meses_devidos"] == 36
    assert r["meses_prescritos"] == 0
    assert r["adicional_periodo"] == 750.0 * 36
    # reflexos proporcionais a 3 anos
    assert quase_igual(r["reflexo_13"], 750.0 * 3)
    assert quase_igual(r["reflexo_ferias"], 750.0 * 3)
    assert quase_igual(r["reflexo_terco_ferias"], 250.0 * 3)
    assert r["total_devido"] > r["adicional_periodo"]
    assert "dentro da prescrição" in r["observacao"]


def test_retroativo_com_prescricao():
    r = calcular_retroativo(2500, 72)
    assert r["meses_devidos"] == PRESCRICAO_MESES  # limitado a 60
    assert r["meses_prescritos"] == 12
    assert r["adicional_periodo"] == 750.0 * 60
    assert "prescrito" in r["observacao"]


def test_retroativo_invalido():
    try:
        calcular_retroativo(2500, 0)
        assert False, "deveria lançar ValueError"
    except ValueError:
        pass


def test_percentual_constante():
    assert PERCENTUAL_PERICULOSIDADE == 0.30


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
    print("TESTES — PERICULOSIDADE DO ELETRICISTA (CÁLCULO TRABALHISTA)")
    print("=" * 60)
    sys.exit(_rodar())
