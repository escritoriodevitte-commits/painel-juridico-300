"""
Exportador PDF - Geração de peças e relatórios em PDF via ReportLab
"""
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.colors import HexColor, grey
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFExporter:
    @staticmethod
    def is_available() -> bool:
        return REPORTLAB_AVAILABLE

    def exportar_peca(self, conteudo: str, tipo: str, processo: dict, filepath: str):
        """Exporta peça jurídica para PDF formatado"""
        if not REPORTLAB_AVAILABLE:
            # Fallback: salvar como TXT
            with open(filepath.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(conteudo)
            return

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                leftMargin=3*cm, rightMargin=3*cm,
                                topMargin=2.5*cm, bottomMargin=2.5*cm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='PecaTitulo', parent=styles['Title'],
                                  fontSize=16, spaceAfter=20, alignment=TA_CENTER,
                                  textColor=HexColor('#1a1a2e')))
        styles.add(ParagraphStyle(name='PecaSubtitulo', parent=styles['Heading2'],
                                  fontSize=12, spaceAfter=10, spaceBefore=15,
                                  textColor=HexColor('#16213e'), alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='PecaCorpo', parent=styles['Normal'],
                                  fontSize=11, leading=16, spaceAfter=8,
                                  alignment=TA_JUSTIFY, firstLineIndent=40))

        elements = []
        # Cabeçalho
        elements.append(Paragraph(f"Processo: {processo.get('numero_processo', '-')}", styles['PecaCorpo']))
        elements.append(Paragraph(f"Reclamante: {processo.get('reclamante', '-')} x Reclamada: {processo.get('reclamada', '-')}", styles['PecaCorpo']))
        elements.append(Spacer(1, 15))

        for line in conteudo.split('\n'):
            stripped = line.strip()
            if not stripped:
                elements.append(Spacer(1, 6))
                continue
            if stripped.startswith('=' * 10) or stripped.startswith('-' * 10):
                continue
            if stripped.startswith('[NOTA INTERNA') or stripped.startswith('[Gerado'):
                continue
            if (stripped.startswith('I ') or stripped.startswith('II ') or stripped.startswith('III ') or
                stripped.startswith('IV ') or stripped.startswith('V ') or stripped.startswith('VI ') or
                stripped.startswith('VII ') or stripped.startswith('VIII ') or
                stripped.startswith('DOS ') or stripped.startswith('DA ') or stripped.startswith('DO ') or
                (stripped.upper() == stripped and len(stripped) > 5)):
                elements.append(Paragraph(stripped, styles['PecaSubtitulo']))
            else:
                # Escapar caracteres especiais para ReportLab
                safe = stripped.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                elements.append(Paragraph(safe, styles['PecaCorpo']))

        doc.build(elements)

    def exportar_calculo(self, resultado: dict, filepath: str):
        """Exporta cálculo de verbas trabalhistas para PDF"""
        if not REPORTLAB_AVAILABLE:
            with open(filepath.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write(str(resultado))
            return

        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                leftMargin=2.5*cm, rightMargin=2.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='VTitulo', parent=styles['Title'],
                                  fontSize=16, spaceAfter=20, alignment=TA_CENTER,
                                  textColor=HexColor('#0f3460')))
        styles.add(ParagraphStyle(name='VSecao', parent=styles['Heading2'],
                                  fontSize=12, spaceAfter=8, spaceBefore=12,
                                  textColor=HexColor('#16213e')))
        styles.add(ParagraphStyle(name='VCorpo', parent=styles['Normal'],
                                  fontSize=10, leading=14, spaceAfter=4))

        elements = []
        elements.append(Paragraph("CALCULO DE VERBAS TRABALHISTAS", styles['VTitulo']))
        elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['VCorpo']))
        elements.append(Spacer(1, 15))

        # Totais
        totais = resultado.get('totais', {})
        elements.append(Paragraph("RESUMO", styles['VSecao']))
        summary_data = [
            ['Indicador', 'Valor'],
            ['Total Bruto', f"R$ {totais.get('total_bruto', 0):,.2f}"],
            ['Total Descontos', f"R$ {totais.get('total_descontos', 0):,.2f}"],
            ['Total Liquido', f"R$ {totais.get('total_liquido', 0):,.2f}"],
            ['FGTS + Multa', f"R$ {totais.get('total_fgts', 0):,.2f}"],
        ]
        t = Table(summary_data, colWidths=[200, 250])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
            ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, grey),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        # Verbas
        verbas = resultado.get('verbas', [])
        if verbas:
            elements.append(Paragraph("VERBAS RESCISORIAS", styles['VSecao']))
            verbas_data = [['Descricao', 'Valor', 'Fundamento']]
            for v in verbas:
                verbas_data.append([
                    v.get('descricao', '-'),
                    f"R$ {v.get('valor', 0):,.2f}",
                    v.get('fundamento', '-')[:40]
                ])
            t2 = Table(verbas_data, colWidths=[200, 100, 150])
            t2.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0f3460')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f8f9fa'), HexColor('#ffffff')]),
            ]))
            elements.append(t2)
            elements.append(Spacer(1, 15))

        # Descontos
        descontos = resultado.get('descontos', [])
        if descontos:
            elements.append(Paragraph("DESCONTOS", styles['VSecao']))
            desc_data = [['Descricao', 'Valor']]
            for d in descontos:
                desc_data.append([d.get('descricao', '-'), f"R$ {d.get('valor', 0):,.2f}"])
            t3 = Table(desc_data, colWidths=[300, 150])
            t3.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), HexColor('#c0392b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, grey),
            ]))
            elements.append(t3)

        doc.build(elements)
