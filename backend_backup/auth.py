# backend/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, AuditLog
from . import db


auth_bp = Blueprint('auth', __name__)




def audit(user_id, action, details=''):
a = AuditLog(user_id=user_id, action=action, details=details)
db.session.add(a)
db.session.commit()




@auth_bp.route('/login', methods=['POST'])
def login():
data = request.json or {}
username = data.get('username')
password = data.get('password')
if not username or not password:
return jsonify({'msg': 'username e password obrigatórios'}), 400


user = User.query.filter_by(username=username).first()
if not user or not check_password_hash(user.password_hash, password):
return jsonify({'msg': 'Credenciais inválidas'}), 401


token = create_access_token(identity=user.username)
audit(user.id, 'login', f'user {user.username} logou')
return jsonify({'access_token': token, 'role': user.role})




@auth_bp.route('/whoami', methods=['GET'])
@jwt_required()
def whoami():
identity = get_jwt_identity()
user = User.query.filter_by(username=identity).first()
return jsonify({'username': user.username, 'full_name': user.full_name, 'role': user.role})