"""
Ferramenta para Eletricista de Painel Eletrônico Industrial.

Cálculos elétricos de dimensionamento e proteção para montagem e
manutenção de painéis industriais, com base na NBR 5410 e práticas
usuais de mercado (cobre, isolação PVC).

Módulo puro (somente biblioteca padrão) — sem dependências externas.
Todas as funções retornam valores em unidades SI usuais:
corrente em A, tensão em V, potência em W (ou kW quando indicado),
seção em mm².
"""
import math

# ==================== TABELAS DE REFERÊNCIA ====================

# Disjuntores - correntes nominais comerciais (IEC 60898 / linha industrial), em A
DISJUNTORES_PADRAO = [
    6, 10, 16, 20, 25, 32, 40, 50, 63, 70, 80, 100,
    125, 160, 200, 250, 320, 400, 500, 630, 800, 1000, 1250, 1600,
]

# Contatores - corrente de emprego AC-3 (uso em motores), em A
CONTATORES_AC3 = [9, 12, 18, 25, 32, 38, 40, 50, 65, 80, 95, 115, 150, 185, 225, 265, 330, 400, 500, 630]

# Capacidade de condução de corrente (ampacidade) - cobre, isolação PVC,
# método de referência B1, 3 condutores carregados, ~30 °C. NBR 5410 (A).
AMPACIDADE_CU_PVC_B1 = {
    1.5: 17.5, 2.5: 24, 4: 32, 6: 41, 10: 57, 16: 76, 25: 101,
    35: 125, 50: 151, 70: 192, 95: 232, 120: 269, 150: 309,
    185: 353, 240: 415, 300: 477,
}

# Resistividade dos condutores (ohm·mm²/m) a ~70 °C de operação
RESISTIVIDADE = {"cobre": 0.0178, "aluminio": 0.0282}

# Limites de queda de tensão recomendados (NBR 5410), em %
QUEDA_MAX_TERMINAL = 4.0   # circuitos terminais
QUEDA_MAX_MOTOR_PARTIDA = 10.0  # partida de motores


def _sqrt3():
    return math.sqrt(3)


# ==================== CORRENTE ====================

def corrente_nominal(potencia_w, tensao_v, trifasico=True, fator_potencia=0.92):
    """Corrente nominal de uma carga resistiva/indutiva genérica.

    potencia_w: potência ativa em W.
    Retorna a corrente em A.
    """
    if tensao_v <= 0 or fator_potencia <= 0:
        raise ValueError("tensão e fator de potência devem ser positivos")
    if trifasico:
        return potencia_w / (_sqrt3() * tensao_v * fator_potencia)
    return potencia_w / (tensao_v * fator_potencia)


def corrente_motor(potencia_cv, tensao_v, trifasico=True, rendimento=0.88,
                   fator_potencia=0.85):
    """Corrente nominal de um motor a partir da potência mecânica.

    potencia_cv: potência no eixo em CV (1 CV = 735,5 W).
    rendimento: rendimento do motor (0-1).
    Retorna dict com potência elétrica e corrente nominal.
    """
    if not (0 < rendimento <= 1):
        raise ValueError("rendimento deve estar entre 0 e 1")
    potencia_mecanica_w = potencia_cv * 735.5
    potencia_eletrica_w = potencia_mecanica_w / rendimento
    if trifasico:
        corrente = potencia_eletrica_w / (_sqrt3() * tensao_v * fator_potencia)
    else:
        corrente = potencia_eletrica_w / (tensao_v * fator_potencia)
    return {
        "potencia_mecanica_w": round(potencia_mecanica_w, 1),
        "potencia_eletrica_w": round(potencia_eletrica_w, 1),
        "corrente_nominal_a": round(corrente, 2),
    }


