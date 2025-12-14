import io
import matplotlib.pyplot as plt
from backend import db
from backend.models import Venda, ItemVenda, Produto
from sqlalchemy import func

def grafico_vendas_por_dia():
    dados = (
        db.session.query(
            func.date(Venda.data_hora).label("dia"),
            func.sum(Venda.total).label("total")
        )
        .group_by(func.date(Venda.data_hora))
        .order_by(func.date(Venda.data_hora))
        .all()
    )

    dias = [str(d.dia) for d in dados]
    totais = [float(d.total) for d in dados]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(dias, totais, marker="o")
    ax.set_title("Vendas por Dia")
    ax.set_xlabel("Dia")
    ax.set_ylabel("Total (R$)")
    ax.grid(True)

    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer


def grafico_produtos_mais_vendidos():
    dados = (
        db.session.query(
            Produto.nome,
            func.sum(ItemVenda.quantidade).label("total_vendido")
        )
        .join(ItemVenda, Produto.id == ItemVenda.produto_id)
        .group_by(Produto.id)
        .order_by(func.sum(ItemVenda.quantidade).desc())
        .all()
    )

    nomes = [d[0] for d in dados]
    quantidades = [int(d[1]) for d in dados]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(nomes, quantidades)
    ax.set_title("Produtos Mais Vendidos")
    ax.set_xlabel("Produto")
    ax.set_ylabel("Quantidade")
    plt.xticks(rotation=45, ha="right")

    buffer = io.BytesIO()
    plt.tight_layout()
    fig.savefig(buffer, format="png")
    buffer.seek(0)
    return buffer

from flask import send_file
from backend.routes.relatorios import relatorios_bp
from backend.relatorios.graficos import grafico_vendas_por_dia, grafico_produtos_mais_vendidos
from backend.relatorios.pdfs import pdf_relatorio_vendas
from backend.utils.auth import requer_perfil

@relatorios_bp.route("/grafico_vendas", methods=["GET"])
@requer_perfil("gerente")
def grafico_vendas():
    buffer = grafico_vendas_por_dia()
    return send_file(buffer, mimetype="image/png", download_name="vendas_por_dia.png")

@relatorios_bp.route("/grafico_produtos", methods=["GET"])
@requer_perfil("gerente")
def grafico_produtos():
    buffer = grafico_produtos_mais_vendidos()
    return send_file(buffer, mimetype="image/png", download_name="produtos_mais_vendidos.png")

@relatorios_bp.route("/pdf_vendas", methods=["GET"])
@requer_perfil("gerente")
def pdf_vendas():
    buffer = pdf_relatorio_vendas()
    return send_file(buffer, mimetype="application/pdf", download_name="relatorio_vendas.pdf")
