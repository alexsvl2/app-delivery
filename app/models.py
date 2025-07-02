# app/models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

# Criamos a instância do SQLAlchemy aqui, mas sem associá-la a um app ainda.
# Isso será feito no __init__.py.
db = SQLAlchemy()

# --- MODELOS DO SISTEMA ---

class Usuario(UserMixin, db.Model):
    """Modelo para o usuário do sistema (login)."""
    __tablename__ = 'delivery_usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password): 
        return check_password_hash(self.password_hash, password)

class Cliente(db.Model):
    """Modelo para os clientes cadastrados."""
    __tablename__ = 'delivery_clientes'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    # Relação para acessar todos os pedidos de um cliente
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

class Produto(db.Model):
    """Modelo para os produtos cadastrados."""
    __tablename__ = 'delivery_produtos'
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False, unique=True)
    valor = db.Column(db.Numeric(10, 2), nullable=False)

class Pedido(db.Model):
    """Modelo para o cabeçalho de um pedido."""
    __tablename__ = 'delivery_pedidos'
    id = db.Column(db.Integer, primary_key=True)
    
    # Chave estrangeira para o cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('delivery_clientes.id'), nullable=False)
    
    # Armazena um "retrato" do nome do cliente no momento do pedido
    nome_cliente = db.Column(db.String(100), nullable=False)
    
    tipo_pedido = db.Column(db.String(20), nullable=False)
    valor_entrega = db.Column(db.Numeric(10, 2), default=0.0)
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relação para acessar os itens de um pedido
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade="all, delete-orphan")

class ItemPedido(db.Model):
    """Modelo para cada item dentro de um pedido."""
    __tablename__ = 'delivery_itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    
    # Chave estrangeira para o pedido
    pedido_id = db.Column(db.Integer, db.ForeignKey('delivery_pedidos.id'), nullable=False)
    
    # Chave estrangeira para o produto
    produto_id = db.Column(db.Integer, db.ForeignKey('delivery_produtos.id'), nullable=False)
    
    # Armazena "retratos" do produto no momento da venda, caso o produto original seja alterado
    produto_descricao = db.Column(db.String(200), nullable=False)
    valor_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    quantidade = db.Column(db.Integer, nullable=False)

# Aqui você poderá adicionar os modelos do seu Fluxo de Caixa no futuro
# Exemplo:
# class LancamentoCaixa(db.Model):
#     __tablename__ = 'caixa_lancamentos'
#     ...