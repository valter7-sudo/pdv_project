# backend/routes/products.py
"""
Rotas de API para gerenciamento de produtos (controle de estoque).
Permite listar, criar, atualizar e remover produtos.
"""

from flask import Blueprint, request, jsonify
from backend import db
from backend.models import Product, AuditLog
from datetime import datetime

products_bp = Blueprint("products_bp", __name__, url_prefix="/api/products")


# 🧾 Listar produtos (com busca opcional)
@products_bp.route("/", methods=["GET"])
def list_products():
    """Retorna todos os produtos ou busca por código/nome."""
    search = request.args.get("q", "").strip()
    if search:
        products = Product.query.filter(
            (Product.name.ilike(f"%{search}%")) | (Product.code.ilike(f"%{search}%"))
        ).all()
    else:
        products = Product.query.all()

    data = [
        {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "price": p.price,
            "quantity": p.quantity,
        }
        for p in products
    ]
    return jsonify(data), 200


# ➕ Adicionar novo produto
@products_bp.route("/", methods=["POST"])
def add_product():
    """Adiciona um novo produto ao estoque."""
    data = request.get_json() or {}

    if not data.get("code") or not data.get("name"):
        return jsonify({"error": "Campos obrigatórios: code e name"}), 400

    # Evita duplicidade de código
    if Product.query.filter_by(code=data["code"]).first():
        return jsonify({"error": "Código de produto já cadastrado"}), 409

    new_product = Product(
        code=data["code"].strip(),
        name=data["name"].strip(),
        price=float(data.get("price", 0)),
        quantity=int(data.get("quantity", 0)),
        created_at=datetime.utcnow(),
    )

    db.session.add(new_product)
    db.session.commit()

    # Log de auditoria
    log = AuditLog(
        action="ADD_PRODUCT",
        details=f"Produto '{new_product.name}' ({new_product.code}) adicionado.",
        timestamp=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Produto adicionado com sucesso!"}), 201


# ✏️ Atualizar produto existente
@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    """Atualiza informações de um produto existente."""
    data = request.get_json() or {}
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    product.name = data.get("name", product.name)
    product.price = float(data.get("price", product.price))
    product.quantity = int(data.get("quantity", product.quantity))

    db.session.commit()

    log = AuditLog(
        action="UPDATE_PRODUCT",
        details=f"Produto '{product.name}' atualizado (ID: {product.id})",
        timestamp=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Produto atualizado com sucesso!"}), 200


# 🗑️ Excluir produto
@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    """Remove um produto do estoque."""
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Produto não encontrado"}), 404

    db.session.delete(product)
    db.session.commit()

    log = AuditLog(
        action="DELETE_PRODUCT",
        details=f"Produto '{product.name}' (ID: {product.id}) removido do sistema.",
        timestamp=datetime.utcnow(),
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({"message": "Produto excluído com sucesso!"}), 200