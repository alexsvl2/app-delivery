# correcao_db.py

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

def adicionar_coluna():
    with app.app_context():
        try:
            # Comando SQL exato para adicionar a coluna que falta
            # Usamos VARCHAR(100) que é compatível com o nosso modelo
            comando_sql = 'ALTER TABLE delivery_pedidos ADD COLUMN nome_cliente VARCHAR(100)'
            
            print("Iniciando 'cirurgia' no banco: Adicionando a coluna 'nome_cliente'...")
            db.session.execute(db.text(comando_sql))
            db.session.commit()
            print("SUCESSO: Coluna 'nome_cliente' adicionada à tabela 'delivery_pedidos'.")

        except Exception as e:
            # Se der erro, é porque a coluna provavelmente já existe de uma tentativa anterior.
            # Isso não é um problema, podemos seguir em frente.
            print(f"AVISO: Não foi possível adicionar a coluna (ela provavelmente já existe). Erro: {e}")
            db.session.rollback()

        print("\nProcesso de correção concluído!")

if __name__ == '__main__':
    adicionar_coluna()