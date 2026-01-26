# -*- coding: utf-8 -*-
import json
import os

ITENS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'itens.json')


def carregar_itens():
    """Carrega os itens do arquivo JSON"""
    if os.path.exists(ITENS_FILE):
        with open(ITENS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'itens': [], 'proximo_id': 1}


def salvar_itens(dados):
    """Salva os itens no arquivo JSON"""
    with open(ITENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def listar_itens():
    """Lista todos os itens"""
    dados = carregar_itens()
    return dados['itens']


def buscar_item_por_id(item_id):
    """Busca um item pelo ID"""
    dados = carregar_itens()
    for item in dados['itens']:
        if item['id'] == item_id:
            return item
    return None


def buscar_item_por_numero(numero_item):
    """Busca um item pelo número"""
    dados = carregar_itens()
    for item in dados['itens']:
        if item['numero_item'] == str(numero_item):
            return item
    return None


def criar_item(numero_item, descricao, unidade_medida):
    """Cria um novo item"""
    dados = carregar_itens()

    novo_item = {
        'id': dados['proximo_id'],
        'numero_item': numero_item,
        'descricao': descricao,
        'unidade_medida': unidade_medida
    }

    dados['itens'].append(novo_item)
    dados['proximo_id'] += 1
    salvar_itens(dados)

    return novo_item


def atualizar_item(item_id, numero_item, descricao, unidade_medida):
    """Atualiza um item existente"""
    dados = carregar_itens()

    for item in dados['itens']:
        if item['id'] == item_id:
            item['numero_item'] = numero_item
            item['descricao'] = descricao
            item['unidade_medida'] = unidade_medida
            salvar_itens(dados)
            return item

    return None


def deletar_item(item_id):
    """Deleta um item"""
    dados = carregar_itens()

    for i, item in enumerate(dados['itens']):
        if item['id'] == item_id:
            dados['itens'].pop(i)
            salvar_itens(dados)
            return True

    return False
