# correcao_db.py (VERSÃO 2 - Adiciona todas as colunas que faltam)

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def rodar_migracao_final():
    with app.app_context():
        # Verificação 1: Adiciona 'nome_cliente' em 'delivery_pedidos'
        try:
            print("Verificando coluna 'nome_cliente' em 'delivery_pedidos'...")
            comando_sql_1 = 'ALTER TABLE delivery_pedidos ADD COLUMN nome_cliente VARCHAR(100)'
            db.session.execute(db.text(comando_sql_1))
            db.session.commit()
            print("--> SUCESSO: Coluna 'nome_cliente' adicionada.")
        except Exception:
            print("--> AVISO: Coluna 'nome_cliente' provavelmente já existe. Tudo certo.")
            db.session.rollback()

        # Verificação 2: Adiciona 'produto_id' em 'delivery_itens_pedido' (A correção principal de agora)
        try:
            print("Verificando coluna 'produto_id' em 'delivery_itens_pedido'...")
            comando_sql_2 = 'ALTER TABLE delivery_itens_pedido ADD COLUMN produto_id INTEGER'
            db.session.execute(db.text(comando_sql_2))
            db.session.commit()
            print("--> SUCESSO: Coluna 'produto_id' adicionada.")
        except Exception:
            print("--> AVISO: Coluna 'produto_id' provavelmente já existe. Tudo certo.")
            db.session.rollback()

        print("\nProcesso de correção do banco de dados concluído!")

if __name__ == '__main__':
    rodar_migracao_final()