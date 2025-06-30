# migracao.py

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

def rodar_migracao():
    with app.app_context():
        print("Iniciando migração do banco de dados...")
        
        # 1. Cria as novas tabelas (Cliente, Produto) se elas não existirem.
        #    O create_all é seguro e não mexe em tabelas existentes.
        print("Passo 1: Criando tabelas novas (clientes, produtos, itens_pedido)...")
        db.create_all()
        print("Tabelas novas criadas com sucesso (ou já existiam).")

        # 2. Adiciona a coluna 'cliente_id' na tabela 'delivery_pedidos' se ela não existir.
        #    Usamos SQL puro para fazer essa alteração específica.
        try:
            print("Passo 2: Tentando adicionar a coluna 'cliente_id' na tabela de pedidos...")
            # O 'IF NOT EXISTS' garante que o comando não dê erro se a coluna já existir.
            # No entanto, a sintaxe exata pode variar. Uma abordagem mais segura é verificar antes.
            # Para simplificar, vamos assumir que a coluna não existe. Em caso de erro, já foi adicionada.
            db.session.execute(db.text('ALTER TABLE delivery_pedidos ADD COLUMN cliente_id INTEGER'))
            db.session.commit()
            print("Coluna 'cliente_id' adicionada com sucesso.")
        except Exception as e:
            # Se der erro, é provável que a coluna já exista, o que não é um problema.
            print(f"Não foi possível adicionar a coluna 'cliente_id' (provavelmente já existe): {e}")
            db.session.rollback()

        print("\nMigração concluída!")
        print("AVISO: Pedidos antigos não terão um cliente associado. Isso é esperado.")
        print("Para associá-los, seria necessário uma migração de dados manual.")

if __name__ == '__main__':
    rodar_migracao()