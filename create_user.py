# create_user.py (VERSÃO CORRIGIDA)

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)
# Configurações do banco de dados e chave secreta
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

# --- Modelo do Usuário (com o nome da tabela corrigido) ---
# É crucial que esta definição seja idêntica à do app.py
class Usuario(db.Model):
    __tablename__ = 'delivery_usuarios'  # Nome da tabela com prefixo
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

# --- Modelo de Pedidos (necessário para o db.create_all) ---
# Definimos todos os modelos aqui para que o comando create_all crie todas as tabelas de uma vez
class Pedido(db.Model):
    __tablename__ = 'delivery_pedidos' # Nome da tabela com prefixo
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


def criar_usuario_inicial():
    # 'app.app_context()' garante que a aplicação esteja configurada para interagir com o DB
    with app.app_context():
        print("Criando todas as tabelas do banco de dados...")
        # Cria TODAS as tabelas definidas acima (delivery_usuarios, delivery_pedidos)
        db.create_all()
        print("Tabelas criadas ou já existentes.")

        # Verifica se o usuário 'admin' já existe na tabela correta
        if Usuario.query.filter_by(username='admin').first() is None:
            print("Criando usuário 'admin'...")
            usuario = 'admin'
            senha = 'senha123'  # Lembre-se de usar uma senha forte!
            
            hashed_password = generate_password_hash(senha)
            novo_usuario = Usuario(username=usuario, password_hash=hashed_password)
            
            db.session.add(novo_usuario)
            db.session.commit()
            print("Usuário 'admin' criado com sucesso!")
        else:
            print("Usuário 'admin' já existe.")

if __name__ == '__main__':
    criar_usuario_inicial()