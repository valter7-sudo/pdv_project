"""
Arquivo de inicialização do backend.

Aqui criamos a aplicação Flask, configuramos o banco de dados
e registramos todas as rotas do sistema.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Instância global do banco de dados
# Ela será usada em outros arquivos (models, rotas, etc.)
db = SQLAlchemy()


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

    # Inicializa o banco de dados com a aplicação
    db.init_app(app)

    # ============================
    # REGISTRO DAS ROTAS (BLUEPRINTS)
    # ============================

    # Importação feita aqui para evitar importação circular
    from backend.routes.produtos import products_bp

    # Registra as rotas de produtos
    app.register_blueprint(products_bp)

    # ============================
    # ROTA RAIZ (TESTE)
    # ============================

    @app.route("/")
    def index():
        """
        Rota principal do sistema.
        Serve apenas para testar se o backend está rodando.
        """
        return "PDV Backend Running"

    return app
