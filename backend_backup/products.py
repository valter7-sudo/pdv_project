# backend/products.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import Product, AuditLog, User
from . import db


products_bp = Blueprint('products', __name__)




def audit(user_id, action, details=''):
a = AuditLog(user_id=user_id, action=action, details=details)
db.session.add(a)
db.session.commit()




def current_user():
identity = get_jwt_identity()
if not identity:
return None
return User.query.filter_by(username=identity).first()




@products_bp.route('/', methods=['GET'])
@jwt_required()
def list_products():
products = Product.query.all()
out = [{'id': p.id, 'code': p.code, 'name': p.name, 'price': p.price, 'quantity': p.quantity} for p in products]
return jsonify(out)




@products_bp.route('/', methods=['POST'])
@jwt_required()
def add_product():
user = current_user()
if user.role not in ('admin', 'buyer', 'operator'):
return jsonify({'msg': 'Permissão negada'}), 403


data = request.json or {}
code = data.get('code')
name = data.get('name')
price = float(data.get('price', 0.0))
quantity = int(data.get('quantity', 0))


if not code or not name:
return jsonify({'msg': 'code e name obrigatórios'}), 400
if Product.query.filter_by(code=code).first():
return jsonify({'msg': 'Produto com esse código já existe'}), 400


p = Product(code=code, name=name, price=price, quantity=quantity)
db.session.add(p)
db.session.commit()
audit(user.id if user else None, 'add_product', f'code={code} name={name} qty={quantity}')
return jsonify({'msg': 'Produto adicionado', 'product_id': p.id})




@products_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_product(product_id):
user = current_user()
if user.role not in ('admin', 'buyer'):
return jsonify({'msg': 'Produto removido'})