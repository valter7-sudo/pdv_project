from flask import Flask
from flask_cors import CORS
from backend import db
from backend.routes.auth import auth_bp
from backend.routes.produtos import produtos_bp
from backend.routes.vendas import vendas_bp
from backend.routes.relatorios import relatorios_bp
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    db.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(produtos_bp, url_prefix="/api/produtos")
    app.register_blueprint(vendas_bp, url_prefix="/api/vendas")
    app.register_blueprint(relatorios_bp, url_prefix="/api/relatorios")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
