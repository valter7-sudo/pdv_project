# backend/routes/relatorios.py

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.models import Venda, ItemVenda, Produto, MovimentacaoEstoque
from backend.utils.permissoes import requer_perfil
from backend import db

relatorios_bp = Blueprint("relatorios", __name__)

# ============================
# RELATÓRIO: VENDAS POR DIA
# ============================
@relatorios_bp.route("/vendas_por_dia", methods=["GET"])
@requer_perfil("gerente", "operador")
def vendas_por_dia():
    vendas = (
        db.session.query(
            func.date(Venda.data_hora).label("dia"),
            func.sum(Venda.total).label("total")
        )
        .group_by(func.date(Venda.data_hora))
        .order_by(func.date(Venda.data_hora))
        .all()
    )

    resultado = [
        {"dia": str(v.dia), "total": float(v.total)}
        for v in vendas
    ]

    return jsonify(resultado), 200


# ============================
# RELATÓRIO: TOTALIZADOR GERAL
# ============================
@relatorios_bp.route("/totalizador", methods=["GET"])
@requer_perfil("gerente")
def totalizador():
    total_vendas = db.session.query(func.sum(Venda.total)).scalar() or 0
    quantidade_vendas = db.session.query(func.count(Venda.id)).scalar() or 0

    return jsonify({
        "total_vendido": float(total_vendas),
        "quantidade_vendas": quantidade_vendas
    }), 200


# ============================
# RELATÓRIO: PRODUTOS MAIS VENDIDOS
# ============================
@relatorios_bp.route("/produtos_mais_vendidos", methods=["GET"])
@requer_perfil("gerente", "operador")
def produtos_mais_vendidos():
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

    resultado = [
        {"produto": nome, "quantidade_vendida": int(total)}
        for nome, total in dados
    ]

    return jsonify(resultado), 200


# ============================
# RELATÓRIO: MOVIMENTAÇÃO DE ESTOQUE
# ============================
@relatorios_bp.route("/estoque", methods=["GET"])
@requer_perfil("gerente")
def relatorio_estoque():
    movimentos = MovimentacaoEstoque.query.order_by(MovimentacaoEstoque.data_hora.desc()).all()

    resultado = [
        {
            "produto": mov.produto.nome,
            "tipo": mov.tipo,
            "quantidade": mov.quantidade,
            "motivo": mov.motivo,
            "data_hora": mov.data_hora.isoformat(),
            "usuario": mov.usuario.nome
        }
        for mov in movimentos
    ]

    return jsonify(resultado), 200
