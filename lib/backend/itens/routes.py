# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify

from lib.backend.itens.service import (
    listar_itens,
    buscar_item_por_id,
    buscar_item_por_numero,
    criar_item,
    atualizar_item,
    deletar_item
)

itens_bp = Blueprint('itens', __name__, url_prefix='/itens')


# ========== PAGINAS ==========

@itens_bp.route('/')
def home():
    """Pagina principal de itens"""
    return render_template('itens/home.html')


# ========== API ==========

@itens_bp.route('/api/itens', methods=['GET'])
def api_listar_itens():
    """Lista todos os itens"""
    itens = listar_itens()
    return jsonify({
        'dados': itens,
        'total_registros': len(itens)
    })


@itens_bp.route('/api/itens/<int:item_id>', methods=['GET'])
def api_buscar_item(item_id):
    """Busca um item pelo ID"""
    item = buscar_item_por_id(item_id)
    if item:
        return jsonify(item)
    return jsonify({'error': 'Item nao encontrado'}), 404


@itens_bp.route('/api/itens/numero/<numero_item>', methods=['GET'])
def api_buscar_item_por_numero(numero_item):
    """Busca um item pelo numero"""
    item = buscar_item_por_numero(numero_item)
    if item:
        return jsonify(item)
    return jsonify({'error': 'Item nao encontrado'}), 404


@itens_bp.route('/api/itens', methods=['POST'])
def api_criar_item():
    """Cria um novo item"""
    dados = request.json

    numero_item = dados.get('numero_item', '').strip()
    descricao = dados.get('descricao', '').strip()
    unidade_medida = dados.get('unidade_medida', '').strip()

    if not numero_item:
        return jsonify({'error': 'Numero do item e obrigatorio'}), 400

    novo_item = criar_item(numero_item, descricao, unidade_medida)
    return jsonify({
        'success': True,
        'message': 'Item criado com sucesso',
        'item': novo_item
    })


@itens_bp.route('/api/itens/<int:item_id>', methods=['PUT'])
def api_atualizar_item(item_id):
    """Atualiza um item"""
    dados = request.json

    numero_item = dados.get('numero_item', '').strip()
    descricao = dados.get('descricao', '').strip()
    unidade_medida = dados.get('unidade_medida', '').strip()

    if not numero_item:
        return jsonify({'error': 'Numero do item e obrigatorio'}), 400

    item = atualizar_item(item_id, numero_item, descricao, unidade_medida)
    if item:
        return jsonify({
            'success': True,
            'message': 'Item atualizado com sucesso',
            'item': item
        })
    return jsonify({'error': 'Item nao encontrado'}), 404


@itens_bp.route('/api/itens/<int:item_id>', methods=['DELETE'])
def api_deletar_item(item_id):
    """Deleta um item"""
    if deletar_item(item_id):
        return jsonify({
            'success': True,
            'message': 'Item excluido com sucesso'
        })
    return jsonify({'error': 'Item nao encontrado'}), 404
