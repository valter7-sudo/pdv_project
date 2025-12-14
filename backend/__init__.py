"""
Arquivo de inicialização do backend.

Aqui criamos a aplicação Flask, configuramos o banco de dados
e registramos todas as rotas do sistema.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Instância global do banco de dados
db = SQLAlchemy()

# Instância global do JWT
jwt = JWTManager()


def create_app():
    """
    Função fábrica da aplicação Flask.

    Essa função cria e configura a aplicação.
    É esse método que o comando `flask run` executa.
    """

    app = Flask(__name__)

    # ============================
    # CONFIGURAÇÕES DA APLICAÇÃO
    # ============================

    # Caminho do banco de dados SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///pdv.db"

    # Desativa mensagens de aviso desnecessárias
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Chave secreta do JWT
    app.config["JWT_SECRET_KEY"] = "troque_esta_chave"

    # Inicializa extensões
    db.init_app(app)
    jwt.init_app(app)

    # ============================
    # REGISTRO DAS ROTAS (BLUEPRINTS)
    # ============================

    # Rotas de autenticação (login)
    from backend.routes.autenticacao import autenticacao_bp
    app.register_blueprint(autenticacao_bp, url_prefix="/api/auth")

    # Rotas de produtos
    from backend.routes.produtos import produtos_bp
    app.register_blueprint(produtos_bp, url_prefix="/api/produtos")

    # ============================
    # ROTA RAIZ (TESTE)
    # ============================

    @app.route("/")
    def index():
        return "PDV Backend Running"

    return app