def potencia_trifasica(tensao_v, corrente_a, fator_potencia=0.92):
    """Potências aparente (VA), ativa (W) e reativa (VAr) de carga trifásica."""
    s = _sqrt3() * tensao_v * corrente_a
    p = s * fator_potencia
    q = s * math.sqrt(max(0.0, 1 - fator_potencia ** 2))
    return {
        "potencia_aparente_va": round(s, 1),
        "potencia_ativa_w": round(p, 1),
        "potencia_reativa_var": round(q, 1),
    }


# ==================== PROTEÇÃO ====================

def dimensionar_disjuntor(corrente_projeto_a, fator_seguranca=1.25):
    """Seleciona o disjuntor comercial imediatamente acima da corrente exigida.

    Aplica fator de segurança (padrão 1,25 para circuitos contínuos / motores).
    Retorna dict com corrente exigida e disjuntor selecionado.
    """
    if corrente_projeto_a <= 0:
        raise ValueError("corrente de projeto deve ser positiva")
    corrente_exigida = corrente_projeto_a * fator_seguranca
    for nominal in DISJUNTORES_PADRAO:
        if nominal >= corrente_exigida:
            return {
                "corrente_projeto_a": round(corrente_projeto_a, 2),
                "corrente_exigida_a": round(corrente_exigida, 2),
                "disjuntor_a": nominal,
            }
    raise ValueError(
        f"corrente exigida {corrente_exigida:.1f} A acima do maior disjuntor "
        f"tabelado ({DISJUNTORES_PADRAO[-1]} A)"
    )


def dimensionar_contator(corrente_motor_a):
    """Seleciona contator pela corrente de emprego AC-3 (acionamento de motor)."""
    if corrente_motor_a <= 0:
        raise ValueError("corrente do motor deve ser positiva")
    for nominal in CONTATORES_AC3:
        if nominal >= corrente_motor_a:
            return {"corrente_motor_a": round(corrente_motor_a, 2), "contator_ac3_a": nominal}
    raise ValueError(
        f"corrente {corrente_motor_a:.1f} A acima do maior contator tabelado "
        f"({CONTATORES_AC3[-1]} A)"
    )


def corrente_curto_circuito(potencia_trafo_kva, tensao_secundaria_v, impedancia_percent):
    """Corrente de curto-circuito simétrica trifásica no secundário de um trafo.

    Útil para definir a capacidade de interrupção (Icu) dos disjuntores do painel.
    """
    if impedancia_percent <= 0:
        raise ValueError("impedância percentual deve ser positiva")
    in_a = (potencia_trafo_kva * 1000) / (_sqrt3() * tensao_secundaria_v)
    icc = in_a / (impedancia_percent / 100)
    return {
        "corrente_nominal_trafo_a": round(in_a, 1),
        "icc_simetrica_a": round(icc, 1),
        "icc_simetrica_ka": round(icc / 1000, 2),
    }


# ==================== CONDUTORES ====================

def dimensionar_condutor(corrente_projeto_a, fator_correcao=1.0):
    """Seleciona a menor seção (mm²) cuja ampacidade atende à corrente de projeto.

    fator_correcao: produto dos fatores de agrupamento/temperatura (<=1).
    A corrente corrigida = corrente_projeto / fator_correcao.
    Base: cobre, PVC, método B1, 3 condutores carregados (NBR 5410).
    """
    if corrente_projeto_a <= 0:
        raise ValueError("corrente de projeto deve ser positiva")
    if not (0 < fator_correcao <= 1):
        raise ValueError("fator de correção deve estar entre 0 e 1")
    corrente_corrigida = corrente_projeto_a / fator_correcao
    for secao, ampacidade in sorted(AMPACIDADE_CU_PVC_B1.items()):
        if ampacidade >= corrente_corrigida:
            return {
                "corrente_projeto_a": round(corrente_projeto_a, 2),
                "corrente_corrigida_a": round(corrente_corrigida, 2),
                "secao_mm2": secao,
                "ampacidade_a": ampacidade,
            }
    raise ValueError(
        f"corrente corrigida {corrente_corrigida:.1f} A acima da maior seção "
        f"tabelada (300 mm² = {AMPACIDADE_CU_PVC_B1[300]} A)"
    )


