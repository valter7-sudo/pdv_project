from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configurações
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pdv.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key"

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ------------------------
# MODELOS
# ------------------------

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    nome_completo = db.Column(db.String(120), nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    papel = db.Column(db.String(20), default="vendedor")

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, default=0)


class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, default=0)


class ItemVenda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey("venda.id"))
    produto_id = db.Column(db.Integer, db.ForeignKey("produto.id"))
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)


# ------------------------
# ROTAS
# ------------------------

@app.route("/api/login", methods=["POST"])
def login():
    dados = request.json
    usuario = Usuario.query.filter_by(usuario=dados["usuario"]).first()

    if not usuario or not usuario.verificar_senha(dados["senha"]):
        return jsonify({"erro": "Usuário ou senha inválidos"}), 401

    token = create_access_token(identity=usuario.usuario, expires_delta=timedelta(hours=8))
    return jsonify({"token": token})


@app.route("/api/produtos", methods=["GET"])
@jwt_required()
def listar_produtos():
    produtos = Produto.query.all()
    return jsonify([
        {"id": p.id, "nome": p.nome, "preco": p.preco, "estoque": p.estoque}
        for p in produtos
    ])


# ------------------------
# CRIA ADMIN AUTOMATICAMENTE
# ------------------------

with app.app_context():
    db.create_all()

    if not Usuario.query.filter_by(usuario="admin").first():
        admin = Usuario(
            usuario="admin",
            nome_completo="Administrador do Sistema",
            papel="admin"
        )
        admin.definir_senha("123456")
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário admin criado automaticamente: admin / 123456")


# ------------------------
# EXECUÇÃO LOCAL
# ------------------------

if __name__ == "__main__":
    app.run(debug=True)