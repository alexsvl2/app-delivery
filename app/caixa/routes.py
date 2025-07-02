# app/caixa/routes.py (VERSÃO CORRIGIDA)

from flask import Blueprint, render_template
from flask_login import login_required

# AQUI ESTÁ A LINHA QUE FALTAVA:
# Ela cria a variável 'caixa_bp' que o __init__.py tenta importar.
caixa_bp = Blueprint(
    'caixa', 
    __name__, 
    template_folder='templates'
)


@caixa_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Esta é a rota principal do seu fluxo de caixa.
    Por enquanto, é apenas uma página de exemplo.
    """
    
    # O render_template vai procurar o arquivo na pasta 'app/caixa/templates/caixa/'
    return render_template('caixa/dashboard.html')

# Adicione outras rotas do seu fluxo de caixa aqui no futuro