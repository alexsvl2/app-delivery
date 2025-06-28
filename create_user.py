# create_user.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

def criar_usuario_inicial():
    with app.app_context():
        db.create_all() # Cria as tabelas se não existirem
        
        # Verifica se o usuário já existe
        if Usuario.query.filter_by(username='admin').first() is None:
            print("Criando usuário 'admin'...")
            # Defina aqui o nome de usuário e a senha
            usuario = 'admin'
            senha = 'senha123' # Mude para uma senha forte!
            
            hashed_password = generate_password_hash(senha)
            novo_usuario = Usuario(username=usuario, password_hash=hashed_password)
            db.session.add(novo_usuario)
            db.session.commit()
            print("Usuário 'admin' criado com sucesso!")
        else:
            print("Usuário 'admin' já existe.")

if __name__ == '__main__':
    criar_usuario_inicial()