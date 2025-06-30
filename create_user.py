# create_user.py (VERSÃO FINAL COMPLETA)

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin # Importação necessária
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

# --- MODELOS COMPLETOS ---

# AQUI ESTÁ A CORREÇÃO PRINCIPAL
class Usuario(UserMixin, db.Model):
    __tablename__ = 'delivery_usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Pedido(db.Model):
    __tablename__ = 'delivery_pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('delivery_clientes.id'), nullable=False)
    cliente = db.relationship('Cliente', backref='pedidos')
    valor_entrega = db.Column(db.Numeric(10, 2), default=0.0)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    data_pedido = db.Column(db.DateTime, default=db.func.now())
    tipo_pedido = db.Column(db.String(20), nullable=False)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade="all, delete-orphan")

class ItemPedido(db.Model):
    __tablename__ = 'delivery_itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('delivery_produtos.id'), nullable=False)
    produto_descricao = db.Column(db.String(200), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    pedido_id = db.Column(db.Integer, db.ForeignKey('delivery_pedidos.id'), nullable=False)

class Cliente(db.Model):
    __tablename__ = 'delivery_clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    bairro = db.Column(db.String(100))

class Produto(db.Model):
    __tablename__ = 'delivery_produtos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False, unique=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)


def criar_tudo():
    with app.app_context():
        print("Criando todas as tabelas (com Clientes e Produtos)...")
        db.create_all()
        print("Tabelas criadas ou já existentes.")
        
        if Usuario.query.filter_by(username='admin').first() is None:
            print("Criando usuário 'admin'...")
            hashed_password = generate_password_hash('senha123')
            novo_usuario = Usuario(username='admin', password_hash=hashed_password)
            db.session.add(novo_usuario)
            db.session.commit()
            print("Usuário 'admin' criado com sucesso!")
        else:
            print("Usuário 'admin' já existe.")

if __name__ == '__main__':
    criar_tudo()