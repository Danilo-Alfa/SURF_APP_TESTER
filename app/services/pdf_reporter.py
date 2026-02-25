from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
import os
from datetime import datetime
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from xml.sax.saxutils import escape

class PDFReporter:
    @staticmethod
    def gerar(resultados, aprovado, motivos, fase="E2E"):
        os.makedirs("storage", exist_ok=True)
        filename = f"storage/relatorio_teste_{fase}.pdf"
        
        # Margens mais largas para aspecto profissional
        doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=20*mm)
        
        styles = getSampleStyleSheet()
        story = []
        
        # --- Paleta de Cores Corporativa (Audit Style) ---
        COLOR_PRIMARY = colors.HexColor("#1e293b")   # Slate 800 (Titulos)
        COLOR_ACCENT = colors.HexColor("#3b82f6")    # Blue 500 (Destaques)
        COLOR_BG_HEADER = colors.HexColor("#f1f5f9") # Slate 100 (Fundo tabelas)
        COLOR_TEXT = colors.HexColor("#334155")      # Slate 700 (Texto corpo)
        COLOR_S1 = colors.HexColor("#dc2626")        # Red 600
        COLOR_S2 = colors.HexColor("#f59e0b")        # Amber 500
        COLOR_BORDER = colors.HexColor("#cbd5e1")    # Slate 300
        
        # --- Estilos Personalizados ---
        style_cover_title = ParagraphStyle('CoverTitle', parent=styles['Title'], fontSize=28, textColor=COLOR_PRIMARY, spaceAfter=10, alignment=TA_CENTER)
        style_cover_sub = ParagraphStyle('CoverSub', parent=styles['Normal'], fontSize=14, textColor=colors.gray, alignment=TA_CENTER)
        
        style_h1 = ParagraphStyle('H1Corp', parent=styles['Heading1'], fontSize=18, textColor=COLOR_PRIMARY, spaceBefore=20, spaceAfter=10, borderPadding=5)
        style_h2 = ParagraphStyle('H2Corp', parent=styles['Heading2'], fontSize=14, textColor=COLOR_ACCENT, spaceBefore=15, spaceAfter=8)
        
        style_normal = ParagraphStyle('BodyCorp', parent=styles['Normal'], fontSize=10, textColor=COLOR_TEXT, leading=14)
        style_small = ParagraphStyle('SmallCorp', parent=styles['Normal'], fontSize=8, textColor=COLOR_TEXT)
        style_code = ParagraphStyle('CodeCorp', parent=styles['Normal'], fontName='Courier', fontSize=8, backColor=colors.whitesmoke, borderPadding=6, leading=10)
        
        # =================================================================================
        # 1. CAPA
        # =================================================================================
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("RELATÓRIO DE AUDITORIA DE QA", style_cover_title))
        story.append(Paragraph("SURF APP TESTER PLATFORM", style_cover_sub))
        story.append(Spacer(1, 1*inch))
        
        # Status Grande na Capa
        status_text = "APROVADO" if aprovado else "REPROVADO"
        status_color = colors.green if aprovado else COLOR_S1
        
        t_status_cover = Table([[status_text]], colWidths=[4*inch])
        t_status_cover.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('TEXTCOLOR', (0,0), (-1,-1), status_color),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 32),
            ('BOX', (0,0), (-1,-1), 2, status_color),
            ('TOPPADDING', (0,0), (-1,-1), 20),
            ('BOTTOMPADDING', (0,0), (-1,-1), 20),
        ]))
        story.append(t_status_cover)
        
        story.append(Spacer(1, 2*inch))
        
        # Info do Projeto na Capa
        data_capa = [
            ["Data da Execução:", datetime.now().strftime('%d/%m/%Y às %H:%M')],
            ["Fase do Teste:", fase],
            ["Ambiente:", "Android / Appium Automation"],
            ["Versão da Plataforma:", "v2.4.0 (Enterprise)"]
        ]
        t_info = Table(data_capa, colWidths=[2*inch, 3*inch])
        t_info.setStyle(TableStyle([
            ('TEXTCOLOR', (0,0), (-1,-1), COLOR_TEXT),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_info)
        story.append(PageBreak())

        # =================================================================================
        # 2. RESUMO EXECUTIVO
        # =================================================================================
        story.append(Paragraph("1. Resumo Executivo", style_h1))
        
        # Métricas Principais
        total = resultados.get('total_testes', 0)
        passed = resultados.get('aprovados', 0)
        failed = total - passed
        coverage = (passed / total * 100) if total > 0 else 0
        s1_count = resultados.get('defeitos_s1', 0)
        s2_count = resultados.get('defeitos_s2', 0)
        
        # Grid de Métricas (2x2)
        data_metrics = [
            [f"{coverage:.1f}%", f"{total}", f"{s1_count}", f"{s2_count}"],
            ["Índice de Aprovação", "Total de Testes", "Falhas Críticas (S1)", "Falhas Médias (S2)"]
        ]
        
        t_metrics = Table(data_metrics, colWidths=[1.8*inch]*4)
        t_metrics.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 18),
            ('TEXTCOLOR', (0,0), (-1,0), COLOR_PRIMARY),
            ('TEXTCOLOR', (2,0), (2,0), COLOR_S1 if s1_count > 0 else COLOR_PRIMARY), # Vermelho se tiver S1
            ('FONTSIZE', (0,1), (-1,1), 9),
            ('TEXTCOLOR', (0,1), (-1,1), colors.gray),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
            ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ]))
        story.append(t_metrics)
        story.append(Spacer(1, 20))
        
        # Conclusão da IA
        sugestao_ia = resultados.get('sugestao_ia')
        if sugestao_ia:
            story.append(Paragraph("Parecer Técnico (IA Analysis)", style_h2))
            # Remove tags HTML simples para o PDF se necessário, ou usa estilos
            story.append(Paragraph(sugestao_ia, style_normal)) # Sugestão IA já vem com tags controladas (<b>)
        
        story.append(Spacer(1, 15))
        
        # Motivos do Quality Gate
        if motivos:
            story.append(Paragraph("Critérios de Decisão (Quality Gate)", style_h2))
            for motivo in motivos:
                bullet = "•"
                story.append(Paragraph(f"{bullet} {escape(motivo)}", style_normal))

        # =================================================================================
        # 3. TABELA DE FALHAS (ESTRATÉGICA)
        # =================================================================================
        lista_falhas = resultados.get('lista_falhas', [])
        if lista_falhas:
            story.append(PageBreak())
            story.append(Paragraph(f"2. Detalhamento de Não-Conformidades", style_h1))
            story.append(Paragraph("A tabela abaixo lista as falhas identificadas, categorizadas por impacto no negócio e com recomendações de correção.", style_normal))
            story.append(Spacer(1, 10))
            
            # Cabeçalho
            data_exec = [["ID / Cat.", "Severidade", "Descrição & Impacto", "Recomendação"]]
            
            for falha in lista_falhas:
                sev = falha['severidade']
                msg = falha['mensagem']
                teste_nome = falha['teste']
                desc_teste = falha.get('descricao', 'Verificação de segurança e qualidade.')
                
                # --- Lógica de Inferência de Categoria e Ação ---
                categoria = "Funcional"
                acao = "Investigar logs técnicos."
                impacto = "Possível instabilidade no uso do aplicativo."

                msg_lower = msg.lower()
                if "debug" in msg_lower: 
                    categoria = "Segurança"
                    acao = "Definir android:debuggable='false' no Manifesto."
                    impacto = "Permite engenharia reversa e acesso total aos dados internos."
                elif "backup" in msg_lower:
                    categoria = "Privacidade"
                    acao = "Definir android:allowBackup='false'."
                    impacto = "Dados do usuário podem ser extraídos via ADB."
                elif "assinatura" in msg_lower:
                    categoria = "Release"
                    acao = "Assinar APK com Keystore de produção."
                    impacto = "Impede a publicação na Google Play Store."
                elif "export" in msg_lower:
                    categoria = "Segurança"
                    acao = "Adicionar android:exported='false' ou permissões."
                    impacto = "Outros apps podem lançar telas internas indevidamente."
                elif "performance" in msg_lower or "frames" in msg_lower:
                    categoria = "Performance"
                    acao = "Otimizar layouts e reduzir operações na Main Thread."
                    impacto = "Lentidão perceptível (Jank) afeta a experiência do usuário."
                
                # Formatação da Célula de Descrição
                cell_desc = [
                    Paragraph(f"<b>{teste_nome}</b>", style_small),
                    Paragraph(f"<i>{desc_teste}</i>", style_small),
                    Spacer(1, 4),
                    Paragraph(f"<b>Erro:</b> {escape(msg)}", style_normal),
                    Spacer(1, 4),
                    Paragraph(f"<b>Impacto:</b> {impacto}", style_small)
                ]
                
                data_exec.append([
                    Paragraph(f"{categoria}", style_small),
                    Paragraph(f"<b>{sev}</b>", style_normal),
                    cell_desc,
                    Paragraph(acao, style_small)
                ])

            # Larguras: ID/Cat (1.2), Sev (0.6), Desc (3.5), Rec (2.0)
            t_exec = Table(data_exec, colWidths=[1.0*inch, 0.6*inch, 3.7*inch, 2.0*inch])
            t_exec.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
                
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ]))
            
            # Colore a coluna de severidade condicionalmente
            for i, row in enumerate(lista_falhas):
                row_idx = i + 1
                sev = row['severidade']
                bg_color = COLOR_S1 if sev == "S1" else (COLOR_S2 if sev == "S2" else colors.white)
                text_color = colors.white if sev in ["S1", "S2"] else colors.black
                t_exec.setStyle(TableStyle([
                    ('BACKGROUND', (1, row_idx), (1, row_idx), bg_color),
                    ('TEXTCOLOR', (1, row_idx), (1, row_idx), text_color),
                    ('ALIGN', (1, row_idx), (1, row_idx), 'CENTER'),
                    ('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'),
                ]))

            story.append(t_exec)
        else:
            story.append(Paragraph("Nenhuma falha impeditiva encontrada.", style_normal))

        # =================================================================================
        # 4. APÊNDICE TÉCNICO
        # =================================================================================
        if lista_falhas:
            story.append(PageBreak())
            story.append(Paragraph("3. Apêndice Técnico (Logs)", style_h1))
            story.append(Paragraph("Esta seção contém os stack traces originais para depuração pela equipe de desenvolvimento.", style_normal))
            story.append(Spacer(1, 10))
            
            for falha in lista_falhas:
                # Bloco KeepTogether para não quebrar título e log em páginas diferentes
                content = []
                content.append(Paragraph(f"🔴 {falha['teste']} ({falha['severidade']})", style_h2))
                
                detalhes = falha.get('detalhes', 'Sem logs disponíveis.')
                # Limita tamanho para não explodir o PDF
                if len(detalhes) > 2000: detalhes = detalhes[:2000] + "\n[... LOG TRUNCADO ...]"
                
                content.append(Paragraph(escape(detalhes).replace("\n", "<br/>"), style_code))
                content.append(Spacer(1, 15))
                story.append(KeepTogether(content))

        # =================================================================================
        # 5. EVIDÊNCIAS VISUAIS
        # =================================================================================
        screenshot_path = "storage/screenshot_final.png"
        if os.path.exists(screenshot_path):
            story.append(PageBreak())
            story.append(Paragraph("4. Evidências Visuais", style_h1))
            try:
                img = Image(screenshot_path, width=4*inch, height=7*inch, kind='proportional')
                t_img = Table([[img]], colWidths=[6*inch])
                t_img.setStyle(TableStyle([
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('BOX', (0,0), (-1,-1), 1, COLOR_BORDER),
                    ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ]))
                story.append(t_img)
                story.append(Paragraph("Figura 1: Estado final da interface durante o teste.", style_small))
            except:
                pass

        doc.build(story)
        return f"/storage/relatorio_teste_{fase}.pdf"