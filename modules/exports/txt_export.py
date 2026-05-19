"""Exportador TXT"""
import os
from datetime import datetime

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports_output")


class TXTExporter:
    @staticmethod
    def export_piece(conteudo: str, tipo: str) -> str:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(EXPORT_DIR, f"{tipo}_{timestamp}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return filepath

    @staticmethod
    def export_verbas(resultado: dict) -> str:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(EXPORT_DIR, f"calculo_verbas_{timestamp}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("  CÁLCULO DE VERBAS TRABALHISTAS\n")
            f.write("=" * 60 + "\n\n")
            dados = resultado.get('dados_contrato', {})
            f.write(f"Salário Base: R$ {dados.get('salario_base', 0):,.2f}\n")
            f.write(f"Admissão: {dados.get('data_admissao', '-')}\n")
            f.write(f"Demissão: {dados.get('data_demissao', '-')}\n")
            f.write(f"Tipo: {dados.get('tipo_rescisao', '-')}\n")
            f.write(f"Tempo de Serviço: {dados.get('tempo_servico', '-')}\n\n")
            f.write("-" * 60 + "\n")
            f.write("VERBAS:\n")
            for k, v in resultado.get('verbas', {}).items():
                if v and v > 0:
                    f.write(f"  {k.replace('_', ' ').title()}: R$ {v:,.2f}\n")
            f.write(f"\nTOTAL BRUTO: R$ {resultado.get('total_bruto', 0):,.2f}\n")
            f.write(f"DESCONTOS: R$ {resultado.get('total_descontos', 0):,.2f}\n")
            f.write(f"TOTAL LÍQUIDO: R$ {resultado.get('total_liquido', 0):,.2f}\n")
        return filepath

    @staticmethod
    def export_relatorio(metrics: dict, judge_ranking: list, thesis_ranking: list) -> str:
        os.makedirs(EXPORT_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(EXPORT_DIR, f"relatorio_estrategico_{timestamp}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("  RELATÓRIO ESTRATÉGICO PROCESSUAL\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Total Processos: {metrics.get('total_processos', 0)}\n")
            f.write(f"Taxa de Êxito: {metrics.get('taxa_exito', 0)}%\n")
            f.write(f"Taxa de Redução: {metrics.get('taxa_reducao', 0)}%\n")
            f.write(f"Economia Total: R$ {metrics.get('economia_total', 0):,.2f}\n\n")
            if judge_ranking:
                f.write("TOP MAGISTRADOS:\n")
                for j in judge_ranking[:10]:
                    f.write(f"  {j['judge_name']}: {j['taxa_exito']}% êxito, R$ {j['economia_total']:,.2f}\n")
            if thesis_ranking:
                f.write("\nTOP TESES:\n")
                for t in thesis_ranking[:10]:
                    f.write(f"  {t['tese'][:60]}: {t['taxa_sucesso']}% sucesso\n")
        return filepath
