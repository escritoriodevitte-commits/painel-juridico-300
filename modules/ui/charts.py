#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Gráficos e Visualizações
Gera gráficos para dashboard usando matplotlib/plotly
"""

from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import json


class ChartGenerator:
    """
    Gerador de gráficos para dashboard
    
    Fornece gráficos para:
    - Taxa de vitória/sucesso
    - Timeline de processos
    - Distribuição por tipo
    - Análise de magistrados
    """
    
    def __init__(self):
        """Inicializa o gerador de gráficos"""
        self.colors = {
            'success': '#22c55e',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'accent': '#3b82f6',
            'gold': '#fbbf24'
        }
    
    def generate_win_rate_chart(self, lawsuits: List[Dict]) -> Dict:
        """
        Gera dados para gráfico de taxa de vitória
        
        Args:
            lawsuits: Lista de processos
        
        Returns:
            Dict com dados para gráfico (formato compatível com plotly/matplotlib)
        """
        statuses = {}
        for lawsuit in lawsuits:
            status = lawsuit.get('status', 'desconhecido')
            statuses[status] = statuses.get(status, 0) + 1
        
        # Mapear status para resultado
        victories = statuses.get('acordo', 0) + statuses.get('sentenca_procedente', 0) + statuses.get('sentenca_parcial', 0)
        defeats = statuses.get('sentenca_improcedente', 0)
        pending = statuses.get('em_andamento', 0)
        archived = statuses.get('arquivado', 0)
        
        total = len(lawsuits)
        
        return {
            'type': 'pie',
            'title': 'Taxa de Vitória/Sucesso',
            'labels': ['Vitórias', 'Derrotas', 'Em Andamento', 'Arquivados'],
            'values': [victories, defeats, pending, archived],
            'colors': [self.colors['success'], self.colors['danger'], 
                      self.colors['warning'], self.colors['accent']],
            'stats': {
                'total': total,
                'taxa_vitoria': f"{(victories/total*100):.1f}%" if total > 0 else "0%",
                'taxa_derrota': f"{(defeats/total*100):.1f}%" if total > 0 else "0%"
            }
        }
    
    def generate_timeline_chart(self, lawsuits: List[Dict]) -> Dict:
        """
        Gera dados para gráfico de timeline de processos
        
        Args:
            lawsuits: Lista de processos
        
        Returns:
            Dict com dados para gráfico de linha temporal
        """
        # Agrupar por mês
        monthly_data = {}
        
        for lawsuit in lawsuits:
            data_dist = lawsuit.get('data_distribuicao')
            if data_dist:
                try:
                    # Assumindo formato DD/MM/AAAA
                    parts = data_dist.split('/')
                    if len(parts) == 3:
                        year_month = f"{parts[2]}-{parts[1]}"
                        monthly_data[year_month] = monthly_data.get(year_month, 0) + 1
                except:
                    pass
        
        # Ordenar por data
        sorted_months = sorted(monthly_data.items())
        
        return {
            'type': 'line',
            'title': 'Timeline de Processos (por mês)',
            'x_labels': [m[0] for m in sorted_months],
            'y_values': [m[1] for m in sorted_months],
            'color': self.colors['accent'],
            'stats': {
                'total_meses': len(sorted_months),
                'media_por_mes': f"{sum(m[1] for m in sorted_months) / len(sorted_months):.1f}" if sorted_months else "0"
            }
        }
    
    def generate_type_distribution_chart(self, lawsuits: List[Dict]) -> Dict:
        """
        Gera dados para gráfico de distribuição por tipo de ação
        
        Args:
            lawsuits: Lista de processos
        
        Returns:
            Dict com dados para gráfico de barras
        """
        types = {}
        for lawsuit in lawsuits:
            # Inferir tipo pela tese ou categoria
            tese = lawsuit.get('tese_inicial', '').lower()
            
            if 'horas extras' in tese or 'hora' in tese:
                tipo = 'Horas Extras'
            elif 'justa causa' in tese:
                tipo = 'Justa Causa'
            elif 'acidente' in tese:
                tipo = 'Acidente de Trabalho'
            elif 'moral' in tese:
                tipo = 'Danos Morais'
            elif 'rescisão' in tese or 'rescissão' in tese:
                tipo = 'Rescisão'
            else:
                tipo = 'Outros'
            
            types[tipo] = types.get(tipo, 0) + 1
        
        return {
            'type': 'bar',
            'title': 'Distribuição por Tipo de Ação',
            'x_labels': list(types.keys()),
            'y_values': list(types.values()),
            'colors': [self.colors['accent']] * len(types),
            'stats': {
                'tipos_encontrados': len(types),
                'tipo_mais_comum': max(types.items(), key=lambda x: x[1])[0] if types else 'N/A'
            }
        }
    
    def generate_judge_performance_chart(self, judges: List[Dict], lawsuits: List[Dict]) -> Dict:
        """
        Gera dados para gráfico de desempenho de magistrados
        
        Args:
            judges: Lista de magistrados
            lawsuits: Lista de processos
        
        Returns:
            Dict com dados para gráfico
        """
        judge_stats = {}
        
        for judge in judges:
            judge_id = judge.get('id')
            judge_name = judge.get('name', f"Juiz {judge_id}")
            
            # Contar processos do juiz
            judge_lawsuits = [l for l in lawsuits if l.get('judge_id') == judge_id]
            
            if judge_lawsuits:
                victories = len([l for l in judge_lawsuits if l['status'] in ['acordo', 'sentenca_procedente']])
                total = len(judge_lawsuits)
                win_rate = (victories / total * 100) if total > 0 else 0
                
                judge_stats[judge_name] = {
                    'total': total,
                    'victories': victories,
                    'win_rate': f"{win_rate:.1f}%"
                }
        
        # Top 5 magistrados
        top_judges = sorted(judge_stats.items(), 
                           key=lambda x: x[1]['total'], reverse=True)[:5]
        
        return {
            'type': 'bar',
            'title': 'Desempenho dos Magistrados (Top 5)',
            'x_labels': [j[0] for j in top_judges],
            'y_values': [j[1]['total'] for j in top_judges],
            'y_label': 'Número de Processos',
            'colors': [self.colors['accent']] * len(top_judges),
            'stats': {
                'total_magistrados': len(judge_stats),
                'magistrados_com_processos': len(top_judges)
            }
        }
    
    def generate_financial_analysis_chart(self, lawsuits: List[Dict]) -> Dict:
        """
        Gera dados para gráfico de análise financeira
        
        Args:
            lawsuits: Lista de processos
        
        Returns:
            Dict com dados para gráfico
        """
        total_claimed = sum(float(l.get('valor_pedido', 0) or 0) for l in lawsuits)
        total_obtained = sum(float(l.get('valor_obtido', 0) or 0) for l in lawsuits)
        total_savings = total_claimed - total_obtained
        
        # Por status
        status_stats = {}
        for status in ['acordo', 'sentenca_procedente', 'sentenca_improcedente', 'em_andamento']:
            lawsuits_by_status = [l for l in lawsuits if l.get('status') == status]
            if lawsuits_by_status:
                claimed = sum(float(l.get('valor_pedido', 0) or 0) for l in lawsuits_by_status)
                obtained = sum(float(l.get('valor_obtido', 0) or 0) for l in lawsuits_by_status)
                status_stats[status] = {
                    'claimed': claimed,
                    'obtained': obtained,
                    'savings': claimed - obtained
                }
        
        return {
            'type': 'stacked_bar',
            'title': 'Análise Financeira por Status',
            'x_labels': list(status_stats.keys()),
            'y_values_1': [status_stats[s]['claimed'] for s in status_stats.keys()],
            'y_values_2': [status_stats[s]['obtained'] for s in status_stats.keys()],
            'labels': ['Valor Pedido', 'Valor Obtido'],
            'colors': [self.colors['danger'], self.colors['success']],
            'stats': {
                'total_reclamado': f"R$ {total_claimed:,.2f}",
                'total_obtido': f"R$ {total_obtained:,.2f}",
                'economia': f"R$ {total_savings:,.2f}",
                'reducao_media': f"{(total_savings/total_claimed*100):.1f}%" if total_claimed > 0 else "0%"
            }
        }
    
    def generate_status_trend_chart(self, lawsuits: List[Dict]) -> Dict:
        """
        Gera dados para gráfico de tendência de status
        
        Args:
            lawsuits: Lista de processos
        
        Returns:
            Dict com dados para gráfico
        """
        status_counts = {}
        for lawsuit in lawsuits:
            status = lawsuit.get('status', 'desconhecido')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Mapear status para label
        status_labels = {
            'em_andamento': 'Em Andamento',
            'acordo': 'Acordos',
            'sentenca_procedente': 'Sentenças Procedentes',
            'sentenca_improcedente': 'Sentenças Improcedentes',
            'sentenca_parcial': 'Sentenças Parciais',
            'arquivado': 'Arquivados'
        }
        
        labeled_stats = {
            status_labels.get(k, k): v for k, v in status_counts.items()
        }
        
        return {
            'type': 'doughnut',
            'title': 'Distribuição por Status',
            'labels': list(labeled_stats.keys()),
            'values': list(labeled_stats.values()),
            'colors': [
                self.colors['warning'],  # Em Andamento
                self.colors['success'],  # Acordos
                self.colors['success'],  # Procedentes
                self.colors['danger'],   # Improcedentes
                self.colors['accent'],   # Parciais
                self.colors['gold']      # Arquivados
            ][:len(labeled_stats)],
            'stats': {
                'total': sum(labeled_stats.values()),
                'maior_grupo': max(labeled_stats.items(), key=lambda x: x[1])[0] if labeled_stats else 'N/A'
            }
        }
    
    def generate_all_charts(self, lawsuits: List[Dict], judges: List[Dict]) -> Dict[str, Dict]:
        """
        Gera todos os gráficos
        
        Args:
            lawsuits: Lista de processos
            judges: Lista de magistrados
        
        Returns:
            Dict com todos os gráficos
        """
        return {
            'win_rate': self.generate_win_rate_chart(lawsuits),
            'timeline': self.generate_timeline_chart(lawsuits),
            'type_distribution': self.generate_type_distribution_chart(lawsuits),
            'judge_performance': self.generate_judge_performance_chart(judges, lawsuits),
            'financial': self.generate_financial_analysis_chart(lawsuits),
            'status_trend': self.generate_status_trend_chart(lawsuits)
        }
    
    def export_chart_data(self, charts: Dict[str, Dict]) -> str:
        """
        Exporta dados dos gráficos em JSON
        
        Args:
            charts: Dicionário com gráficos
        
        Returns:
            str: JSON com dados dos gráficos
        """
        export_data = {
            'export_date': datetime.now().isoformat(),
            'charts': charts
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
