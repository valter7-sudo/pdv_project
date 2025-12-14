from backend import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    estoque = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Product {self.nome}>"


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(50), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AuditLog {self.acao}>"
