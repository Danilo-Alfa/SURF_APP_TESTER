from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from datetime import datetime

class PDFReporter:
    @staticmethod
    def gerar(resultados, aprovado, motivos, fase="E2E"):
        os.makedirs("storage", exist_ok=True)
        filename = f"storage/relatorio_teste_{fase}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # --- Estilos ---
        title_style = ParagraphStyle('TitleCustom', parent=styles['Title'], fontSize=24, textColor=colors.HexColor("#0f172a"), spaceAfter=20)
        h2_style = ParagraphStyle('H2Custom', parent=styles['Heading2'], fontSize=16, textColor=colors.HexColor("#0ea5e9"), spaceBefore=15, borderBottomWidth=1, borderColor=colors.HexColor("#e2e8f0"))
        code_style = ParagraphStyle('Code', parent=styles['Normal'], fontName='Courier', fontSize=8, backColor=colors.HexColor("#f1f5f9"), borderPadding=5)
        
        # --- Cabeçalho ---
        story.append(Paragraph("SURF APP TESTER", title_style))
        story.append(Paragraph(f"Relatório de Qualidade - Fase {fase}", styles['Heading3']))
        story.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # --- Status ---
        status_text = "APROVADO" if aprovado else "REPROVADO"
        status_bg = colors.green if aprovado else colors.red
        
        t_status = Table([["Status Final", status_text]], colWidths=[3*inch, 3*inch])
        t_status.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor("#f1f5f9")),
            ('BACKGROUND', (1, 0), (1, 0), status_bg),
            ('TEXTCOLOR', (1, 0), (1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('PADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(t_status)
        story.append(Spacer(1, 20))
        
        # --- Resumo ---
        story.append(Paragraph("Resumo da Execução", h2_style))
        total = resultados.get('total_testes', 0)
        passed = resultados.get('aprovados', 0)
        failed = total - passed
        coverage = (passed / total * 100) if total > 0 else 0
        
        data_resumo = [
            ["Total", "Aprovados", "Falhas", "Cobertura"],
            [str(total), str(passed), str(failed), f"{coverage:.1f}%"]
        ]
        
        t_resumo = Table(data_resumo, colWidths=[1.5*inch]*4)
        t_resumo.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
        ]))
        story.append(t_resumo)
        story.append(Spacer(1, 20))
        
        # --- Detalhamento de Erros ---
        lista_falhas = resultados.get('lista_falhas', [])
        if lista_falhas:
            story.append(Paragraph(f"Detalhamento de Erros ({len(lista_falhas)})", h2_style))
            
            for falha in lista_falhas:
                # Título do erro
                story.append(Paragraph(f"🔴 {falha['teste']}", styles['Heading4']))
                
                # Tabela de info
                data_falha = [
                    ["Severidade:", falha['severidade']],
                    ["Mensagem:", Paragraph(falha['mensagem'], styles['Normal'])],
                    ["Classe:", falha['classe']]
                ]
                t_falha = Table(data_falha, colWidths=[1.2*inch, 4.8*inch])
                t_falha.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#fef2f2")),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ]))
                story.append(t_falha)
                
                # Traceback técnico
                if falha.get('detalhes'):
                    story.append(Spacer(1, 5))
                    # Corta traceback muito longo
                    trace = falha['detalhes'][:800] + "..." if len(falha['detalhes']) > 800 else falha['detalhes']
                    story.append(Paragraph(trace.replace("\n", "<br/>"), code_style))
                
                story.append(Spacer(1, 10))
        
        # --- Motivos do Quality Gate ---
        if motivos:
            story.append(Paragraph("Critérios de Aceite / Motivos", h2_style))
            for motivo in motivos:
                icon = "✅" if "APROVADO" in motivo else "⚠️"
                if "[CÓDIGO]" in motivo: icon = "🔒"
                story.append(Paragraph(f"{icon} {motivo}", styles['Normal']))
                story.append(Spacer(1, 4))
        
        story.append(Spacer(1, 20))

        # --- Tabela Completa de Testes (Solicitação do Usuário) ---
        lista_testes = resultados.get('lista_testes', [])
        if lista_testes:
            story.append(PageBreak())
            story.append(Paragraph("Relatório Detalhado de Todos os Testes", h2_style))
            story.append(Spacer(1, 10))
            
            # Cabeçalho da tabela
            data_full = [["Status", "Teste", "Descrição"]]
            
            for teste in lista_testes:
                status_icon = "✅" if teste['status'] == "APROVADO" else "❌"
                # Limita tamanho do nome
                nome = (teste['name'][:40] + '..') if len(teste['name']) > 40 else teste['name']
                desc = Paragraph(teste.get('description', '-'), styles['Normal'])
                data_full.append([status_icon, nome, desc])
            
            t_full = Table(data_full, colWidths=[0.8*inch, 2.5*inch, 4.0*inch])
            t_full.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(t_full)

        # --- Screenshot ---
        screenshot_path = "storage/screenshot_final.png"
        if os.path.exists(screenshot_path):
            story.append(PageBreak())
            story.append(Paragraph("Evidência Visual (Screenshot)", h2_style))
            try:
                # Ajusta imagem para caber na página
                img = Image(screenshot_path, width=4*inch, height=7*inch, kind='proportional')
                story.append(img)
            except:
                story.append(Paragraph("Imagem encontrada mas não pôde ser carregada.", styles['Normal']))

        doc.build(story)
        return f"/storage/relatorio_teste_{fase}.pdf"