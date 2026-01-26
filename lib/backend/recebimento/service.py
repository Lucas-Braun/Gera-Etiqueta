import json
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lotes.json')


def carregar_lotes():
    """Carrega dados do arquivo JSON"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"lotes": [], "ultimo_id": 0}


def salvar_lotes(dados):
    """Salva dados no arquivo JSON"""
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def listar_lotes():
    """Lista todos os lotes"""
    dados = carregar_lotes()
    # Retornar ordenado por data de cadastro (mais recente primeiro)
    lotes = dados.get('lotes', [])
    return sorted(lotes, key=lambda x: x.get('dt_cadastro', ''), reverse=True)


def buscar_lote_por_id(lote_id):
    """Busca lote pelo ID"""
    dados = carregar_lotes()
    for lote in dados.get('lotes', []):
        if lote['id'] == lote_id:
            return lote
    return None


def criar_lote(numero_lote, id_item=None, data_recebimento=None, data_fabricacao=None, data_validade=None,
               quantidade=None, numero_nota_fiscal=None, observacao=None):
    """Cria um novo lote"""
    dados = carregar_lotes()

    novo_id = dados.get('ultimo_id', 0) + 1

    novo_lote = {
        'id': novo_id,
        'numero_lote': numero_lote.upper(),
        'id_item': id_item,
        'data_recebimento': data_recebimento,
        'data_fabricacao': data_fabricacao,
        'data_validade': data_validade,
        'quantidade': quantidade,
        'numero_nota_fiscal': numero_nota_fiscal,
        'observacao': observacao,
        'dt_cadastro': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    dados['lotes'].append(novo_lote)
    dados['ultimo_id'] = novo_id

    salvar_lotes(dados)
    return novo_lote, None


def atualizar_lote(lote_id, numero_lote=None, id_item=None, data_recebimento=None, data_fabricacao=None,
                  data_validade=None, quantidade=None, numero_nota_fiscal=None, observacao=None):
    """Atualiza um lote existente"""
    dados = carregar_lotes()

    for i, lote in enumerate(dados.get('lotes', [])):
        if lote['id'] == lote_id:
            if numero_lote is not None:
                dados['lotes'][i]['numero_lote'] = numero_lote.upper()
            if id_item is not None:
                dados['lotes'][i]['id_item'] = id_item
            if data_recebimento is not None:
                dados['lotes'][i]['data_recebimento'] = data_recebimento
            if data_fabricacao is not None:
                dados['lotes'][i]['data_fabricacao'] = data_fabricacao
            if data_validade is not None:
                dados['lotes'][i]['data_validade'] = data_validade
            if quantidade is not None:
                dados['lotes'][i]['quantidade'] = quantidade
            if numero_nota_fiscal is not None:
                dados['lotes'][i]['numero_nota_fiscal'] = numero_nota_fiscal
            if observacao is not None:
                dados['lotes'][i]['observacao'] = observacao
            dados['lotes'][i]['dt_atualizacao'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            salvar_lotes(dados)
            return dados['lotes'][i], None

    return None, "Lote nao encontrado"


def deletar_lote(lote_id):
    """Deleta um lote"""
    dados = carregar_lotes()

    for i, lote in enumerate(dados.get('lotes', [])):
        if lote['id'] == lote_id:
            lote_removido = dados['lotes'].pop(i)
            salvar_lotes(dados)
            return lote_removido, None

    return None, "Lote nao encontrado"
