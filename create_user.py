# create_user.py (versão para a nova estrutura)

from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

# Cria uma instância da aplicação para ter o contexto do banco de dados
app = create_app()

# Executa as operações dentro do contexto da aplicação
with app.app_context():
    print("Criando todas as tabelas do banco de dados...")
    db.create_all()
    print("Tabelas criadas ou já existentes.")
    
    # Lógica para criar o usuário admin, se ele não existir
    if Usuario.query.filter_by(username='admin').first() is None:
        print("Criando usuário 'admin'...")
        
        novo_usuario = Usuario(username='admin')
        # A função set_password não existe mais no modelo, usamos a importada
        hashed_password = generate_password_hash('senha123')
        novo_usuario.password_hash = hashed_password
        
        db.session.add(novo_usuario)
        db.session.commit()
        print("Usuário 'admin' criado com sucesso!")
    else:
        print("Usuário 'admin' já existe.")