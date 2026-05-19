"""
Analytics Engine - Motor de análise estratégica do Painel Jurídico
Previsão, teses, risco, competitiva, dashboard
"""
from core.database import get_all_lawsuits, get_all_judges, get_all_settlements, get_all_legal_references


class AnalyticsEngine:

    @staticmethod
    def get_dashboard_metrics():
        lawsuits = get_all_lawsuits()
        total = len(lawsuits)
        if total == 0:
            return {'total_processos': 0, 'em_andamento': 0, 'encerrados': 0, 'taxa_exito': 0,
                    'total_pedido': 0, 'total_obtido': 0, 'economia_total': 0, 'taxa_reducao': 0}
        em_andamento = len([l for l in lawsuits if l['status'] == 'em_andamento'])
        encerrados = total - em_andamento
        exitos = len([l for l in lawsuits if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial')])
        total_pedido = sum(l.get('valor_pedido', 0) or 0 for l in lawsuits)
        total_obtido = sum(l.get('valor_obtido', 0) or 0 for l in lawsuits)
        economia = sum(l.get('economia_processual', 0) or 0 for l in lawsuits)
        taxa_exito = round(exitos / max(encerrados, 1) * 100, 1)
        taxa_reducao = round(economia / max(total_pedido, 1) * 100, 1)
        return {
            'total_processos': total, 'em_andamento': em_andamento, 'encerrados': encerrados,
            'taxa_exito': taxa_exito, 'total_pedido': round(total_pedido, 2),
            'total_obtido': round(total_obtido, 2), 'economia_total': round(economia, 2),
            'taxa_reducao': taxa_reducao,
        }

    @staticmethod
    def get_prediction(judge_id=None, valor_pedido=None):
        lawsuits = get_all_lawsuits()
        if judge_id:
            lawsuits = [l for l in lawsuits if l.get('judge_id') == judge_id]
        total = len(lawsuits)
        if total == 0:
            return {'scores': {'prova': 5, 'jurisprudencia': 5, 'risco': 5, 'perfil_juiz': 5, 'final': 5},
                    'taxa_acordo': 0, 'taxa_improcedencia': 0, 'valor_acordo_sugerido': 0,
                    'estrategia': 'Dados insuficientes para previsão'}
        acordos = len([l for l in lawsuits if l['status'] == 'acordo'])
        improcedentes = len([l for l in lawsuits if l['status'] == 'sentenca_improcedente'])
        taxa_acordo = round(acordos / max(total, 1) * 100, 1)
        taxa_improcedencia = round(improcedentes / max(total, 1) * 100, 1)

        refs = get_all_legal_references()
        score_jurisp = min(10, 5 + len(refs) // 5)
        score_prova = 7
        score_risco = max(1, 10 - int(taxa_acordo / 10))
        score_juiz = 7 if taxa_acordo > 50 else 5
        score_final = round((score_prova + score_jurisp + score_risco + score_juiz) / 4, 1)

        valor_medio_acordo = 0
        acordos_list = [l for l in lawsuits if l['status'] == 'acordo' and l.get('valor_obtido')]
        if acordos_list:
            valor_medio_acordo = sum(l['valor_obtido'] for l in acordos_list) / len(acordos_list)

        vp = valor_pedido or (sum(l.get('valor_pedido', 0) or 0 for l in lawsuits) / max(total, 1))
        valor_sugerido = round(vp * (1 - taxa_acordo / 100) * 0.5, 2) if taxa_acordo > 0 else round(vp * 0.3, 2)

        if taxa_acordo > 60:
            estrategia = "Alta taxa de acordo. Recomendar negociação precoce com proposta agressiva."
        elif taxa_improcedencia > 30:
            estrategia = "Boa taxa de improcedência. Manter defesa técnica robusta e resistir a acordos desfavoráveis."
        else:
            estrategia = "Cenário equilibrado. Avaliar caso a caso e preparar defesa sólida."

        return {
            'scores': {'prova': score_prova, 'jurisprudencia': score_jurisp, 'risco': score_risco,
                       'perfil_juiz': score_juiz, 'final': score_final},
            'taxa_acordo': taxa_acordo, 'taxa_improcedencia': taxa_improcedencia,
            'valor_acordo_sugerido': valor_sugerido, 'estrategia': estrategia,
        }

    @staticmethod
    def get_prediction_history():
        lawsuits = get_all_lawsuits()
        judges = get_all_judges()
        result = []
        for j in judges:
            jl = [l for l in lawsuits if l.get('judge_id') == j['id']]
            if not jl:
                continue
            total = len(jl)
            acordos = len([l for l in jl if l['status'] == 'acordo'])
            improcedentes = len([l for l in jl if l['status'] == 'sentenca_improcedente'])
            exitos = len([l for l in jl if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial')])
            result.append({
                'judge_name': j['name'], 'total_processos': total,
                'taxa_acordo': round(acordos / total * 100, 1),
                'taxa_improcedencia': round(improcedentes / total * 100, 1),
                'taxa_exito': round(exitos / total * 100, 1),
            })
        return sorted(result, key=lambda x: x['taxa_exito'], reverse=True)

    @staticmethod
    def suggest_theses():
        lawsuits = get_all_lawsuits()
        teses_map = {}
        for l in lawsuits:
            tese = l.get('tese_defesa', '') or ''
            if not tese or len(tese) < 5:
                continue
            key = tese[:80]
            if key not in teses_map:
                teses_map[key] = {'tese': tese[:120], 'total': 0, 'exitos': 0, 'economia_total': 0}
            teses_map[key]['total'] += 1
            if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial'):
                teses_map[key]['exitos'] += 1
                teses_map[key]['economia_total'] += (l.get('economia_processual', 0) or 0)

        teses = []
        for v in teses_map.values():
            v['taxa_sucesso'] = round(v['exitos'] / max(v['total'], 1) * 100, 1)
            v['economia_media'] = round(v['economia_total'] / max(v['exitos'], 1), 2)
            teses.append(v)
        teses.sort(key=lambda x: x['taxa_sucesso'], reverse=True)

        provas = [
            {'tipo': 'Gravação de áudio', 'peso': 10, 'descricao': 'Prova direta, alta credibilidade'},
            {'tipo': 'Laudo pericial', 'peso': 9, 'descricao': 'Prova técnica vinculante'},
            {'tipo': 'Prints/WhatsApp', 'peso': 8, 'descricao': 'Prova documental digital'},
            {'tipo': 'Testemunha presencial', 'peso': 7, 'descricao': 'Prova oral direta'},
            {'tipo': 'Documento assinado', 'peso': 7, 'descricao': 'Prova documental formal'},
            {'tipo': 'Câmeras de segurança', 'peso': 6, 'descricao': 'Prova visual contextual'},
            {'tipo': 'E-mail corporativo', 'peso': 6, 'descricao': 'Prova documental eletrônica'},
            {'tipo': 'Testemunha indireta', 'peso': 4, 'descricao': 'Prova oral indireta'},
        ]

        exitos = [l for l in lawsuits if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial')]
        derrotas = [l for l in lawsuits if l['status'] == 'sentenca_procedente']

        padroes_vitoria = {
            'total': len(exitos),
            'media_economia': round(sum(l.get('economia_processual', 0) or 0 for l in exitos) / max(len(exitos), 1), 2),
            'media_pedido': round(sum(l.get('valor_pedido', 0) or 0 for l in exitos) / max(len(exitos), 1), 2),
            'media_obtido': round(sum(l.get('valor_obtido', 0) or 0 for l in exitos) / max(len(exitos), 1), 2),
        }
        padroes_derrota = {
            'total': len(derrotas),
            'media_pedido': round(sum(l.get('valor_pedido', 0) or 0 for l in derrotas) / max(len(derrotas), 1), 2),
            'media_obtido': round(sum(l.get('valor_obtido', 0) or 0 for l in derrotas) / max(len(derrotas), 1), 2),
        }

        return {'teses': teses, 'provas': provas, 'padroes_vitoria': padroes_vitoria, 'padroes_derrota': padroes_derrota}

    @staticmethod
    def get_risk_overview():
        lawsuits = get_all_lawsuits()
        risks = []
        for l in lawsuits:
            vp = l.get('valor_pedido', 0) or 0
            vo = l.get('valor_obtido', 0) or 0
            status = l['status']
            if status in ('acordo', 'sentenca_improcedente', 'sentenca_procedente', 'sentenca_parcial', 'arquivado'):
                nivel = 'Encerrado'
                score = 0
                prob = 0
                acao = 'Processo encerrado'
            elif vp > 100000:
                nivel = 'Crítico'
                score = 9
                prob = 70
                acao = 'Priorizar defesa técnica e considerar acordo estratégico'
            elif vp > 50000:
                nivel = 'Alto'
                score = 7
                prob = 50
                acao = 'Reforçar defesa e monitorar prazos'
            elif vp > 20000:
                nivel = 'Médio'
                score = 5
                prob = 30
                acao = 'Manter acompanhamento regular'
            else:
                nivel = 'Baixo'
                score = 3
                prob = 15
                acao = 'Acompanhamento padrão'

            risks.append({
                'processo': {'numero': l['numero_processo'], 'reclamante': l['reclamante'],
                             'status': status, 'valor_pedido': vp},
                'nivel': nivel, 'score_risco': score, 'risco_financeiro': vp,
                'probabilidade_perda': prob, 'acao': acao,
            })
        risks.sort(key=lambda x: x['score_risco'], reverse=True)
        return risks

    @staticmethod
    def get_competitive_dashboard():
        lawsuits = get_all_lawsuits()
        total = len(lawsuits)
        if total == 0:
            return {'taxa_exito_geral': 0, 'taxa_reducao_geral': 0, 'total_economia': 0,
                    'valor_medio_acordo': 0, 'faixas_acordos': []}
        encerrados = [l for l in lawsuits if l['status'] != 'em_andamento']
        exitos = [l for l in encerrados if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial')]
        total_pedido = sum(l.get('valor_pedido', 0) or 0 for l in lawsuits)
        total_obtido = sum(l.get('valor_obtido', 0) or 0 for l in lawsuits)
        economia = sum(l.get('economia_processual', 0) or 0 for l in lawsuits)
        acordos = [l for l in lawsuits if l['status'] == 'acordo' and l.get('valor_obtido')]
        valor_medio_acordo = round(sum(l['valor_obtido'] for l in acordos) / max(len(acordos), 1), 2)

        faixas = [
            {'faixa': 'Até R$ 5.000', 'min': 0, 'max': 5000, 'count': 0},
            {'faixa': 'R$ 5.001 - R$ 15.000', 'min': 5001, 'max': 15000, 'count': 0},
            {'faixa': 'R$ 15.001 - R$ 30.000', 'min': 15001, 'max': 30000, 'count': 0},
            {'faixa': 'R$ 30.001 - R$ 50.000', 'min': 30001, 'max': 50000, 'count': 0},
            {'faixa': 'Acima de R$ 50.000', 'min': 50001, 'max': float('inf'), 'count': 0},
        ]
        for a in acordos:
            val = a['valor_obtido']
            for f in faixas:
                if f['min'] <= val <= f['max']:
                    f['count'] += 1
                    break

        return {
            'taxa_exito_geral': round(len(exitos) / max(len(encerrados), 1) * 100, 1),
            'taxa_reducao_geral': round(economia / max(total_pedido, 1) * 100, 1),
            'total_economia': round(economia, 2),
            'valor_medio_acordo': valor_medio_acordo,
            'faixas_acordos': [{'faixa': f['faixa'], 'count': f['count']} for f in faixas],
        }

    @staticmethod
    def get_judge_ranking():
        lawsuits = get_all_lawsuits()
        judges = get_all_judges()
        result = []
        for j in judges:
            jl = [l for l in lawsuits if l.get('judge_id') == j['id']]
            if not jl:
                continue
            total = len(jl)
            acordos = len([l for l in jl if l['status'] == 'acordo'])
            exitos = len([l for l in jl if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial')])
            eco = sum(l.get('economia_processual', 0) or 0 for l in jl)
            tp = sum(l.get('valor_pedido', 0) or 0 for l in jl)
            result.append({
                'judge_name': j['name'], 'vara': j['vara'], 'total_processos': total,
                'taxa_acordo': round(acordos / total * 100, 1),
                'taxa_exito': round(exitos / total * 100, 1),
                'taxa_reducao': round(eco / max(tp, 1) * 100, 1),
                'economia_total': round(eco, 2),
            })
        return sorted(result, key=lambda x: x['taxa_exito'], reverse=True)

    @staticmethod
    def get_thesis_ranking():
        lawsuits = get_all_lawsuits()
        teses_map = {}
        for l in lawsuits:
            tese = l.get('tese_defesa', '') or ''
            if not tese or len(tese) < 5:
                continue
            key = tese[:80]
            if key not in teses_map:
                teses_map[key] = {'tese': tese[:120], 'total': 0, 'exitos': 0, 'economia_total': 0, 'total_pedido': 0}
            teses_map[key]['total'] += 1
            teses_map[key]['total_pedido'] += (l.get('valor_pedido', 0) or 0)
            if l['status'] in ('acordo', 'sentenca_improcedente', 'sentenca_parcial'):
                teses_map[key]['exitos'] += 1
                teses_map[key]['economia_total'] += (l.get('economia_processual', 0) or 0)

        result = []
        for v in teses_map.values():
            v['taxa_sucesso'] = round(v['exitos'] / max(v['total'], 1) * 100, 1)
            v['taxa_reducao'] = round(v['economia_total'] / max(v['total_pedido'], 1) * 100, 1)
            result.append(v)
        return sorted(result, key=lambda x: x['taxa_sucesso'], reverse=True)
