# backend/routes/autenticacao.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from backend.models import Usuario
from backend import db

autenticacao_bp = Blueprint("autenticacao", __name__)

@autenticacao_bp.route("/login", methods=["POST"])
def login():
    dados = request.get_json()

    usuario_digitado = dados.get("usuario")
    senha_digitada = dados.get("senha")

    if not usuario_digitado or not senha_digitada:
        return jsonify({"erro": "Usuário e senha são obrigatórios"}), 400

    usuario = Usuario.query.filter_by(usuario=usuario_digitado).first()

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    if not usuario.verificar_senha(senha_digitada):
        return jsonify({"erro": "Senha incorreta"}), 401

    token = create_access_token(identity=usuario.id)

    return jsonify({
        "mensagem": "Login realizado com sucesso",
        "token": token,
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "perfil": usuario.perfil.nome
        }
    }), 200
