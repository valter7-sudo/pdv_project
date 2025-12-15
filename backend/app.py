from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity
)
from flask_cors import CORS

# ---------------------
# Configuração básica
# ---------------------
app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pdv.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'troque_esta_chave_por_uma_super_secreta'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=8)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# ---------------------
# MODELOS
# ---------------------
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    nome_completo = db.Column(db.String(120))
    senha_hash = db.Column(db.String(256), nullable=False)
    papel = db.Column(db.String(30), nullable=False, default='operador')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(64), unique=True, nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    preco = db.Column(db.Float, nullable=False, default=0.0)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    criado_por_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False, default=0.0)


class ItemVenda(db.Model):
    __tablename__ = "itens_venda"

    id = db.Column(db.Integer, primary_key=True)
    venda_id = db.Column(db.Integer, db.ForeignKey('vendas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)


class LogAuditoria(db.Model):
    __tablename__ = "logs_auditoria"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, nullable=True)
    acao = db.Column(db.String(200))
    detalhes = db.Column(db.String(1000))
    registrado_em = db.Column(db.DateTime, default=datetime.utcnow)
# ---------------------
# Funções auxiliares
# ---------------------
def registrar_auditoria(usuario_id, acao, detalhes=""):
    log = LogAuditoria(usuario_id=usuario_id, acao=acao, detalhes=detalhes)
    db.session.add(log)
    db.session.commit()


def exigir_papel(*papeis_permitidos):
    def decorador(fn):
        @jwt_required()
        def wrapper(*args, **kwargs):
            identidade = get_jwt_identity()
            usuario = Usuario.query.filter_by(usuario=identidade).first()
            if not usuario or usuario.papel not in papeis_permitidos:
                return jsonify({"mensagem": "Permissão negada"}), 403
            return fn(usuario, *args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorador

# ---------------------
# Rotas: Autenticação
# ---------------------
@app.route('/api/auth/login', methods=['POST'])
def login():
    dados = request.json or {}
    usuario_str = dados.get('username')
    senha = dados.get('password')

    if not usuario_str or not senha:
        return jsonify({"mensagem": "username e password são obrigatórios"}), 400

    usuario = Usuario.query.filter_by(usuario=usuario_str).first()
    if not usuario or not usuario.verificar_senha(senha):
        return jsonify({"mensagem": "Credenciais inválidas"}), 401

    token = create_access_token(identity=usuario.usuario)
    registrar_auditoria(usuario.id, "login", f"Usuário {usuario.usuario} realizou login")

    return jsonify({
        "access_token": token,
        "papel": usuario.papel,
        "usuario": usuario.usuario,
        "nome_completo": usuario.nome_completo
    })

# ---------------------
# Rotas: Usuários
# ---------------------
@app.route('/api/usuarios', methods=['POST'])
@exigir_papel('admin')
def criar_usuario(usuario_atual):
    dados = request.json or {}
    usuario_str = dados.get('username')
    senha = dados.get('password')
    papel = dados.get('role', 'operador')
    nome_completo = dados.get('full_name', '')

    if not usuario_str or not senha:
        return jsonify({"mensagem": "username e password são obrigatórios"}), 400

    if Usuario.query.filter_by(usuario=usuario_str).first():
        return jsonify({"mensagem": "Já existe um usuário com esse username"}), 400

    novo_usuario = Usuario(
        usuario=usuario_str,
        nome_completo=nome_completo,
        papel=papel
    )
    novo_usuario.definir_senha(senha)
    db.session.add(novo_usuario)
    db.session.commit()

    registrar_auditoria(usuario_atual.id, "criar_usuario", f"Criou usuário {usuario_str} com papel {papel}")

    return jsonify({"mensagem": "Usuário criado com sucesso", "username": usuario_str})


@app.route('/api/usuarios', methods=['GET'])
@exigir_papel('admin')
def listar_usuarios(usuario_atual):
    usuarios = Usuario.query.all()
    retorno = []
    for u in usuarios:
        retorno.append({
            "id": u.id,
            "username": u.usuario,
            "nome_completo": u.nome_completo,
            "papel": u.papel,
            "criado_em": u.criado_em.isoformat()
        })
    return jsonify(retorno)
# ---------------------
# Rotas: Produtos
# ---------------------
@app.route('/api/produtos', methods=['POST'])
@exigir_papel('admin', 'operador', 'comprador')
def adicionar_produto(usuario_atual):
    dados = request.json or {}
    codigo = dados.get('code')
    nome = dados.get('name')
    preco = dados.get('price', 0.0)
    quantidade = dados.get('quantity', 0)

    if not codigo or not nome:
        return jsonify({"mensagem": "code e name são obrigatórios"}), 400

    if Produto.query.filter_by(codigo=codigo).first():
        return jsonify({"mensagem": "Já existe um produto com esse código"}), 400

    produto = Produto(
        codigo=codigo,
        nome=nome,
        preco=float(preco),
        quantidade=int(quantidade)
    )
    db.session.add(produto)
    db.session.commit()

    registrar_auditoria(
        usuario_atual.id,
        "adicionar_produto",
        f"code={codigo} name={nome} qty={quantidade}"
    )

    return jsonify({"mensagem": "Produto adicionado com sucesso", "produto_id": produto.id})


@app.route('/api/produtos', methods=['GET'])
@jwt_required()
def listar_produtos():
    produtos = Produto.query.all()
    retorno = []
    for p in produtos:
        retorno.append({
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "preco": p.preco,
            "quantidade": p.quantidade,
            "criado_em": p.criado_em.isoformat()
        })
    return jsonify(retorno)


@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
@exigir_papel('admin', 'comprador')
def atualizar_produto(usuario_atual, produto_id):
    produto = Produto.query.get_or_404(produto_id)
    dados = request.json or {}

    produto.nome = dados.get('name', produto.nome)
    produto.preco = float(dados.get('price', produto.preco))
    produto.quantidade = int(dados.get('quantity', produto.quantidade))

    db.session.commit()

    registrar_auditoria(usuario_atual.id, "atualizar_produto", f"id={produto_id}")

    return jsonify({"mensagem": "Produto atualizado com sucesso"})


@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
@exigir_papel('admin')
def remover_produto(usuario_atual, produto_id):
    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()

    registrar_auditoria(usuario_atual.id, "remover_produto", f"id={produto_id}")

    return jsonify({"mensagem": "Produto removido com sucesso"})
# ---------------------
# Rotas: Vendas
# ---------------------
@app.route('/api/vendas', methods=['POST'])
@exigir_papel('admin', 'operador', 'comprador')
def registrar_venda(usuario_atual):
    dados = request.json or {}
    itens = dados.get('items', [])

    if not itens:
        return jsonify({"mensagem": "items é obrigatório e não pode ser vazio"}), 400

    venda = Venda(criado_por_id=usuario_atual.id, total=0.0)
    db.session.add(venda)

    total = 0.0
    for item in itens:
        codigo = item.get('code')
        quantidade = int(item.get('quantity', 0))

        produto = Produto.query.filter_by(codigo=codigo).first()
        if not produto:
            db.session.rollback()
            return jsonify({"mensagem": f"Produto com código {codigo} não encontrado"}), 400

        if produto.quantidade < quantidade:
            db.session.rollback()
            return jsonify({"mensagem": f"Estoque insuficiente para {produto.nome}"}), 400

        subtotal = produto.preco * quantidade

        # ✅ ESTE BLOCO É O QUE ESTAVA DANDO ERRO — AGORA ESTÁ PERFEITO
        item_venda = ItemVenda(
            venda_id=venda.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco=produto.preco,
            subtotal=subtotal
        )

        db.session.add(item_venda)
        produto.quantidade -= quantidade
        total += subtotal

    venda.total = total
    db.session.commit()

    registrar_auditoria(
        usuario_atual.id,
        "registrar_venda",
        f"venda_id={venda.id} total={total}"
    )

    return jsonify({
        "mensagem": "Venda registrada com sucesso",
        "venda_id": venda.id,
        "total": total
    })
# ---------------------
# Relatórios
# ---------------------
@app.route('/api/relatorios/estoque', methods=['GET'])
@exigir_papel('admin', 'comprador', 'fiscal')
def relatorio_estoque(usuario_atual):
    limite = int(request.args.get('threshold', 10))
    produtos = Produto.query.order_by(Produto.quantidade.asc()).all()

    baixo_estoque = []
    for p in produtos:
        if p.quantidade <= limite:
            baixo_estoque.append({
                "codigo": p.codigo,
                "nome": p.nome,
                "quantidade": p.quantidade
            })

    return jsonify({"baixo_estoque": baixo_estoque})


# ✅ NOVO: Vendas por dia
@app.route('/api/relatorios/vendas_por_dia', methods=['GET'])
@exigir_papel('admin', 'comprador', 'fiscal')
def relatorio_vendas_por_dia(usuario_atual):
    resultados = (
        db.session.query(
            db.func.date(Venda.criado_em).label("dia"),
            db.func.sum(Venda.total).label("total")
        )
        .group_by(db.func.date(Venda.criado_em))
        .order_by(db.func.date(Venda.criado_em))
        .all()
    )

    retorno = []
    for dia, total in resultados:
        retorno.append({
            "dia": str(dia),
            "total": float(total)
        })

    return jsonify(retorno)


# ✅ NOVO: Totalizador
@app.route('/api/relatorios/totalizador', methods=['GET'])
@exigir_papel('admin', 'comprador', 'fiscal')
def relatorio_totalizador(usuario_atual):
    total_vendido = db.session.query(db.func.sum(Venda.total)).scalar() or 0
    quantidade_vendas = db.session.query(db.func.count(Venda.id)).scalar() or 0

    return jsonify({
        "total_vendido": float(total_vendido),
        "quantidade_vendas": quantidade_vendas
    })


# ✅ NOVO: Produtos mais vendidos
@app.route('/api/relatorios/produtos_mais_vendidos', methods=['GET'])
@exigir_papel('admin', 'comprador', 'fiscal')
def relatorio_produtos_mais_vendidos(usuario_atual):
    resultados = (
        db.session.query(
            Produto.nome.label("produto"),
            db.func.sum(ItemVenda.quantidade).label("quantidade_vendida")
        )
        .join(ItemVenda, Produto.id == ItemVenda.produto_id)
        .group_by(Produto.nome)
        .order_by(db.func.sum(ItemVenda.quantidade).desc())
        .all()
    )

    retorno = []
    for produto, quantidade in resultados:
        retorno.append({
            "produto": produto,
            "quantidade_vendida": int(quantidade)
        })

    return jsonify(retorno)
# ---------------------
# Servir FRONTEND
# ---------------------
@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/produtos')
def pagina_produtos():
    return send_from_directory('frontend', 'produtos.html')

@app.route('/relatorios')
def pagina_relatorios():
    return send_from_directory('frontend', 'relatorios.html')

@app.route('/vendas')
def pagina_vendas():
    return send_from_directory('frontend', 'vendas.html')

@app.route('/js/<path:arquivo>')
def arquivos_js(arquivo):
    return send_from_directory('frontend/js', arquivo)

# ---------------------
# Inicialização do BD + Admin automático
# ---------------------
with app.app_context():
    db.create_all()

    admin = Usuario.query.filter_by(usuario="admin").first()
    if not admin:
        admin = Usuario(
            usuario="admin",
            nome_completo="Administrador do Sistema",
            papel="admin"
        )
        admin.definir_senha("123456")
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuário admin criado automaticamente: admin / 123456")

# ---------------------
# Execução local
# ---------------------
if __name__ == '__main__':
    app.run(debug=True)