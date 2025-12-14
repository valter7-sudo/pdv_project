# app.py
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity
)

# ---------------------
# Configuração básica
# ---------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pdv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'troque_esta_chave_por_uma_super_secreta'  # Mude em produção
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ---------------------
# MODELS
# ---------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120))
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(30), nullable=False, default='operator')  # admin, operator, buyer, fiscal, client
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), unique=True, nullable=False)  # código de barras
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False, default=0.0)

class SaleItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sale_id = db.Column(db.Integer, db.ForeignKey('sale.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)  # price at the moment of sale
    subtotal = db.Column(db.Float, nullable=False)

class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    action = db.Column(db.String(200))
    details = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# ---------------------
# Helpers
# ---------------------
def audit(user_id, action, details=""):
    log = AuditLog(user_id=user_id, action=action, details=details)
    db.session.add(log)
    db.session.commit()

def require_role(*allowed_roles):
    def decorator(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            user = User.query.filter_by(username=identity).first()
            if not user or user.role not in allowed_roles:
                return jsonify({"msg": "Permissão negada"}), 403
            return fn(user, *args, **kwargs)
        # Flask expects function attributes
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator

# ---------------------
# Routes: Auth
# ---------------------
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "username e password obrigatórios"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Credenciais inválidas"}), 401

    access_token = create_access_token(identity=user.username)
    audit(user.id, "login", f"user {user.username} logou")
    return jsonify({"access_token": access_token, "role": user.role})

# ---------------------
# Routes: Users (Admin)
# ---------------------
@app.route('/api/users', methods=['POST'])
@require_role('admin')
def create_user(current_user):
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'operator')
    full_name = data.get('full_name', '')

    if not username or not password:
        return jsonify({"msg": "username e password obrigatórios"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"msg": "username já existe"}), 400

    u = User(username=username, full_name=full_name, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    audit(current_user.id, "create_user", f"criou {username} role={role}")
    return jsonify({"msg": "Usuário criado", "username": username})

@app.route('/api/users', methods=['GET'])
@require_role('admin')
def list_users(current_user):
    users = User.query.all()
    out = [{"id": u.id, "username": u.username, "full_name": u.full_name, "role": u.role} for u in users]
    return jsonify(out)

# ---------------------
# Routes: Products (Stock)
# ---------------------
@app.route('/api/products', methods=['POST'])
@require_role('admin', 'operator', 'buyer')
def add_product(current_user):
    data = request.json or {}
    code = data.get('code')
    name = data.get('name')
    price = data.get('price', 0.0)
    quantity = data.get('quantity', 0)

    if not code or not name:
        return jsonify({"msg": "code e name obrigatórios"}), 400
    if Product.query.filter_by(code=code).first():
        return jsonify({"msg": "Produto com esse código já existe"}), 400

    p = Product(code=code, name=name, price=float(price), quantity=int(quantity))
    db.session.add(p)
    db.session.commit()
    audit(current_user.id, "add_product", f"code={code} name={name} qty={quantity}")
    return jsonify({"msg": "Produto adicionado", "product_id": p.id})

@app.route('/api/products', methods=['GET'])
@jwt_required()
def list_products():
    products = Product.query.all()
    out = [{"id": p.id, "code": p.code, "name": p.name, "price": p.price, "quantity": p.quantity} for p in products]
    return jsonify(out)

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@require_role('admin', 'buyer')
def update_product(current_user, product_id):
    p = Product.query.get_or_404(product_id)
    data = request.json or {}
    p.name = data.get('name', p.name)
    p.price = float(data.get('price', p.price))
    p.quantity = int(data.get('quantity', p.quantity))
    db.session.commit()
    audit(current_user.id, "update_product", f"id={product_id}")
    return jsonify({"msg": "Produto atualizado"})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@require_role('admin')
def delete_product(current_user, product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    audit(current_user.id, "delete_product", f"id={product_id}")
    return jsonify({"msg": "Produto removido"})

# ---------------------
# Routes: Sell (creates sale, reduces stock)
# ---------------------
@app.route('/api/sales', methods=['POST'])
@require_role('admin', 'operator', 'buyer')
def create_sale(current_user):
    data = request.json or {}
    items = data.get('items', [])  # expected: [{"code": "...", "quantity": n}, ...]
    if not items:
        return jsonify({"msg": "items obrigatórios"}), 400

    sale = Sale(created_by=current_user.id, total=0.0)
    db.session.add(sale)
    total = 0.0
    for it in items:
        code = it.get('code')
        qty = int(it.get('quantity', 0))
        product = Product.query.filter_by(code=code).first()
        if not product:
            db.session.rollback()
            return jsonify({"msg": f"Produto com código {code} não encontrado"}), 400
        if product.quantity < qty:
            db.session.rollback()
            return jsonify({"msg": f"Estoque insuficiente para {product.name} (tem {product.quantity})"}), 400

        subtotal = product.price * qty
        si = SaleItem(sale_id=sale.id, product_id=product.id, quantity=qty, price=product.price, subtotal=subtotal)
        db.session.add(si)
        product.quantity -= qty  # decrement stock
        total += subtotal

    sale.total = total
    db.session.commit()
    audit(current_user.id, "create_sale", f"sale_id={sale.id} total={total}")
    return jsonify({"msg": "Venda registrada", "sale_id": sale.id, "total": total})

# ---------------------
# Routes: Reports / Stock check
# ---------------------
@app.route('/api/reports/stock', methods=['GET'])
@require_role('admin', 'buyer', 'fiscal')
def stock_report(current_user):
    threshold = int(request.args.get('threshold', 10))
    products = Product.query.order_by(Product.quantity.asc()).all()
    low = [{"code": p.code, "name": p.name, "qty": p.quantity} for p in products if p.quantity <= threshold]
    return jsonify({"low_stock": low, "all_count": len(products)})

# ---------------------
# CLI helper to create admin user
# ---------------------
@app.cli.command('create-admin')
def create_admin():
    username = input("username admin: ").strip()
    password = input("password: ").strip()
    if not username or not password:
        print("username e password obrigatórios")
        return
    if User.query.filter_by(username=username).first():
        print("username já existe")
        return
    u = User(username=username, role='admin')
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    print("Admin criado com sucesso.")

# ---------------------
# Inicialização do DB
# ---------------------
if __name__ == '__main__':
    # Cria DB e tabelas se não existirem
    db.create_all()
    print("DB pronto. Rode `flask run` para iniciar a aplicação.")