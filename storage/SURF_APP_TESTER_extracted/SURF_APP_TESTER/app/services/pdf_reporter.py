# Arquivo: app/services/pdf_reporter.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

class PDFReporter:
    @staticmethod
    def gerar(dados: dict, aprovado: bool, motivos: list, fase: str) -> str:
        # Cria nome único e garante pasta
        filename = f"Report_{fase}_{datetime.now().strftime('%H%M%S')}.pdf"
        filepath = os.path.join("storage", filename)
        os.makedirs("storage", exist_ok=True)

        c = canvas.Canvas(filepath, pagesize=letter)
        
        # Título e Status
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, f"Relatório Quality Gate: {fase}")
        
        cor = "green" if aprovado else "red"
        status = "APROVADO" if aprovado else "REPROVADO"
        c.setFillColor(cor)
        c.drawString(50, 720, f"STATUS: {status}")
        
        # Dados
        c.setFillColor("black")
        c.setFont("Helvetica", 12)
        c.drawString(50, 680, f"Total Testes: {dados['total_testes']}")
        c.drawString(50, 660, f"Defeitos S1: {dados['defeitos_s1']}")
        c.drawString(50, 640, f"Defeitos S2: {dados['defeitos_s2']}")
        
        if not aprovado:
            c.drawString(50, 600, "Motivos da Reprovação:")
            y = 580
            for m in motivos:
                c.drawString(60, y, f"- {m}")
                y -= 20
        else:
            c.drawString(50, 600, "Mensagem: Pronto para promoção de fase.")

        c.save()
        return filepath