# app.py (VERSÃO COMPLETA E ATUALIZADA)

import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
from datetime import date # Importa o 'date' para filtrar por dia
from sqlalchemy import cast, Date # Importa o 'cast' e 'Date' para a consulta

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do App
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


# --- Modelos do Banco de Dados ---

class Usuario(UserMixin, db.Model):
    __tablename__ = 'delivery_usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pedido(db.Model):
    __tablename__ = 'delivery_pedidos'
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text)
    bairro = db.Column(db.String(100))
    descricao = db.Column(db.Text, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    valor_entrega = db.Column(db.Numeric(10, 2))
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    data_pedido = db.Column(db.DateTime, default=db.func.now())
    tipo_pedido = db.Column(db.String(20), nullable=False)


# --- Configuração do Login ---

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))


# --- Rotas da Aplicação ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        # Lógica de login...
        # (código omitido para brevidade, continua o mesmo)
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        try:
            # Lógica para CADASTRAR novo pedido
            # (código omitido para brevidade, continua o mesmo)
            flash('Pedido cadastrado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar o pedido: {e}', 'danger')

    # MUDANÇA 02: Mostra apenas os pedidos do dia atual
    hoje = date.today()
    pedidos_do_dia = Pedido.query.filter(cast(Pedido.data_pedido, Date) == hoje).order_by(Pedido.data_pedido.desc()).all()
    
    return render_template('dashboard.html', pedidos=pedidos_do_dia)

# MUDANÇA 03: Rota para o histórico de pedidos
@app.route('/historico')
@login_required
def historico():
    todos_os_pedidos = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    return render_template('historico.html', pedidos=todos_os_pedidos)

# MUDANÇA 04: Rota para EDITAR um pedido
@app.route('/editar_pedido/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def editar_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            # Atualiza os dados do pedido com os dados do formulário
            pedido.nome_cliente = request.form['nome_cliente']
            pedido.tipo_pedido = request.form['tipo_pedido']
            pedido.endereco = request.form.get('endereco', '')
            pedido.bairro = request.form.get('bairro', '')
            pedido.descricao = request.form['descricao']
            
            valor_str = request.form['valor'].replace(',', '.')
            pedido.valor = float(valor_str)
            pedido.quantidade = int(request.form['quantidade'])
            
            valor_entrega_str = request.form.get('valor_entrega', '0.0').replace(',', '.')
            pedido.valor_entrega = float(valor_entrega_str) if pedido.tipo_pedido == 'Delivery' else 0.0
            
            # Recalcula o valor total
            pedido.valor_total = (pedido.valor * pedido.quantidade) + pedido.valor_entrega
            
            db.session.commit()
            flash('Pedido atualizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o pedido: {e}', 'danger')
            
    return render_template('editar_pedido.html', pedido=pedido)

# MUDANÇA 04: Rota para EXCLUIR um pedido
@app.route('/excluir_pedido/<int:pedido_id>', methods=['POST'])
@login_required
def excluir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido:
        try:
            db.session.delete(pedido)
            db.session.commit()
            flash('Pedido excluído com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao excluir o pedido: {e}', 'danger')
    else:
        flash('Pedido não encontrado.', 'danger')
    
    # Redireciona para a página de onde o usuário veio (dashboard ou histórico)
    return redirect(request.referrer or url_for('dashboard'))


@app.route('/imprimir/<int:pedido_id>')
@login_required
def imprimir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido não encontrado", 404
    return render_template('imprimir_pedido.html', pedido=pedido)


if __name__ == '__main__':
    app.run(debug=True)