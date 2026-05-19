"""
Calculadora de Verbas Trabalhistas - CLT 2026
Cálculo completo e robusto conforme legislação vigente:
- Saldo de salário
- Aviso prévio (proporcional ao tempo de serviço, art. 7º XXI CF + Lei 12.506/2011)
- 13º salário proporcional e integral
- Férias proporcionais + 1/3 constitucional
- Férias vencidas + 1/3 (simples e em dobro, art. 137 CLT)
- FGTS: depósito rescisório + multa 40% / 20%
- Multa art. 477 §8º CLT (atraso na rescisão)
- Multa art. 467 CLT (verbas incontroversas)
- Horas extras (50%, 100% domingos/feriados)
- Adicional noturno (20%, art. 73 CLT)
- Insalubridade (10%, 20%, 40% sobre salário mínimo)
- Periculosidade (30% sobre salário base, art. 193 CLT)
- Adicional de transferência (25%, art. 469 §3º CLT)
- Salário-família
- Vale-transporte (desconto 6%)
- INSS progressivo 2026
- IRRF com dedução por dependentes
- DSR sobre horas extras
- Reflexos de HE/adicionais sobre 13º, férias, FGTS
- Seguro-desemprego (estimativa de parcelas)
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import math

# ==================== CONSTANTES 2026 ====================

SALARIO_MINIMO_2026 = 1518.00

TETO_INSS_2026 = 8157.41

TABELA_INSS_2026 = [
    (1518.00, 0.075),
    (2793.88, 0.09),
    (4190.83, 0.12),
    (8157.41, 0.14),
]

TABELA_IRRF_2026 = [
    (2259.20, 0.0, 0.0),
    (2826.65, 0.075, 169.44),
    (3751.05, 0.15, 381.44),
    (4664.68, 0.225, 662.77),
    (float('inf'), 0.275, 896.00),
]

DEDUCAO_DEPENDENTE_IRRF = 189.59

# Contribuição sindical 2026 (padrão 1 dia de trabalho)
CONTRIBUICAO_SINDICAL_PERCENTUAL = 1 / 30  # 1 dia de 30 dias de trabalho

# Salário-família 2026 (estimativa baseada em 2025)
SALARIO_FAMILIA_TETO = 1819.26
SALARIO_FAMILIA_VALOR = 62.04

# Seguro-desemprego 2026 (faixas estimadas)
SEGURO_DESEMP_FAIXAS = [
    (2120.76, 0.8, 0),
    (3536.26, 0.5, 1696.61),
    (float('inf'), 0, 2404.36),  # valor fixo
]
SEGURO_DESEMP_TETO = 2404.36

TIPOS_RESCISAO = {
    'sem_justa_causa': 'Dispensa sem justa causa',
    'pedido_demissao': 'Pedido de demissão',
    'justa_causa_empregador': 'Justa causa aplicada pelo empregador',
    'justa_causa_empregado': 'Justa causa do empregador (rescisão indireta)',
    'rescisao_indireta': 'Rescisão indireta (art. 483 CLT)',
    'culpa_reciproca': 'Culpa recíproca (art. 484 CLT)',
    'acordo_mutuo': 'Acordo mútuo (art. 484-A CLT)',
    'termino_contrato': 'Término de contrato por prazo determinado',
    'falecimento': 'Falecimento do empregado',
}


# ==================== FUNÇÕES AUXILIARES ====================

def formatar_moeda(valor):
    """Formata valor para moeda brasileira R$ X.XXX,XX"""
    try:
        if valor is None:
            return "R$ 0,00"
        negativo = valor < 0
        valor = abs(valor)
        inteiro = int(valor)
        centavos = round((valor - inteiro) * 100)
        if centavos >= 100:
            inteiro += 1
            centavos = 0
        # Formatar com pontos de milhar
        s = str(inteiro)
        partes = []
        while len(s) > 3:
            partes.insert(0, s[-3:])
            s = s[:-3]
        partes.insert(0, s)
        resultado = '.'.join(partes) + ',' + f"{centavos:02d}"
        return f"-R$ {resultado}" if negativo else f"R$ {resultado}"
    except (TypeError, ValueError):
        return "R$ 0,00"


def parse_data(data_str):
    """Converte string de data para objeto date"""
    if isinstance(data_str, date):
        return data_str
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(data_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def calcular_tempo_servico(dt_admissao, dt_demissao):
    """Calcula tempo de serviço detalhado usando relativedelta"""
    rd = relativedelta(dt_demissao, dt_admissao)
    anos = rd.years
    meses = rd.months
    dias = rd.days
    total_dias = (dt_demissao - dt_admissao).days
    total_meses = anos * 12 + meses + (1 if dias >= 15 else 0)
    return {
        'anos': anos,
        'meses': meses,
        'dias': dias,
        'total_dias': total_dias,
        'total_meses': total_meses,
        'total_meses_exato': anos * 12 + meses,
        'descricao': f"{anos} ano(s), {meses} mês(es) e {dias} dia(s)",
    }


# ==================== CÁLCULOS DE IMPOSTOS ====================

def calcular_inss(salario_contribuicao):
    """Cálculo progressivo do INSS conforme tabela 2026"""
    if salario_contribuicao <= 0:
        return 0
    inss = 0
    anterior = 0
    for teto, aliquota in TABELA_INSS_2026:
        faixa = min(salario_contribuicao, teto) - anterior
        if faixa > 0:
            inss += faixa * aliquota
        anterior = teto
        if salario_contribuicao <= teto:
            break
    return round(inss, 2)


def calcular_irrf(base_calculo, dependentes=0):
    """Cálculo do IRRF com dedução por dependentes"""
    base = base_calculo - (dependentes * DEDUCAO_DEPENDENTE_IRRF)
    if base <= 0:
        return 0
    for teto, aliquota, deducao in TABELA_IRRF_2026:
        if base <= teto:
            return round(max(base * aliquota - deducao, 0), 2)
    return 0


# ==================== CÁLCULOS DE VERBAS ====================

def calcular_saldo_salario(remuneracao_diaria, dias_trabalhados):
    """Saldo de salário proporcional aos dias trabalhados no mês da rescisão"""
    return round(remuneracao_diaria * dias_trabalhados, 2)


def calcular_aviso_previo(remuneracao, anos_servico, tipo_rescisao, aviso_previo_tipo):
    """
    Aviso prévio proporcional ao tempo de serviço (Lei 12.506/2011)
    Base: 30 dias + 3 dias por ano de serviço, máximo 90 dias
    """
    if tipo_rescisao in ('justa_causa_empregador', 'termino_contrato'):
        return {'valor': 0, 'dias': 0, 'tipo': 'nenhum'}

    dias_aviso = min(30 + (anos_servico * 3), 90)

    if tipo_rescisao == 'pedido_demissao':
        # Empregado que pede demissão: 30 dias fixos
        dias_aviso = 30
        if aviso_previo_tipo == 'indenizado':
            # Empregado que não cumpre: empregador pode descontar
            return {'valor': 0, 'dias': 30, 'tipo': 'desconto_possivel',
                    'desconto': round(remuneracao, 2)}
        else:
            return {'valor': 0, 'dias': 30, 'tipo': 'trabalhado'}

    if tipo_rescisao == 'acordo_mutuo':
        # Art. 484-A: metade do aviso prévio indenizado
        if aviso_previo_tipo == 'indenizado':
            valor = round((remuneracao / 30 * dias_aviso) * 0.5, 2)
            return {'valor': valor, 'dias': dias_aviso, 'tipo': 'indenizado_metade'}
        return {'valor': 0, 'dias': dias_aviso, 'tipo': 'trabalhado'}

    if tipo_rescisao == 'culpa_reciproca':
        # Súmula 14 TST: metade do aviso prévio
        valor = round((remuneracao / 30 * dias_aviso) * 0.5, 2)
        return {'valor': valor, 'dias': dias_aviso, 'tipo': 'metade_culpa_reciproca'}

    # Sem justa causa / rescisão indireta
    if aviso_previo_tipo == 'indenizado':
        valor = round(remuneracao / 30 * dias_aviso, 2)
        return {'valor': valor, 'dias': dias_aviso, 'tipo': 'indenizado'}
    elif aviso_previo_tipo == 'trabalhado':
        return {'valor': 0, 'dias': dias_aviso, 'tipo': 'trabalhado'}
    else:
        return {'valor': 0, 'dias': 0, 'tipo': 'nenhum'}


def calcular_13_proporcional(remuneracao, meses_trabalhados_ano, tipo_rescisao):
    """
    13º salário proporcional (Lei 4.090/62)
    Não é devido na justa causa aplicada pelo empregador
    Culpa recíproca: metade (Súmula 14 TST)
    """
    if tipo_rescisao == 'justa_causa_empregador':
        return 0
    valor = round(remuneracao / 12 * meses_trabalhados_ano, 2)
    if tipo_rescisao == 'culpa_reciproca':
        valor = round(valor * 0.5, 2)
    return valor


def calcular_ferias_proporcionais(remuneracao, meses_periodo_aquisitivo, tipo_rescisao):
    """
    Férias proporcionais + 1/3 constitucional (art. 146 CLT)
    Justa causa: não é devido (Súmula 171 TST)
    Culpa recíproca: metade (Súmula 14 TST)
    """
    if tipo_rescisao == 'justa_causa_empregador':
        return {'ferias': 0, 'terco': 0}
    ferias = round(remuneracao / 12 * min(meses_periodo_aquisitivo, 12), 2)
    if tipo_rescisao == 'culpa_reciproca':
        ferias = round(ferias * 0.5, 2)
    terco = round(ferias / 3, 2)
    return {'ferias': ferias, 'terco': terco}


def calcular_ferias_vencidas(remuneracao, periodos_vencidos, periodos_em_dobro=0):
    """
    Férias vencidas + 1/3 (art. 137 CLT)
    Se vencidas há mais de 12 meses do período concessivo: em dobro
    """
    ferias_simples = round(remuneracao * periodos_vencidos, 2)
    ferias_dobro = round(remuneracao * 2 * periodos_em_dobro, 2)
    total_ferias = ferias_simples + ferias_dobro
    terco = round(total_ferias / 3, 2)
    return {
        'ferias_simples': ferias_simples,
        'ferias_dobro': ferias_dobro,
        'total_ferias': total_ferias,
        'terco': terco,
        'total': round(total_ferias + terco, 2),
    }


def calcular_multa_fgts(saldo_fgts, deposito_rescisorio, tipo_rescisao):
    """
    Multa do FGTS (art. 18 Lei 8.036/90)
    Sem justa causa / rescisão indireta: 40%
    Acordo mútuo (art. 484-A): 20%
    Culpa recíproca: 20% (art. 484 CLT)
    """
    base = saldo_fgts + deposito_rescisorio
    if tipo_rescisao in ('sem_justa_causa', 'justa_causa_empregado', 'rescisao_indireta'):
        return {'percentual': 40, 'valor': round(base * 0.40, 2), 'base': round(base, 2)}
    elif tipo_rescisao in ('acordo_mutuo', 'culpa_reciproca'):
        return {'percentual': 20, 'valor': round(base * 0.20, 2), 'base': round(base, 2)}
    else:
        return {'percentual': 0, 'valor': 0, 'base': round(base, 2)}


def calcular_deposito_fgts_rescisorio(remuneracao, aviso_previo_indenizado, decimo_terceiro_prop):
    """Depósito do FGTS sobre verbas rescisórias (8%)"""
    base = remuneracao + aviso_previo_indenizado + decimo_terceiro_prop
    return round(base * 0.08, 2)


def calcular_horas_extras(salario_hora, qtd_horas_50, qtd_horas_100=0):
    """
    Horas extras (art. 59 CLT)
    50% dias úteis, 100% domingos/feriados
    """
    he_50 = round(salario_hora * 1.5 * qtd_horas_50, 2)
    he_100 = round(salario_hora * 2.0 * qtd_horas_100, 2)
    return {
        'he_50': he_50,
        'he_100': he_100,
        'total': round(he_50 + he_100, 2),
        'qtd_50': qtd_horas_50,
        'qtd_100': qtd_horas_100,
    }


def calcular_dsr_sobre_horas_extras(valor_he_total, dias_uteis_mes=26, domingos_feriados_mes=4):
    """DSR sobre horas extras (Súmula 172 TST)"""
    if dias_uteis_mes == 0:
        return 0
    return round((valor_he_total / dias_uteis_mes) * domingos_feriados_mes, 2)


def calcular_adicional_noturno(salario_hora, horas_noturnas_mes=0, percentual=20):
    """
    Adicional noturno (art. 73 CLT)
    Urbano: 20% sobre hora noturna (22h às 5h)
    Hora noturna reduzida: 52min30s
    """
    if horas_noturnas_mes <= 0:
        return {'valor': 0, 'horas': 0}
    valor = round(salario_hora * (percentual / 100) * horas_noturnas_mes, 2)
    return {'valor': valor, 'horas': horas_noturnas_mes}


def calcular_insalubridade(grau, base_calculo=None):
    """
    Insalubridade (art. 192 CLT)
    Mínimo: 10%, Médio: 20%, Máximo: 40%
    Base: salário mínimo (Súmula Vinculante 4 STF - controvérsia)
    """
    base = base_calculo or SALARIO_MINIMO_2026
    percentuais = {'minimo': 0.10, 'medio': 0.20, 'maximo': 0.40}
    pct = percentuais.get(grau, 0)
    return {
        'grau': grau or 'nenhum',
        'percentual': pct * 100,
        'base': round(base, 2),
        'valor': round(base * pct, 2),
    }


def calcular_periculosidade(salario_base, aplica=False):
    """Periculosidade (art. 193 CLT) - 30% sobre salário base"""
    if not aplica:
        return {'valor': 0, 'percentual': 0}
    return {
        'valor': round(salario_base * 0.30, 2),
        'percentual': 30,
    }


def calcular_adicional_transferencia(salario_base, aplica=False):
    """Adicional de transferência (art. 469 §3º CLT) - 25%"""
    if not aplica:
        return 0
    return round(salario_base * 0.25, 2)


def calcular_salario_familia(salario, num_filhos_menores=0):
    """Salário-família (art. 65 Lei 8.213/91)"""
    if salario > SALARIO_FAMILIA_TETO or num_filhos_menores <= 0:
        return {'valor': 0, 'por_filho': 0, 'filhos': num_filhos_menores}
    valor = round(SALARIO_FAMILIA_VALOR * num_filhos_menores, 2)
    return {'valor': valor, 'por_filho': SALARIO_FAMILIA_VALOR, 'filhos': num_filhos_menores}


def calcular_multa_477(remuneracao, aplica=True):
    """
    Multa art. 477 §8º CLT
    Atraso no pagamento das verbas rescisórias (10 dias úteis)
    Valor: 1 salário do empregado
    """
    if not aplica:
        return 0
    return round(remuneracao, 2)


def calcular_multa_467(verbas_incontroversas, aplica=False):
    """
    Multa art. 467 CLT
    Verbas incontroversas não pagas na 1ª audiência
    Valor: 50% sobre as verbas incontroversas
    """
    if not aplica:
        return 0
    return round(verbas_incontroversas * 0.50, 2)


def estimar_seguro_desemprego(salario_medio_3m, meses_trabalhados, vezes_solicitado=0):
    """
    Estimativa do seguro-desemprego (Lei 7.998/90)
    Parcelas: 3 a 5 conforme tempo de serviço e vezes solicitado
    """
    # Número de parcelas
    if vezes_solicitado == 0:
        # Primeira solicitação: mínimo 12 meses nos últimos 18
        if meses_trabalhados >= 24:
            parcelas = 5
        elif meses_trabalhados >= 12:
            parcelas = 4
        else:
            parcelas = 0
    elif vezes_solicitado == 1:
        # Segunda solicitação: mínimo 9 meses nos últimos 12
        if meses_trabalhados >= 24:
            parcelas = 5
        elif meses_trabalhados >= 12:
            parcelas = 4
        elif meses_trabalhados >= 9:
            parcelas = 3
        else:
            parcelas = 0
    else:
        # Demais: mínimo 6 meses
        if meses_trabalhados >= 24:
            parcelas = 5
        elif meses_trabalhados >= 12:
            parcelas = 4
        elif meses_trabalhados >= 6:
            parcelas = 3
        else:
            parcelas = 0

    if parcelas == 0:
        return {'parcelas': 0, 'valor_parcela': 0, 'total': 0}

    # Valor da parcela
    sm = salario_medio_3m
    if sm <= SEGURO_DESEMP_FAIXAS[0][0]:
        valor = round(sm * SEGURO_DESEMP_FAIXAS[0][1], 2)
    elif sm <= SEGURO_DESEMP_FAIXAS[1][0]:
        excedente = sm - SEGURO_DESEMP_FAIXAS[0][0]
        valor = round(SEGURO_DESEMP_FAIXAS[1][2] + excedente * SEGURO_DESEMP_FAIXAS[1][1], 2)
    else:
        valor = SEGURO_DESEMP_TETO

    valor = max(valor, SALARIO_MINIMO_2026)
    valor = min(valor, SEGURO_DESEMP_TETO)

    return {
        'parcelas': parcelas,
        'valor_parcela': round(valor, 2),
        'total': round(valor * parcelas, 2),
    }


def calcular_reflexos(valor_mensal, meses_13=None, meses_ferias=None):
    """Calcula reflexos de adicionais sobre 13º, férias e FGTS"""
    reflexos = {}
    if meses_13 and meses_13 > 0:
        reflexos['sobre_13'] = round(valor_mensal / 12 * meses_13, 2)
    if meses_ferias and meses_ferias > 0:
        ferias = round(valor_mensal / 12 * meses_ferias, 2)
        reflexos['sobre_ferias'] = ferias
        reflexos['sobre_terco_ferias'] = round(ferias / 3, 2)
    reflexos['sobre_fgts_mensal'] = round(valor_mensal * 0.08, 2)
    return reflexos


def calcular_reflexos_fgts_completos(remuneracao_habitual, horas_extras_total, dsr_he, adic_noturno_valor, insalub_valor, pericu_valor, meses_trabalhados=1):
    """
    Calcula reflexos FGTS sobre TODOS os adicionais conforme Lei 8.036/90
    O FGTS (8%) incide sobre: salário + HE + DSR + noturno + insalubridade + periculosidade
    """
    base_fgts_mensal = remuneracao_habitual + horas_extras_total + dsr_he + adic_noturno_valor + insalub_valor + pericu_valor
    fgts_mensal = round(base_fgts_mensal * 0.08, 2)
    fgts_total = round(fgts_mensal * meses_trabalhados, 2)
    return {
        'base_mensal': round(base_fgts_mensal, 2),
        'fgts_mensal': fgts_mensal,
        'meses_trabalhados': meses_trabalhados,
        'fgts_total': fgts_total,
    }


def calcular_licenca_premio(remuneracao, anos_servico, periodos_nao_utilizados=0):
    """
    Licença-prêmio (30 dias a cada 5 anos de serviço)
    Conversível em dinheiro no desligamento (art. 153 CLT)
    """
    # 1 período de 30 dias a cada 5 anos completos
    periodos_adquiridos = int(anos_servico // 5)
    periodos_disponiveis = periodos_adquiridos - periodos_nao_utilizados
    
    remuneracao_diaria = remuneracao / 30
    valor_licenca = round(remuneracao_diaria * 30 * periodos_disponiveis, 2)
    
    return {
        'periodos_adquiridos': periodos_adquiridos,
        'periodos_utilizados': periodos_nao_utilizados,
        'periodos_disponiveis': max(periodos_disponiveis, 0),
        'valor_por_periodo': round(remuneracao_diaria * 30, 2),
        'valor_total': valor_licenca,
    }


def calcular_abono_ferias(remuneracao, meses_ferias_direito=12, parte_convertida=1):
    """
    Abono de férias (art. 143 CLT - conversão de 1/3)
    Permite converter 1/3 (ou mais) das férias em dinheiro
    """
    ferias_simples = round(remuneracao / 12 * meses_ferias_direito, 2)
    terco = round(ferias_simples / 3, 2)
    
    # Parte convertida em dinheiro (padrão 1/3, máximo 10 dias do direito de férias)
    abono = round(terco * parte_convertida, 2) if parte_convertida <= 1 else round(ferias_simples * (parte_convertida / 3), 2)
    ferias_gozadas = round(ferias_simples - abono, 2)
    
    return {
        'ferias_simples': ferias_simples,
        'terco_ferias': terco,
        'parte_convertida_percentual': parte_convertida * 100 if parte_convertida <= 1 else (parte_convertida / 3 * 100),
        'abono_dinheiro': abono,
        'ferias_gozadas': ferias_gozadas,
        'total': round(ferias_simples, 2),
    }


def calcular_contribuicao_sindical(remuneracao, aplica=False):
    """
    Contribuição sindical (Lei 5.584/70)
    Desconto de 1 dia de trabalho quando houver assembléia para eleição
    Normalmente cobrado em março (mês de eleição dos sindicatos)
    """
    if not aplica:
        return 0
    return round(remuneracao / 30, 2)


def calcular_irrf_progressivo_13(valor_13, num_dependentes=0):
    """
    IRRF sobre 13º salário com cálculo separado e alíquota progressiva
    Base de cálculo separada (art. 12-B da Lei 7.713/88)
    """
    # O 13º tem tributação especial (isolada do resto da renda)
    base = valor_13 - (num_dependentes * DEDUCAO_DEPENDENTE_IRRF)
    if base <= 0:
        return 0
    
    # Aplicar tabela IRRF normal
    for teto, aliquota, deducao in TABELA_IRRF_2026:
        if base <= teto:
            return round(max(base * aliquota - deducao, 0), 2)
    return 0


# ==================== FUNÇÃO PRINCIPAL ====================

def calcular_verbas(params):
    """
    Função principal de cálculo de verbas trabalhistas.
    Recebe um dicionário com todos os parâmetros e retorna resultado detalhado.

    Parâmetros aceitos:
    - salario_base (float): Salário base mensal
    - data_admissao (str): Data de admissão AAAA-MM-DD ou DD/MM/AAAA
    - data_demissao (str): Data de demissão AAAA-MM-DD ou DD/MM/AAAA
    - tipo_rescisao (str): Tipo de rescisão contratual
    - aviso_previo (str): 'indenizado', 'trabalhado' ou 'nenhum'
    - saldo_fgts (float): Saldo atual do FGTS
    - horas_extras_50 (float): Média de horas extras 50% por mês
    - horas_extras_100 (float): Média de horas extras 100% por mês
    - adicional_noturno_horas (float): Horas noturnas por mês
    - insalubridade_grau (str): 'minimo', 'medio', 'maximo' ou None
    - periculosidade (bool): Se recebe periculosidade
    - adicional_transferencia (bool): Se recebe adicional de transferência
    - periodos_ferias_vencidas (int): Períodos de férias vencidas simples
    - periodos_ferias_dobro (int): Períodos de férias vencidas em dobro
    - num_dependentes (int): Número de dependentes para IRRF
    - num_filhos_menores (int): Filhos menores de 14 anos (salário-família)
    - comissoes_media (float): Média mensal de comissões
    - gratificacoes (float): Gratificações habituais
    - vale_transporte (bool): Se desconta vale-transporte
    - multa_477 (bool): Aplicar multa do art. 477
    - multa_467 (bool): Aplicar multa do art. 467
    - vezes_seguro_desemprego (int): Quantas vezes já solicitou seguro-desemprego
    - dias_uteis_mes (int): Dias úteis no mês (padrão 26)
    - domingos_feriados_mes (int): Domingos e feriados no mês (padrão 4)
    """
    if isinstance(params, (int, float)):
        params = {'salario_base': float(params)}

    # ===== EXTRAIR PARÂMETROS =====
    salario_base = float(params.get('salario_base', SALARIO_MINIMO_2026))
    data_admissao_str = params.get('data_admissao', '2020-01-15')
    data_demissao_str = params.get('data_demissao', '2024-06-30')
    tipo_rescisao = params.get('tipo_rescisao', 'sem_justa_causa')
    aviso_previo_tipo = params.get('aviso_previo', 'indenizado')
    saldo_fgts = float(params.get('saldo_fgts', 0))
    horas_extras_50 = float(params.get('horas_extras_50', params.get('horas_extras_mes', 0)))
    horas_extras_100 = float(params.get('horas_extras_100', 0))
    adicional_noturno_horas = float(params.get('adicional_noturno_horas', 0))
    # Compatibilidade com formato antigo
    if adicional_noturno_horas == 0:
        adn_pct = float(params.get('adicional_noturno_pct', 0))
        if adn_pct > 0:
            adicional_noturno_horas = 120  # estimativa padrão
    insalubridade_grau = params.get('insalubridade_grau', None)
    # Compatibilidade numérica
    if isinstance(insalubridade_grau, (int, float)):
        if insalubridade_grau >= 40:
            insalubridade_grau = 'maximo'
        elif insalubridade_grau >= 20:
            insalubridade_grau = 'medio'
        elif insalubridade_grau >= 10:
            insalubridade_grau = 'minimo'
        else:
            insalubridade_grau = None
    periculosidade = bool(params.get('periculosidade', False))
    if isinstance(params.get('periculosidade'), (int, float)):
        periculosidade = float(params.get('periculosidade', 0)) >= 30
    adicional_transferencia = bool(params.get('adicional_transferencia', False))
    periodos_ferias_vencidas = int(params.get('periodos_ferias_vencidas',
                                               params.get('meses_ferias_vencidas', 0)))
    periodos_ferias_dobro = int(params.get('periodos_ferias_dobro', 0))
    num_dependentes = int(params.get('num_dependentes', 0))
    num_filhos_menores = int(params.get('num_filhos_menores', 0))
    comissoes_media = float(params.get('comissoes_media', 0))
    gratificacoes = float(params.get('gratificacoes', 0))
    vale_transporte = bool(params.get('vale_transporte', False))
    aplicar_multa_477 = bool(params.get('multa_477', False))
    aplicar_multa_467 = bool(params.get('multa_467', False))
    vezes_seguro = int(params.get('vezes_seguro_desemprego', 0))
    dias_uteis_mes = int(params.get('dias_uteis_mes', 26))
    domingos_feriados_mes = int(params.get('domingos_feriados_mes', 4))

    # ===== DATAS E TEMPO DE SERVIÇO =====
    dt_adm = parse_data(data_admissao_str) or date(2020, 1, 15)
    dt_dem = parse_data(data_demissao_str) or date(2024, 6, 30)
    if dt_dem < dt_adm:
        dt_adm, dt_dem = dt_dem, dt_adm

    tempo = calcular_tempo_servico(dt_adm, dt_dem)

    # ===== REMUNERAÇÃO =====
    insalub = calcular_insalubridade(insalubridade_grau)
    pericu = calcular_periculosidade(salario_base, periculosidade)
    adic_transf = calcular_adicional_transferencia(salario_base, adicional_transferencia)

    remuneracao = salario_base + comissoes_media + gratificacoes + insalub['valor'] + pericu['valor'] + adic_transf
    salario_hora = remuneracao / 220  # jornada padrão 44h/semana
    remuneracao_diaria = remuneracao / 30

    # ===== HORAS EXTRAS E ADICIONAIS =====
    he = calcular_horas_extras(salario_hora, horas_extras_50, horas_extras_100)
    dsr_he = calcular_dsr_sobre_horas_extras(he['total'], dias_uteis_mes, domingos_feriados_mes)
    adic_noturno = calcular_adicional_noturno(salario_hora, adicional_noturno_horas)

    # Remuneração com habitualidades (para cálculo de reflexos)
    remuneracao_habitual = remuneracao + he['total'] + dsr_he + adic_noturno['valor']

    # ===== SALDO DE SALÁRIO =====
    dias_trabalhados_mes = dt_dem.day
    saldo_salario = calcular_saldo_salario(remuneracao_diaria, dias_trabalhados_mes)

    # ===== AVISO PRÉVIO =====
    aviso = calcular_aviso_previo(remuneracao_habitual, tempo['anos'], tipo_rescisao, aviso_previo_tipo)

    # Projeção do aviso para cálculo de 13º e férias
    dias_aviso_projecao = aviso['dias'] if aviso['tipo'] in ('indenizado', 'indenizado_metade') else 0

    # ===== 13º PROPORCIONAL =====
    # Meses trabalhados no ano da rescisão (incluindo projeção do aviso)
    dt_ref_13 = dt_dem
    if dias_aviso_projecao > 0:
        dt_ref_13 = dt_dem + relativedelta(days=dias_aviso_projecao)
    meses_13_ano = dt_ref_13.month
    if dt_ref_13.day < 15:
        meses_13_ano = max(meses_13_ano - 1, 0)
    # Se admitido no mesmo ano
    if dt_adm.year == dt_ref_13.year:
        meses_13_ano = max(meses_13_ano - dt_adm.month + (1 if dt_adm.day <= 15 else 0), 0)

    decimo_terceiro = calcular_13_proporcional(remuneracao_habitual, meses_13_ano, tipo_rescisao)

    # ===== FÉRIAS PROPORCIONAIS =====
    # Período aquisitivo corrente
    ano_ref = dt_dem.year
    try:
        ultimo_aniv = date(ano_ref, dt_adm.month, dt_adm.day)
    except ValueError:
        ultimo_aniv = date(ano_ref, dt_adm.month, 28)
    if ultimo_aniv > dt_dem:
        ultimo_aniv = ultimo_aniv - relativedelta(years=1)

    dt_ref_ferias = dt_dem
    if dias_aviso_projecao > 0:
        dt_ref_ferias = dt_dem + relativedelta(days=dias_aviso_projecao)

    meses_ferias = 0
    d = ultimo_aniv
    while d + relativedelta(months=1) <= dt_ref_ferias:
        meses_ferias += 1
        d += relativedelta(months=1)
    # Fração >= 15 dias conta como mês
    dias_restantes_ferias = (dt_ref_ferias - d).days
    if dias_restantes_ferias >= 15:
        meses_ferias += 1
    meses_ferias = min(meses_ferias, 12)

    ferias_prop = calcular_ferias_proporcionais(remuneracao_habitual, meses_ferias, tipo_rescisao)

    # ===== FÉRIAS VENCIDAS =====
    ferias_venc = calcular_ferias_vencidas(remuneracao_habitual, periodos_ferias_vencidas, periodos_ferias_dobro)

    # ===== FGTS =====
    deposito_fgts_resc = calcular_deposito_fgts_rescisorio(
        saldo_salario,
        aviso['valor'],
        decimo_terceiro
    )
    multa_fgts = calcular_multa_fgts(saldo_fgts, deposito_fgts_resc, tipo_rescisao)

    # ===== SALÁRIO-FAMÍLIA =====
    sal_familia = calcular_salario_familia(salario_base, num_filhos_menores)

    # ===== MULTAS =====
    multa_477_val = calcular_multa_477(remuneracao, aplicar_multa_477)
    total_verbas_incontroversas = saldo_salario + decimo_terceiro + ferias_prop['ferias'] + ferias_prop['terco']
    multa_467_val = calcular_multa_467(total_verbas_incontroversas, aplicar_multa_467)

    # ===== SEGURO-DESEMPREGO =====
    seguro = {'parcelas': 0, 'valor_parcela': 0, 'total': 0}
    if tipo_rescisao in ('sem_justa_causa', 'rescisao_indireta', 'justa_causa_empregado'):
        seguro = estimar_seguro_desemprego(remuneracao, tempo['total_meses'], vezes_seguro)

    # ===== REFLEXOS =====
    reflexos_he = {}
    if he['total'] > 0:
        reflexos_he = calcular_reflexos(he['total'] + dsr_he, meses_13_ano, meses_ferias)

    reflexos_noturno = {}
    if adic_noturno['valor'] > 0:
        reflexos_noturno = calcular_reflexos(adic_noturno['valor'], meses_13_ano, meses_ferias)

    # ===== MONTAGEM DAS VERBAS =====
    verbas = {}
    verbas['saldo_salario'] = saldo_salario
    verbas['aviso_previo'] = aviso['valor']
    verbas['decimo_terceiro_proporcional'] = decimo_terceiro
    verbas['ferias_proporcionais'] = ferias_prop['ferias']
    verbas['terco_ferias_proporcionais'] = ferias_prop['terco']
    verbas['ferias_vencidas'] = ferias_venc['total_ferias']
    verbas['terco_ferias_vencidas'] = ferias_venc['terco']
    verbas['multa_fgts'] = multa_fgts['valor']
    verbas['deposito_fgts_rescisorio'] = deposito_fgts_resc
    verbas['horas_extras'] = he['total']
    verbas['dsr_horas_extras'] = dsr_he
    verbas['adicional_noturno'] = adic_noturno['valor']
    verbas['insalubridade'] = insalub['valor']
    verbas['periculosidade'] = pericu['valor']
    verbas['adicional_transferencia'] = adic_transf
    verbas['salario_familia'] = sal_familia['valor']
    verbas['multa_art_477'] = multa_477_val
    verbas['multa_art_467'] = multa_467_val

    # Reflexos
    total_reflexos = 0
    for r in [reflexos_he, reflexos_noturno]:
        for v in r.values():
            total_reflexos += v
    verbas['reflexos_adicionais'] = round(total_reflexos, 2)

    total_bruto = round(sum(v for v in verbas.values() if v > 0), 2)

    # ===== DESCONTOS =====
    descontos = {}
    inss = calcular_inss(remuneracao)
    descontos['inss'] = inss

    base_irrf = remuneracao - inss
    irrf = calcular_irrf(base_irrf, num_dependentes)
    descontos['irrf'] = irrf

    if vale_transporte and salario_base > 0:
        vt_desconto = round(salario_base * 0.06, 2)
        descontos['vale_transporte'] = vt_desconto

    # Desconto aviso prévio não cumprido (pedido de demissão)
    if aviso.get('desconto', 0) > 0 and tipo_rescisao == 'pedido_demissao' and aviso_previo_tipo == 'indenizado':
        descontos['aviso_previo_desconto'] = aviso['desconto']

    total_descontos = round(sum(descontos.values()), 2)
    total_liquido = round(total_bruto - total_descontos, 2)

    # ===== RESULTADO COMPLETO =====
    return {
        'dados_contrato': {
            'salario_base': salario_base,
            'data_admissao': str(dt_adm),
            'data_demissao': str(dt_dem),
            'tipo_rescisao': tipo_rescisao,
            'tipo_rescisao_descricao': TIPOS_RESCISAO.get(tipo_rescisao, tipo_rescisao),
            'tempo_servico': tempo['descricao'],
            'tempo_anos': tempo['anos'],
            'tempo_meses_total': tempo['total_meses'],
            'remuneracao_total': round(remuneracao, 2),
            'remuneracao_habitual': round(remuneracao_habitual, 2),
            'salario_hora': round(salario_hora, 2),
            'aviso_previo_tipo': aviso['tipo'],
            'aviso_previo_dias': aviso['dias'],
        },
        'verbas': verbas,
        'detalhamento': {
            'aviso_previo': aviso,
            'horas_extras': he,
            'dsr_horas_extras': dsr_he,
            'adicional_noturno': adic_noturno,
            'insalubridade': insalub,
            'periculosidade': pericu,
            'ferias_vencidas': ferias_venc,
            'multa_fgts': multa_fgts,
            'salario_familia': sal_familia,
            'seguro_desemprego': seguro,
            'reflexos_he': reflexos_he,
            'reflexos_noturno': reflexos_noturno,
            'meses_13': meses_13_ano,
            'meses_ferias': meses_ferias,
        },
        'descontos': descontos,
        'total_bruto': total_bruto,
        'total_descontos': total_descontos,
        'total_liquido': total_liquido,
        'seguro_desemprego': seguro,
        'fundamentacao': {
            'saldo_salario': 'Art. 462 e 464 CLT',
            'aviso_previo': 'Art. 7º, XXI, CF/88 + Lei 12.506/2011',
            'decimo_terceiro': 'Lei 4.090/62 + Lei 4.749/65',
            'ferias': 'Art. 129 a 153 CLT + Art. 7º, XVII, CF/88',
            'fgts': 'Lei 8.036/90 + Art. 7º, III, CF/88',
            'multa_fgts': 'Art. 18 §1º Lei 8.036/90',
            'acordo_mutuo': 'Art. 484-A CLT (Reforma Trabalhista)',
            'culpa_reciproca': 'Art. 484 CLT + Súmula 14 TST',
            'horas_extras': 'Art. 59 CLT + Súmula 264 TST',
            'dsr': 'Lei 605/49 + Súmula 172 TST',
            'adicional_noturno': 'Art. 73 CLT',
            'insalubridade': 'Art. 189 a 197 CLT + NR-15',
            'periculosidade': 'Art. 193 CLT + NR-16',
            'multa_477': 'Art. 477 §8º CLT',
            'multa_467': 'Art. 467 CLT',
            'seguro_desemprego': 'Lei 7.998/90 + Lei 13.134/2015',
            'salario_familia': 'Art. 65 a 70 Lei 8.213/91',
            'irrf': 'Lei 7.713/88 + IN RFB',
            'inss': 'Lei 8.212/91 + EC 103/2019',
        },
    }
