from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from backend import db
from backend.models import Venda
from sqlalchemy import func
import io

def pdf_relatorio_vendas():
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 800, "Relatório de Vendas")

    pdf.setFont("Helvetica", 12)

    vendas = (
        db.session.query(
            func.date(Venda.data_hora).label("dia"),
            func.sum(Venda.total).label("total")
        )
        .group_by(func.date(Venda.data_hora))
        .order_by(func.date(Venda.data_hora))
        .all()
    )

    y = 760
    for v in vendas:
        pdf.drawString(50, y, f"{v.dia}: R$ {float(v.total):.2f}")
        y -= 20

        if y < 50:
            pdf.showPage()
            y = 800

    pdf.save()
    buffer.seek(0)
    return buffer

