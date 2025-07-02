# app/auth/routes.py (VERSÃO CORRIGIDA)

# AQUI ESTÁ A CORREÇÃO: Adicionamos 'request' e 'flash' à linha de importação
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user, login_user, logout_user
from app.models import db, Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
@login_required
def index():
    return render_template('main_menu.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
        
    if request.method == 'POST':
        user = Usuario.query.filter_by(username=request.form.get('username')).first()
        if user and user.check_password(request.form.get('password')):
            login_user(user)
            return redirect(url_for('auth.index'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
            
    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))