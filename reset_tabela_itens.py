# reset_tabela_itens.py

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Carrega as configurações do banco de dados
load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def resetar_tabela():
    with app.app_context():
        try:
            print("Iniciando reset: Tentando apagar a tabela 'delivery_itens_pedido' antiga...")
            # O 'CASCADE' remove quaisquer dependências que possam impedir a exclusão
            # O 'IF EXISTS' garante que não dê erro se a tabela já foi apagada
            db.session.execute(db.text('DROP TABLE IF EXISTS delivery_itens_pedido CASCADE'))
            db.session.commit()
            print("SUCESSO: Tabela 'delivery_itens_pedido' antiga removida (ou já não existia).")
        except Exception as e:
            print(f"AVISO ao tentar apagar a tabela: {e}")
            db.session.rollback()

if __name__ == '__main__':
    resetar_tabela()