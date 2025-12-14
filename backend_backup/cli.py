# backend/cli.py
"""
CLI administrativo para o backend PDV.
Use: python backend/cli.py
ou execute esta função dentro do flask shell.
"""

from getpass import getpass
import sys

# importa a fábrica de app para fornecer app context
from backend import create_app, db
from backend.models import User

app = create_app()  # cria a app com configuração padrão


def _create_user(username: str, password: str, role: str = "user", full_name: str = ""):
    """Helper que cria e salva usuário com senha hasheada."""
    existing = User.query.filter_by(username=username).first()
    if existing:
        print(f"⚠️ Usuário '{username}' já existe.")
        return None

    u = User(username=username.strip(), full_name=full_name.strip(), role=role)
    u.set_password(password)   # usa método seguro do model
    db.session.add(u)
    db.session.commit()
    print(f"✅ Usuário '{username}' criado com sucesso com role='{role}'.")
    return u


def create_admin_cli():
    """Cria um usuário administrador via terminal (com proteção de senha)."""
    print("=== Criar novo usuário administrador ===")
    username = input("Digite o nome de usuário (login): ").strip()
    if not username:
        print("⚠️ Username não pode ficar vazio.")
        return

    # digita a senha sem eco
    password = getpass("Digite a senha: ").strip()
    password2 = getpass("Confirme a senha: ").strip()
    if password != password2:
        print("⚠️ Senhas não conferem. Tente novamente.")
        return
    if len(password) < 6:
        print("⚠️ A senha deve ter pelo menos 6 caracteres.")
        return

    full_name = input("Nome completo (opcional): ").strip()
    _create_user(username, password, role="admin", full_name=full_name)


def create_user_cli():
    """Cria um usuário comum via terminal."""
    print("=== Criar novo usuário comum ===")
    username = input("Digite o nome de usuário: ").strip()
    if not username:
        print("⚠️ Username não pode ficar vazio.")
        return

    password = getpass("Digite a senha: ").strip()
    password2 = getpass("Confirme a senha: ").strip()
    if password != password2:
        print("⚠️ Senhas não conferem. Tente novamente.")
        return
    if len(password) < 4:
        print("⚠️ A senha deve ter pelo menos 4 caracteres.")
        return

    full_name = input("Nome completo (opcional): ").strip()
    _create_user(username, password, role="user", full_name=full_name)


def ensure_db():
    """Cria as tabelas se ainda não existirem."""
    with app.app_context():
        db.create_all()


if __name__ == "__main__":
    # roda com app context para que o db funcione
    with app.app_context():
        ensure_db()
        print("=== PAINEL ADMINISTRATIVO (CLI) ===")
        print("1 - Criar administrador")
        print("2 - Criar usuário comum")
        print("3 - Sair")
        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            create_admin_cli()
        elif escolha == "2":
            create_user_cli()
        else:
            print("Saindo...")
            sys.exit(0)