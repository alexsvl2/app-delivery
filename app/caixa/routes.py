# app/caixa/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, timedelta

# Importa o 'db' e o modelo 'Transacao' do arquivo central de modelos
from app.models import db, Transacao

# Criação do Blueprint de Caixa
caixa_bp = Blueprint(
    'caixa', 
    __name__, 
    template_folder='templates'
)

# --- ROTAS DA APLICAÇÃO DE CAIXA ---

@caixa_bp.route('/')
@caixa_bp.route('/dashboard')
@login_required
def index():
    transacoes = Transacao.query.all()
    total_entradas = sum(t.valor for t in transacoes if t.tipo == 'entrada')
    total_saidas = sum(t.valor for t in transacoes if t.tipo == 'saida')
    total_fiados = sum(t.valor for t in transacoes if t.tipo == 'fiado')
    
    saldo = total_entradas - total_saidas

    # Aponta para o template dentro da pasta de templates do blueprint de caixa
    return render_template(
        'caixa/index.html', 
        saldo=saldo, 
        total_entradas=total_entradas, 
        total_saidas=total_saidas,
        total_fiados=total_fiados
    )

@caixa_bp.route('/extrato')
@login_required
def extrato():
    query = Transacao.query
    tipo_filtro = request.args.get('tipo_filtro', 'todos')
    if tipo_filtro and tipo_filtro != 'todos':
        query = query.filter(Transacao.tipo == tipo_filtro)
    
    periodo = request.args.get('periodo', 'mes_atual')
    today = date.today()
    
    start_date_filtro = request.args.get('start_date')
    end_date_filtro = request.args.get('end_date')

    if periodo == 'semana_atual':
        start_date_filtro = today - timedelta(days=today.weekday())
        query = query.filter(Transacao.data_transacao >= start_date_filtro)
    elif periodo == 'ultimos_7_dias':
        start_date_filtro = today - timedelta(days=6)
        query = query.filter(Transacao.data_transacao >= start_date_filtro)
    elif periodo == 'ultimos_15_dias':
        start_date_filtro = today - timedelta(days=14)
        query = query.filter(Transacao.data_transacao >= start_date_filtro)
    elif periodo == 'personalizado':
        if start_date_filtro and end_date_filtro:
            query = query.filter(Transacao.data_transacao.between(start_date_filtro, end_date_filtro))
    else: # mes_atual
        start_date_filtro = today.replace(day=1)
        query = query.filter(Transacao.data_transacao >= start_date_filtro)
        
    transacoes = query.order_by(Transacao.data_transacao.desc(), Transacao.id.desc()).all()
    
    total_entradas_periodo = sum(t.valor for t in transacoes if t.tipo == 'entrada')
    total_saidas_periodo = sum(t.valor for t in transacoes if t.tipo == 'saida')
    total_fiados_periodo = sum(t.valor for t in transacoes if t.tipo == 'fiado')
    saldo_periodo = total_entradas_periodo - total_saidas_periodo
    
    return render_template('caixa/extrato.html', transacoes=transacoes, 
                           periodo_selecionado=periodo,
                           tipo_selecionado=tipo_filtro,
                           start_date=start_date_filtro, end_date=end_date_filtro,
                           saldo_periodo=saldo_periodo, total_entradas_periodo=total_entradas_periodo, 
                           total_saidas_periodo=total_saidas_periodo, total_fiados_periodo=total_fiados_periodo)

@caixa_bp.route('/add', methods=['POST'])
@login_required
def add_transacao():
    data_str = request.form.get('data_transacao')
    nova_transacao = Transacao(
        data_transacao=date.fromisoformat(data_str) if data_str else date.today(),
        tipo=request.form['tipo'],
        descricao=request.form['descricao'],
        valor=float(request.form['valor'])
    )
    db.session.add(nova_transacao)
    db.session.commit()
    # Redireciona para a nova rota 'index' dentro do blueprint 'caixa'
    return redirect(url_for('caixa.index'))

@caixa_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    if request.method == 'POST':
        transacao.data_transacao = date.fromisoformat(request.form['data_transacao'])
        transacao.tipo = request.form['tipo']
        transacao.descricao = request.form['descricao']
        transacao.valor = float(request.form['valor'])
        db.session.commit()
        return redirect(url_for('caixa.extrato'))
    return render_template('caixa/edit.html', transacao=transacao)

@caixa_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    return redirect(url_for('caixa.extrato'))