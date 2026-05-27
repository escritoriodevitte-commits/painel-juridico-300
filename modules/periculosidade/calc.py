"""
Calculadora de Periculosidade do Eletricista (cálculo trabalhista).

Ferramenta de "calculista" para apurar o adicional de periculosidade devido
ao eletricitário/eletricista que trabalha em contato com sistema elétrico de
potência ou em condições de risco equivalente, e seus reflexos nas demais
verbas — útil em petição inicial e liquidação de sentença trabalhista.

Fundamentos legais:
- Adicional de 30% sobre o salário-base (CLT art. 193, § 1º; Lei 12.740/2012).
- Atividade do eletricitário reconhecida como perigosa (Lei 7.369/85, revogada
  e absorvida pela Lei 12.740/2012; NR-10; NR-16, Anexo 4).
- Base de cálculo: salário-base (Súmula 191, I, do TST). Para contratos
  anteriores à Lei 12.740/2012, a Súmula 191, II, admite incidência sobre o
  conjunto de parcelas de natureza salarial — disponível via base_calculo.
- Prescrição quinquenal: art. 7º, XXIX, da CF (limite de 60 meses).

Módulo puro (somente biblioteca padrão). Valores monetários em reais (float).
"""

PERCENTUAL_PERICULOSIDADE = 0.30
ALIQUOTA_FGTS = 0.08
PRESCRICAO_MESES = 60  # prescrição quinquenal (art. 7º, XXIX, CF)


def calcular_adicional(base_calculo, percentual=PERCENTUAL_PERICULOSIDADE):
    """Valor mensal do adicional de periculosidade.

    base_calculo: salário-base (Súmula 191/TST) ou, nos casos da Súmula 191, II,
    o total das parcelas salariais.
    """
    if base_calculo < 0:
        raise ValueError("base de cálculo não pode ser negativa")
    return round(base_calculo * percentual, 2)


def calcular_reflexos(adicional_mensal, incluir_fgts=True, meses_no_ano=12):
    """Reflexos do adicional mensal (referente a 1 ano de competências).

    Considera 13º salário, férias acrescidas de 1/3 e, opcionalmente, FGTS (8%)
    sobre o adicional e seus reflexos em 13º e férias.
    Retorna dict com cada reflexo e o subtotal anual.
    """
    if adicional_mensal < 0:
        raise ValueError("adicional não pode ser negativo")
    adicional_ano = round(adicional_mensal * meses_no_ano, 2)
    decimo_terceiro = round(adicional_mensal, 2)                 # 1/12 * 12 meses
    ferias = round(adicional_mensal, 2)                          # 1/12 * 12 meses
    terco_ferias = round(ferias / 3, 2)                          # 1/3 constitucional
    base_fgts = adicional_ano + decimo_terceiro + ferias + terco_ferias
    fgts = round(base_fgts * ALIQUOTA_FGTS, 2) if incluir_fgts else 0.0
    subtotal = round(adicional_ano + decimo_terceiro + ferias + terco_ferias + fgts, 2)
    return {
        "adicional_ano": adicional_ano,
        "decimo_terceiro": decimo_terceiro,
        "ferias": ferias,
        "terco_ferias": terco_ferias,
        "fgts": fgts,
        "subtotal_anual": subtotal,
    }


def calcular_retroativo(base_calculo, meses, incluir_fgts=True,
                        percentual=PERCENTUAL_PERICULOSIDADE):
    """Valor retroativo do adicional + reflexos para um período em meses.

    Aplica a prescrição quinquenal: meses acima de 60 são sinalizados e o
    cálculo é limitado a 60 competências.
    Retorna dict detalhado, pronto para liquidação.
    """
    if meses <= 0:
        raise ValueError("o período em meses deve ser positivo")
    meses_prescritos = max(0, meses - PRESCRICAO_MESES)
    meses_devidos = min(meses, PRESCRICAO_MESES)

    adicional_mensal = calcular_adicional(base_calculo, percentual)
    anos = meses_devidos / 12
    reflexos = calcular_reflexos(adicional_mensal, incluir_fgts=incluir_fgts)

    adicional_periodo = round(adicional_mensal * meses_devidos, 2)
    # reflexos do dict são anuais; proporcionaliza ao período devido
    decimo_terceiro = round(reflexos["decimo_terceiro"] * anos, 2)
    ferias = round(reflexos["ferias"] * anos, 2)
    terco_ferias = round(reflexos["terco_ferias"] * anos, 2)
    base_fgts = adicional_periodo + decimo_terceiro + ferias + terco_ferias
    fgts = round(base_fgts * ALIQUOTA_FGTS, 2) if incluir_fgts else 0.0
    total = round(adicional_periodo + decimo_terceiro + ferias + terco_ferias + fgts, 2)

    return {
        "base_calculo": round(base_calculo, 2),
        "percentual": percentual,
        "adicional_mensal": adicional_mensal,
        "meses_informados": meses,
        "meses_devidos": meses_devidos,
        "meses_prescritos": meses_prescritos,
        "adicional_periodo": adicional_periodo,
        "reflexo_13": decimo_terceiro,
        "reflexo_ferias": ferias,
        "reflexo_terco_ferias": terco_ferias,
        "fgts": fgts,
        "total_devido": total,
        "observacao": (
            "Cálculo limitado à prescrição quinquenal (art. 7º, XXIX, CF). "
            f"{meses_prescritos} mês(es) prescrito(s)."
            if meses_prescritos else
            "Período integralmente dentro da prescrição quinquenal."
        ),
    }


if __name__ == "__main__":  # demonstração rápida
    base = 2500.0
    print(f"Salário-base: R$ {base:.2f}")
    print("Adicional mensal (30%):", calcular_adicional(base))
    print("Reflexos (1 ano):", calcular_reflexos(calcular_adicional(base)))
    print("Retroativo 36 meses:", calcular_retroativo(base, 36))
    print("Retroativo 72 meses (com prescrição):", calcular_retroativo(base, 72))
