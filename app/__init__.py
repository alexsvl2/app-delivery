# app/__init__.py

import os
from flask import Flask
from flask_login import LoginManager
from .models import db, Usuario
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    
    # Configurações da aplicação
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa o banco de dados com a aplicação
    db.init_app(app)

    # Configuração do sistema de Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' # Aponta para a rota de login no blueprint 'auth'
    login_manager.login_message = "Você precisa estar logado para acessar esta página."
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    # --- Registro dos Blueprints ---
    
    # Blueprint de Autenticação (Login, Logout, Menu Principal)
    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp)

    # Blueprint de Pedidos
    from .pedidos.routes import pedidos_bp
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')

    # Blueprint de Fluxo de Caixa
    from .caixa.routes import caixa_bp
    app.register_blueprint(caixa_bp, url_prefix='/caixa')
    
    return app