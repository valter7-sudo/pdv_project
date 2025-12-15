from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data.get("usuario")
    senha = data.get("senha")

    if usuario == "admin" and senha == "123456":
        token = create_access_token(identity=usuario)
        return jsonify(access_token=token), 200

    return jsonify(msg="Credenciais inválidas"), 401
