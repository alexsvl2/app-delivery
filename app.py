# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
from datetime import datetime

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
login_manager.login_view = 'login' # Redireciona para a rota /login se não estiver logado

# --- Modelos do Banco de Dados ---

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    nome_cliente = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.Text)
    bairro = db.Column(db.String(100))
    descricao = db.Column(db.Text, nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    valor_entrega = db.Column(db.Numeric(10, 2))
    valor_total = db.Column(db.Numeric(10, 2), nullable=False)
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_pedido = db.Column(db.String(20), nullable=False)

# --- Configuração do Login ---

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- Rotas da Aplicação ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Usuario.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos.')
            
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
            # Coleta de dados do formulário
            tipo_pedido = request.form['tipo_pedido']
            valor = float(request.form['valor'])
            quantidade = int(request.form['quantidade'])
            
            # Cálculo do valor de entrega e total
            valor_entrega = float(request.form.get('valor_entrega', 0.0)) if tipo_pedido == 'Delivery' else 0.0
            valor_total = (valor * quantidade) + valor_entrega

            # Criação do novo pedido
            novo_pedido = Pedido(
                nome_cliente=request.form['nome_cliente'],
                endereco=request.form.get('endereco', ''),
                bairro=request.form.get('bairro', ''),
                descricao=request.form['descricao'],
                quantidade=quantidade,
                valor=valor,
                valor_entrega=valor_entrega,
                valor_total=valor_total,
                tipo_pedido=tipo_pedido
            )
            
            db.session.add(novo_pedido)
            db.session.commit()
            
            flash('Pedido cadastrado com sucesso!', 'success')
            return redirect(url_for('imprimir_pedido', pedido_id=novo_pedido.id))

        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar o pedido: {e}', 'danger')

    # Exibe os últimos 10 pedidos no dashboard
    pedidos_recentes = Pedido.query.order_by(Pedido.data_pedido.desc()).limit(10).all()
    return render_template('dashboard.html', pedidos=pedidos_recentes)


@app.route('/imprimir/<int:pedido_id>')
@login_required
def imprimir_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('imprimir_pedido.html', pedido=pedido)

if __name__ == '__main__':
    # Para desenvolvimento local
    app.run(debug=True)