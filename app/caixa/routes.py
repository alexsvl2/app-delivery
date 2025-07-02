# app/caixa/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import date, timedelta
from decimal import Decimal

# Importa o 'db' e o modelo 'Transacao' do arquivo central 'models.py'
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

    return render_template(
        'caixa/index.html', 
        saldo=saldo, 
        total_entradas=total_entradas, 
        total_saidas=total_saidas,
        total_fiados=total_fiados,
        today_date=date.today().isoformat() # Adicionado para o formulário no modal
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
    try:
        data_str = request.form.get('data_transacao')
        
        # AQUI ESTÁ A CORREÇÃO
        valor_str = request.form['valor'].replace(',', '.')
        valor = Decimal(valor_str)

        nova_transacao = Transacao(
            data_transacao=date.fromisoformat(data_str) if data_str else date.today(),
            tipo=request.form['tipo'],
            descricao=request.form['descricao'],
            valor=valor
        )
        db.session.add(nova_transacao)
        db.session.commit()
        flash('Transação adicionada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao adicionar transação: {e}", 'danger')
        
    return redirect(url_for('caixa.index'))

@caixa_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    if request.method == 'POST':
        try:
            transacao.data_transacao = date.fromisoformat(request.form['data_transacao'])
            transacao.tipo = request.form['tipo']
            transacao.descricao = request.form['descricao']
            
            valor_str = request.form['valor'].replace(',', '.')
            transacao.valor = Decimal(valor_str)
            
            db.session.commit()
            flash('Transação atualizada com sucesso!', 'success')
            return redirect(url_for('caixa.extrato'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao editar transação: {e}", 'danger')

    return render_template('caixa/edit.html', transacao=transacao)

@caixa_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    try:
        db.session.delete(transacao)
        db.session.commit()
        flash('Transação excluída com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao excluir transação: {e}", 'danger')
        
    return redirect(url_for('caixa.extrato'))