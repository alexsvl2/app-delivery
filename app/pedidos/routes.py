# app/pedidos/routes.py (VERSÃO FINAL COM NOVO MENU)

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Pedido, Cliente, Produto, ItemPedido
from datetime import date
from sqlalchemy import cast, Date
from decimal import Decimal

# Criação do Blueprint de Pedidos
pedidos_bp = Blueprint('pedidos', __name__, template_folder='templates')

# ROTA PRINCIPAL DO BLUEPRINT DE PEDIDOS - AGORA MOSTRA O MENU DE ÍCONES
@pedidos_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('pedidos/dashboard_menu.html')

# NOVA ROTA PARA A PÁGINA DE VENDAS DELIVERY
@pedidos_bp.route('/venda/delivery')
@login_required
def venda_delivery():
    hoje = date.today()
    pedidos_do_dia = Pedido.query.filter(cast(Pedido.data_pedido, Date) == hoje, Pedido.tipo_pedido == 'Delivery').order_by(Pedido.data_pedido.desc()).all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('pedidos/venda_form.html', tipo_venda='Delivery', pedidos_do_dia=pedidos_do_dia, clientes=clientes, produtos=produtos)

# NOVA ROTA PARA A PÁGINA DE VENDAS NO BALCÃO
@pedidos_bp.route('/venda/balcao')
@login_required
def venda_balcao():
    hoje = date.today()
    pedidos_do_dia = Pedido.query.filter(cast(Pedido.data_pedido, Date) == hoje, Pedido.tipo_pedido == 'Retirada').order_by(Pedido.data_pedido.desc()).all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('pedidos/venda_form.html', tipo_venda='Retirada', pedidos_do_dia=pedidos_do_dia, clientes=clientes, produtos=produtos)

# NOVA ROTA PARA A PÁGINA DE MESAS (EXEMPLO)
@pedidos_bp.route('/mesas')
@login_required
def gerenciar_mesas():
    return render_template('pedidos/mesas.html')

# ROTA PARA SALVAR O PEDIDO
@pedidos_bp.route('/novo', methods=['POST'])
@login_required
def novo_pedido():
    try:
        cliente_id = request.form.get('cliente_id')
        tipo_pedido = request.form['tipo_pedido']

        if not cliente_id:
            flash('Selecione um cliente para o pedido.', 'warning')
            return redirect(request.referrer or url_for('pedidos.dashboard'))

        cliente_selecionado = db.session.get(Cliente, int(cliente_id))
        
        novo_pedido = Pedido(
            cliente_id=cliente_id,
            nome_cliente=cliente_selecionado.nome,
            tipo_pedido=tipo_pedido
        )
        
        produto_ids = request.form.getlist('produto_id[]')
        quantidades = request.form.getlist('item_quantidade[]')
        
        if not produto_ids:
            flash('Adicione pelo menos um item ao pedido.', 'warning')
            return redirect(request.referrer or url_for('pedidos.dashboard'))

        valor_total_itens = Decimal('0.0')

        for i in range(len(produto_ids)):
            if produto_ids[i]:
                produto = db.session.get(Produto, int(produto_ids[i]))
                if produto:
                    quantidade = int(quantidades[i])
                    item = ItemPedido(
                        produto_id=produto.id,
                        produto_descricao=produto.descricao,
                        quantidade=quantidade,
                        valor_unitario=produto.valor
                    )
                    novo_pedido.itens.append(item)
                    valor_total_itens += quantidade * produto.valor
        
        valor_entrega = Decimal('0.0')
        if novo_pedido.tipo_pedido == 'Delivery':
            valor_entrega = Decimal(request.form.get('valor_entrega', '0.0').replace(',', '.'))
        
        novo_pedido.valor_entrega = valor_entrega
        novo_pedido.valor_total = valor_total_itens + valor_entrega
        
        db.session.add(novo_pedido)
        db.session.commit()
        flash('Pedido cadastrado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar pedido: {e}', 'danger')
    
    # Redireciona de volta para a página de origem da venda
    if tipo_pedido == 'Delivery':
        return redirect(url_for('pedidos.venda_delivery'))
    else:
        return redirect(url_for('pedidos.venda_balcao'))


@pedidos_bp.route('/excluir/<int:pedido_id>', methods=['POST'])
@login_required
def excluir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if pedido:
        db.session.delete(pedido)
        db.session.commit()
        flash('Pedido excluído com sucesso!', 'success')
    return redirect(request.referrer or url_for('pedidos.dashboard'))

@pedidos_bp.route('/imprimir/<int:pedido_id>')
@login_required
def imprimir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        return "Pedido não encontrado", 404
    return render_template('pedidos/imprimir_pedido.html', pedido=pedido)

@pedidos_bp.route('/historico')
@login_required
def historico():
    pedidos = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    return render_template('pedidos/historico.html', pedidos=pedidos)

@pedidos_bp.route('/clientes')
@login_required
def gerenciar_clientes():
    clientes = Cliente.query.order_by(Cliente.nome).all()
    return render_template('pedidos/clientes.html', clientes=clientes)

@pedidos_bp.route('/clientes/novo', methods=['POST'])
@login_required
def novo_cliente():
    try:
        novo = Cliente(nome=request.form['nome'], telefone=request.form.get('telefone'), endereco=request.form.get('endereco'), bairro=request.form.get('bairro'))
        db.session.add(novo)
        db.session.commit()
        flash('Cliente cadastrado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('pedidos.gerenciar_clientes'))

@pedidos_bp.route('/clientes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_cliente(id):
    cliente = db.session.get(Cliente, id)
    if cliente and not cliente.pedidos:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente excluído.', 'success')
    elif cliente:
        flash('Não é possível excluir um cliente que já possui pedidos.', 'warning')
    return redirect(url_for('pedidos.gerenciar_clientes'))

@pedidos_bp.route('/produtos')
@login_required
def gerenciar_produtos():
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('pedidos/produtos.html', produtos=produtos)

@pedidos_bp.route('/produtos/novo', methods=['POST'])
@login_required
def novo_produto():
    try:
        valor = Decimal(request.form.get('valor', '0.0').replace(',', '.'))
        novo = Produto(descricao=request.form['descricao'], valor=valor)
        db.session.add(novo)
        db.session.commit()
        flash('Produto cadastrado!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('pedidos.gerenciar_produtos'))

@pedidos_bp.route('/produtos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = db.session.get(Produto, id)
    # seria ideal verificar se o produto está em algum pedido antes de excluir
    if produto:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído.', 'success')
    return redirect(url_for('pedidos.gerenciar_produtos'))