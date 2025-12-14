# backend/utils/permissoes.py

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from backend.models import Usuario

def usuario_logado():
    """
    Retorna o objeto Usuario correspondente ao token JWT atual.
    """
    usuario_id = get_jwt_identity()
    return Usuario.query.get(usuario_id)


def requer_token(funcao):
    """
    Decorador que exige que o usuário esteja autenticado.
    """
    @wraps(funcao)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
        except Exception:
            return jsonify({"erro": "Token inválido ou ausente"}), 401
        return funcao(*args, **kwargs)
    return wrapper


def requer_perfil(*perfis_permitidos):
    """
    Decorador que exige que o usuário tenha um dos perfis permitidos.
    Exemplo de uso:
        @requer_perfil("gerente", "operador")
    """
    def decorator(funcao):
        @wraps(funcao)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            usuario = usuario_logado()

            if usuario.perfil.nome not in perfis_permitidos:
                return jsonify({"erro": "Acesso negado"}), 403

            return funcao(*args, **kwargs)
        return wrapper
    return decorator
