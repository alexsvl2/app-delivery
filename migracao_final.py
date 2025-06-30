# migracao_final.py

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

def rodar_migracao_final():
    with app.app_context():
        try:
            print("Iniciando migração final: Adicionando a coluna 'cliente_nome'...")
            # Comando SQL para adicionar a coluna, se ela não existir.
            # Usamos VARCHAR(100) para o nome do cliente.
            # NOT NULL foi removido para evitar problemas com dados antigos, o app irá preenchê-la para novos pedidos.
            db.session.execute(db.text('ALTER TABLE delivery_pedidos ADD COLUMN cliente_nome VARCHAR(100)'))
            db.session.commit()
            print("Coluna 'cliente_nome' adicionada com sucesso à tabela 'delivery_pedidos'.")
        except Exception as e:
            # Se der erro, é provável que a coluna já exista, o que não é um problema.
            print(f"AVISO: Não foi possível adicionar a coluna 'cliente_nome'. Provavelmente ela já existe. Erro: {e}")
            db.session.rollback()

        print("\nMigração final concluída!")

if __name__ == '__main__':
    rodar_migracao_final()