def queda_tensao(corrente_a, comprimento_m, secao_mm2, tensao_v,
                 trifasico=True, material="cobre", limite_percent=QUEDA_MAX_TERMINAL):
    """Queda de tensão num condutor (ida e volta), em V e %.

    Retorna dict com queda, percentual, tensão no ponto de uso e se está dentro
    do limite recomendado.
    """
    if secao_mm2 <= 0 or comprimento_m < 0 or tensao_v <= 0:
        raise ValueError("seção, tensão e comprimento devem ser válidos")
    rho = RESISTIVIDADE.get(material)
    if rho is None:
        raise ValueError("material deve ser 'cobre' ou 'aluminio'")
    fator = _sqrt3() if trifasico else 2.0
    queda_v = fator * rho * comprimento_m * corrente_a / secao_mm2
    queda_pct = (queda_v / tensao_v) * 100
    return {
        "queda_v": round(queda_v, 2),
        "queda_percent": round(queda_pct, 2),
        "tensao_no_uso_v": round(tensao_v - queda_v, 2),
        "limite_percent": limite_percent,
        "dentro_limite": queda_pct <= limite_percent,
    }


def secao_minima_por_queda(corrente_a, comprimento_m, tensao_v, queda_max_percent=QUEDA_MAX_TERMINAL,
                           trifasico=True, material="cobre"):
    """Menor seção comercial que mantém a queda de tensão dentro do limite."""
    rho = RESISTIVIDADE.get(material)
    if rho is None:
        raise ValueError("material deve ser 'cobre' ou 'aluminio'")
    fator = _sqrt3() if trifasico else 2.0
    queda_max_v = tensao_v * queda_max_percent / 100
    if queda_max_v <= 0:
        raise ValueError("queda máxima deve ser positiva")
    secao_teorica = fator * rho * comprimento_m * corrente_a / queda_max_v
    for secao in sorted(AMPACIDADE_CU_PVC_B1):
        if secao >= secao_teorica:
            return {
                "secao_teorica_mm2": round(secao_teorica, 2),
                "secao_comercial_mm2": secao,
            }
    raise ValueError(
        f"seção teórica {secao_teorica:.1f} mm² acima da maior seção tabelada (300 mm²)"
    )


# ==================== CORREÇÃO DE FATOR DE POTÊNCIA ====================

def corrigir_fator_potencia(potencia_ativa_w, fp_atual, fp_desejado=0.92):
    """Potência reativa capacitiva (kVAr) para correção do fator de potência.

    Retorna dict com kVAr necessários e ângulos antes/depois.
    """
    if not (0 < fp_atual <= 1) or not (0 < fp_desejado <= 1):
        raise ValueError("fatores de potência devem estar entre 0 e 1")
    if fp_desejado <= fp_atual:
        raise ValueError("fp desejado deve ser maior que o atual")
    ang_atual = math.acos(fp_atual)
    ang_desejado = math.acos(fp_desejado)
    qc_w = potencia_ativa_w * (math.tan(ang_atual) - math.tan(ang_desejado))
    return {
        "fp_atual": fp_atual,
        "fp_desejado": fp_desejado,
        "potencia_reativa_capacitiva_kvar": round(qc_w / 1000, 2),
    }


if __name__ == "__main__":  # demonstração rápida
    motor = corrente_motor(potencia_cv=10, tensao_v=380)
    print("Motor 10 CV / 380 V trifásico:", motor)
    print("Disjuntor:", dimensionar_disjuntor(motor["corrente_nominal_a"]))
    print("Contator:", dimensionar_contator(motor["corrente_nominal_a"]))
    print("Condutor:", dimensionar_condutor(motor["corrente_nominal_a"]))
    print("Queda 50 m:", queda_tensao(motor["corrente_nominal_a"], 50, 6, 380))
