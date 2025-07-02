from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from app.models import Usuario

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    return render_template('main_menu.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Sua lógica de login vem para cá...
    # Após o sucesso, redirecione para o menu principal:
    # return redirect(url_for('main.index'))
    pass

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))