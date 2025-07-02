# run.py

from app import create_app

# Chama a função que cria e configura nossa aplicação
app = create_app()

if __name__ == '__main__':
    # Roda o servidor de desenvolvimento do Flask
    app.run(debug=True)