# app/pedidos/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import db, Pedido, Cliente, Produto, ItemPedido
from datetime import date
from sqlalchemy import cast, Date
from decimal import Decimal

# Criação do Blueprint de Pedidos
pedidos_bp = Blueprint('pedidos', __name__, template_folder='templates')


# --- ROTAS DO MENU E VENDAS ---

@pedidos_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard_menu.html')

@pedidos_bp.route('/venda/delivery')
@login_required
def venda_delivery():
    hoje = date.today()
    pedidos_do_dia = Pedido.query.filter(cast(Pedido.data_pedido, Date) == hoje, Pedido.tipo_pedido == 'Delivery').order_by(Pedido.data_pedido.desc()).all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('venda_form.html', tipo_venda='Delivery', pedidos_do_dia=pedidos_do_dia, clientes=clientes, produtos=produtos)

@pedidos_bp.route('/venda/balcao')
@login_required
def venda_balcao():
    hoje = date.today()
    pedidos_do_dia = Pedido.query.filter(cast(Pedido.data_pedido, Date) == hoje, Pedido.tipo_pedido == 'Retirada').order_by(Pedido.data_pedido.desc()).all()
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('venda_form.html', tipo_venda='Retirada', pedidos_do_dia=pedidos_do_dia, clientes=clientes, produtos=produtos)

@pedidos_bp.route('/mesas')
@login_required
def gerenciar_mesas():
    return render_template('mesas.html')


# --- ROTAS DE AÇÕES DE PEDIDO ---

@pedidos_bp.route('/novo', methods=['POST'])
@login_required
def novo_pedido():
    tipo_pedido = request.form.get('tipo_pedido')
    try:
        cliente_id = request.form.get('cliente_id')
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
    
    if tipo_pedido == 'Delivery':
        return redirect(url_for('pedidos.venda_delivery'))
    else:
        return redirect(url_for('pedidos.venda_balcao'))

@pedidos_bp.route('/editar/<int:pedido_id>', methods=['GET', 'POST'])
@login_required
def editar_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        flash('Pedido não encontrado.', 'danger')
        return redirect(url_for('pedidos.dashboard'))

    if request.method == 'POST':
        try:
            # Limpa itens antigos para adicionar os novos. É mais simples do que comparar.
            for item in pedido.itens:
                db.session.delete(item)
            
            # Atualiza os dados do pedido
            pedido.cliente_id = request.form['cliente_id']
            cliente_selecionado = db.session.get(Cliente, int(pedido.cliente_id))
            pedido.nome_cliente = cliente_selecionado.nome
            pedido.tipo_pedido = request.form['tipo_pedido']
            
            # Adiciona os novos itens
            produto_ids = request.form.getlist('produto_id[]')
            quantidades = request.form.getlist('item_quantidade[]')
            
            valor_total_itens = Decimal('0.0')
            for i in range(len(produto_ids)):
                if produto_ids[i] and quantidades[i]:
                    produto = db.session.get(Produto, int(produto_ids[i]))
                    if produto:
                        item = ItemPedido(
                            produto_id=produto.id,
                            produto_descricao=produto.descricao,
                            quantidade=int(quantidades[i]),
                            valor_unitario=produto.valor
                        )
                        pedido.itens.append(item)
                        valor_total_itens += item.quantidade * item.valor_unitario

            valor_entrega = Decimal('0.0')
            if pedido.tipo_pedido == 'Delivery':
                valor_entrega = Decimal(request.form.get('valor_entrega', '0.0').replace(',', '.'))

            pedido.valor_entrega = valor_entrega
            pedido.valor_total = valor_total_itens + valor_entrega
            
            db.session.commit()
            flash('Pedido atualizado com sucesso!', 'success')
            # Redireciona para o histórico para ver o pedido atualizado
            return redirect(url_for('pedidos.historico'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar o pedido: {e}', 'danger')
            
    clientes = Cliente.query.order_by(Cliente.nome).all()
    produtos = Produto.query.order_by(Produto.descricao).all()
    return render_template('editar_pedido.html', pedido=pedido, clientes=clientes, produtos=produtos)

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
    return render_template('imprimir_pedido.html', pedido=pedido)

# --- ROTAS DE GESTÃO ---
@pedidos_bp.route('/historico')
@login_required
def historico():
    pedidos = Pedido.query.order_by(Pedido.data_pedido.desc()).all()
    return render_template('historico.html', pedidos=pedidos)

@pedidos_bp.route('/clientes')
@login_required
def gerenciar_clientes():
    clientes = Cliente.query.order_by(Cliente.nome).all()
    return render_template('clientes.html', clientes=clientes)

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
    return render_template('produtos.html', produtos=produtos)

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
    # Idealmente, verificar se o produto está em algum ItemPedido antes de excluir
    if produto:
        db.session.delete(produto)
        db.session.commit()
        flash('Produto excluído.', 'success')
    return redirect(url_for('pedidos.gerenciar_produtos'))