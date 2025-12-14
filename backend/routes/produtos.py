# backend/routes/produtos.py

from flask import Blueprint, request, jsonify
from backend.models import Produto, LogAuditoria
from backend import db
from backend.utils.permissoes import requer_token, requer_perfil, usuario_logado

produtos_bp = Blueprint("produtos", __name__)

# ============================
# LISTAR PRODUTOS
# ============================
@produtos_bp.route("/", methods=["GET"])
@requer_token
def listar_produtos():
    produtos = Produto.query.all()

    lista = [
        {
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "preco": p.preco,
            "quantidade": p.quantidade
        }
        for p in produtos
    ]

    return jsonify(lista), 200


# ============================
# CADASTRAR PRODUTO
# ============================
@produtos_bp.route("/", methods=["POST"])
@requer_perfil("gerente", "operador")
def cadastrar_produto():
    dados = request.get_json()

    codigo = dados.get("codigo")
    nome = dados.get("nome")
    preco = dados.get("preco")
    quantidade = dados.get("quantidade", 0)

    if not codigo or not nome or preco is None:
        return jsonify({"erro": "Campos obrigatórios: codigo, nome, preco"}), 400

    if Produto.query.filter_by(codigo=codigo).first():
        return jsonify({"erro": "Já existe um produto com este código"}), 400

    produto = Produto(
        codigo=codigo,
        nome=nome,
        preco=preco,
        quantidade=quantidade
    )

    db.session.add(produto)
    db.session.commit()

    # Auditoria
    usuario = usuario_logado()
    log = LogAuditoria(
        acao="Cadastro de produto",
        detalhes=f"Produto {nome} (código {codigo}) cadastrado",
        usuario_id=usuario.id
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"mensagem": "Produto cadastrado com sucesso"}), 201


# ============================
# ATUALIZAR PRODUTO
# ============================
@produtos_bp.route("/<int:id>", methods=["PUT"])
@requer_perfil("gerente", "operador")
def atualizar_produto(id):
    produto = Produto.query.get(id)

    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    dados = request.get_json()

    produto.nome = dados.get("nome", produto.nome)
    produto.preco = dados.get("preco", produto.preco)
    produto.quantidade = dados.get("quantidade", produto.quantidade)

    db.session.commit()

    # Auditoria
    usuario = usuario_logado()
    log = LogAuditoria(
        acao="Atualização de produto",
        detalhes=f"Produto {produto.nome} atualizado",
        usuario_id=usuario.id
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"mensagem": "Produto atualizado com sucesso"}), 200


# ============================
# EXCLUIR PRODUTO
# ============================
@produtos_bp.route("/<int:id>", methods=["DELETE"])
@requer_perfil("gerente")
def excluir_produto(id):
    produto = Produto.query.get(id)

    if not produto:
        return jsonify({"erro": "Produto não encontrado"}), 404

    db.session.delete(produto)
    db.session.commit()

    # Auditoria
    usuario = usuario_logado()
    log = LogAuditoria(
        acao="Exclusão de produto",
        detalhes=f"Produto {produto.nome} excluído",
        usuario_id=usuario.id
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"mensagem": "Produto excluído com sucesso"}), 200
