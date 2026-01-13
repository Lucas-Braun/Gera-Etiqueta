import json
import os
from datetime import datetime

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'produtos.json')


def carregar_dados():
    """Carrega dados do arquivo JSON"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"produtos": [], "ultimo_id": 0}


def salvar_dados(dados):
    """Salva dados no arquivo JSON"""
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def listar_produtos():
    """Lista todos os produtos"""
    dados = carregar_dados()
    return dados.get('produtos', [])


def buscar_produto_por_id(produto_id):
    """Busca produto pelo ID"""
    dados = carregar_dados()
    for produto in dados.get('produtos', []):
        if produto['id'] == produto_id:
            return produto
    return None


def buscar_produto_por_numero(numero):
    """Busca produto pelo numero"""
    dados = carregar_dados()
    for produto in dados.get('produtos', []):
        if produto['numero'] == numero:
            return produto
    return None


def criar_produto(descricao, numero, peso, validade_meses, cnpj, dun):
    """Cria um novo produto"""
    dados = carregar_dados()

    # Verificar se numero ja existe
    for produto in dados.get('produtos', []):
        if produto['numero'] == numero:
            return None, f"Produto com numero {numero} ja existe"

    novo_id = dados.get('ultimo_id', 0) + 1

    novo_produto = {
        'id': novo_id,
        'numero': numero,
        'descricao': descricao.upper(),
        'peso': peso,
        'validade_meses': validade_meses,
        'cnpj': cnpj,
        'dun': dun,
        'dt_criacao': datetime.now().strftime('%Y-%m-%d')
    }

    dados['produtos'].append(novo_produto)
    dados['ultimo_id'] = novo_id

    salvar_dados(dados)
    return novo_produto, None


def atualizar_produto(produto_id, peso=None, validade_meses=None, cnpj=None):
    """Atualiza um produto existente"""
    dados = carregar_dados()

    for i, produto in enumerate(dados.get('produtos', [])):
        if produto['id'] == produto_id:
            if peso is not None:
                dados['produtos'][i]['peso'] = peso
            if validade_meses is not None:
                dados['produtos'][i]['validade_meses'] = validade_meses
            if cnpj is not None:
                dados['produtos'][i]['cnpj'] = cnpj
            dados['produtos'][i]['dt_atualizacao'] = datetime.now().strftime('%Y-%m-%d')

            salvar_dados(dados)
            return dados['produtos'][i], None

    return None, "Produto nao encontrado"


def deletar_produto(produto_id):
    """Deleta um produto"""
    dados = carregar_dados()

    for i, produto in enumerate(dados.get('produtos', [])):
        if produto['id'] == produto_id:
            produto_removido = dados['produtos'].pop(i)
            salvar_dados(dados)
            return produto_removido, None

    return None, "Produto nao encontrado"
