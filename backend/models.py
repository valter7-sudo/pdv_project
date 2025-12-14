# backend/models.py
"""
Modelos do banco de dados do sistema PDV.

Este arquivo define todas as tabelas principais:
- Usuários (funcionários)
- Perfis de acesso
- Produtos
- Logs de auditoria

Todos os nomes estão em português para facilitar o aprendizado.
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from backend import db


# =========================
# PERFIS DE ACESSO
# =========================
class PerfilAcesso(db.Model):
    __tablename__ = "perfis_acesso"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    descricao = db.Column(db.String(255))

    def __repr__(self):
        return f"<PerfilAcesso {self.nome}>"


# =========================
# USUÁRIOS (FUNCIONÁRIOS)
# =========================
class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)

    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    perfil_id = db.Column(
        db.Integer,
        db.ForeignKey("perfis_acesso.id"),
        nullable=False
    )

    perfil = db.relationship("PerfilAcesso")

    # Define a senha (gera o hash)
    def definir_senha(self, senha_plana):
        self.senha_hash = generate_password_hash(senha_plana)

    # Verifica se a senha está correta
    def verificar_senha(self, senha_plana):
        return check_password_hash(self.senha_hash, senha_plana)

    def __repr__(self):
        return f"<Usuario {self.usuario}>"


# =========================
# PRODUTOS
# =========================
class Produto(db.Model):
    __tablename__ = "produtos"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    quantidade = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Produto {self.nome}>"

# ============================
# MOVIMENTAÇÃO DE ESTOQUE
# ============================
class MovimentacaoEstoque(db.Model):
    __tablename__ = "movimentacoes_estoque"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False)  # entrada ou saída
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(255), nullable=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    produto = db.relationship("Produto")

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario = db.relationship("Usuario")

    def __repr__(self):
        return f"<MovimentacaoEstoque {self.tipo} - {self.quantidade}>"

# =========================
# LOG DE AUDITORIA
# =========================
class LogAuditoria(db.Model):
    __tablename__ = "logs_auditoria"

    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(100), nullable=False)
    detalhes = db.Column(db.String(255))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)

    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.id"),
        nullable=True
    )

    usuario = db.relationship("Usuario")

# =========================
# VENDAS
# =========================
class Venda(db.Model):
    __tablename__ = "vendas"

    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Float, nullable=False, default=0.0)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario = db.relationship("Usuario")

    def __repr__(self):
        return f"<Venda {self.id} - Total {self.total}>"


# =========================
# ITENS DA VENDA
# =========================
class ItemVenda(db.Model):
    __tablename__ = "itens_venda"

    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    venda_id = db.Column(db.Integer, db.ForeignKey("vendas.id"), nullable=False)
    venda = db.relationship("Venda", backref="itens")

    produto_id = db.Column(db.Integer, db.ForeignKey("produtos.id"), nullable=False)
    produto = db.relationship("Produto")

    def __repr__(self):
        return f"<ItemVenda venda={self.venda_id} produto={self.produto_id}>"
