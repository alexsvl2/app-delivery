# app.py (VERSÃO 100% COMPLETA E CORRIGIDA)

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from datetime import date
from sqlalchemy import cast, Date
from decimal import Decimal

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Por favor, faça o login para acessar esta página."
login_manager.login_message_category = "info"


# --- MODELOS FINAIS E CORRETOS ---
class Usuario(UserMixin, db.Model):
    __tablename__ = 'delivery_usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    def check_password(self, password): return check_password_hash(self.password_hash, password)

class Pedido(db.Model):
    __tablename__ = 'delivery_pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('delivery_clientes.id'), nullable=False)
    nome_cliente = db.Column(db.String(100), nullable=False)
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

@login_manager.user_loader
def load_user(user_id): return db.session.get(Usuario, int(user_id))


# --- ROTAS DE AUTENTICAÇÃO E DASHBOARD ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('dashboard'))
        else: flash('Usuário ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    hoje = date.today()
    pedidos_do_dia = Pedido.query.filter(cast(Pedido.data_pedido, Date) == hoje).order_by(Pedido.data_pedido.desc()).all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('dashboard.html', pedidos=pedidos_do_dia, clientes=clientes, produtos=produtos)

# --- ROTAS DE PEDIDOS ---
@app.route('/novo_pedido', methods=['POST'])
@login_required
def novo_pedido():
    try:
        cliente_id = request.form.get('cliente_id')
        if not cliente_id:
            flash('Selecione um cliente para o pedido.', 'warning'); return redirect(url_for('dashboard'))

        cliente_selecionado = db.session.get(Cliente, int(cliente_id))
        if not cliente_selecionado:
            flash('Cliente selecionado não encontrado.', 'danger'); return redirect(url_for('dashboard'))

        novo_pedido = Pedido(
            cliente_id=cliente_id,
            nome_cliente=cliente_selecionado.nome,
            tipo_pedido=request.form['tipo_pedido']
        )
        
        produto_ids = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('item_quantidade[]')
        
        if not produto_ids:
            flash('Adicione pelo menos um item ao pedido.', 'warning'); return redirect(url_for('dashboard'))

        valor_total_itens = Decimal('0.0')

        for i in range(len(produto_ids)):
            if produto_ids[i]:
                produto = db.session.get(Produto, int(produto_ids[i]))
                if produto:
                    quantidade = int(quantidades[i])
                    item = ItemPedido(
                        produto_id=produto.id,
                        produto_descricao=produto.descricao,
                        quantidade=quantidade,
                        valor_unitario=produto.valor
                    )
                    novo_pedido.itens.append(item)
                    valor_total_itens += quantidade * produto.valor
        
        valor_entrega = Decimal('0.0')
        if novo_pedido.tipo_pedido == 'Delivery':
            valor_entrega = Decimal(request.form.get('valor_entrega', '0.0').replace(',', '.'))
        
        novo_pedido.valor_entrega = valor_entrega
        novo_pedido.valor_total = valor_total_itens + valor_entrega
        
        db.session.add(novo_pedido)
        db.session.commit()
        flash('Pedido cadastrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar pedido: {e}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/excluir_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def excluir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido:
        db.session.delete(pedido)
        db.session.commit()
        flash('Pedido excluído com sucesso!', 'success')
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/imprimir/<int:pedido_id>')
@login_required
def imprimir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido não encontrado", 404
    return render_template('imprimir_pedido.html', pedido=pedido)

@app.route('/historico')
@login_required
def historico():
    pedidos = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    return render_template('historico.html', pedidos=pedidos)

# --- ROTAS DE GESTÃO DE CLIENTES ---
@app.route('/clientes')
@login_required
def gerenciar_clientes():
    clientes = Cliente.query.order_by(Cliente.nome).all()
    return render_template('clientes.html', clientes=clientes)

@app.route('/clientes/novo', methods=['POST'])
@login_required
def novo_cliente():
    try:
        novo = Cliente(nome=request.form['nome'], telefone=request.form.get('telefone'), endereco=request.form.get('endereco'), bairro=request.form.get('bairro'))
        db.session.add(novo)
        db.session.commit()
        flash('Cliente cadastrado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('gerenciar_clientes'))

@app.route('/clientes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_cliente(id):
    cliente = db.session.get(Cliente, id)
    if cliente and not cliente.pedidos:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído.', 'success')
    elif cliente:
        flash('Não é possível excluir um cliente que já possui pedidos.', 'warning')
    return redirect(url_for('gerenciar_clientes'))

# --- ROTAS DE GESTÃO DE PRODUTOS ---
@app.route('/produtos')
@login_required
def gerenciar_produtos():
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('produtos.html', produtos=produtos)

@app.route('/produtos/novo', methods=['POST'])
@login_required
def novo_produto():
    try:
        valor = Decimal(request.form.get('valor', '0.0').replace(',', '.'))
        novo = Produto(descricao=request.form['descricao'], valor=valor)
        db.session.add(novo)
        db.session.commit()
        flash('Produto cadastrado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('gerenciar_produtos'))

@app.route('/produtos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = db.session.get(Produto, id)
    if produto:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído.', 'success')
    return redirect(url_for('gerenciar_produtos'))


if __name__ == '__main__':
    app.run(debug=True)