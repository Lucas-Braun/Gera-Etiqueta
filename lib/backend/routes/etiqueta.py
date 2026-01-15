from flask import Blueprint, render_template, request, jsonify, make_response, session, redirect, url_for, flash
import barcode
from barcode.writer import ImageWriter
import io
import base64
from datetime import datetime
from dateutil.relativedelta import relativedelta

from lib.backend.data_service import (
    listar_produtos,
    buscar_produto_por_id,
    buscar_produto_por_numero,
    criar_produto,
    atualizar_produto,
    deletar_produto
)

etiqueta_bp = Blueprint('etiqueta', __name__, url_prefix='/etiqueta')


# ========== PAGINAS PRINCIPAIS ==========

@etiqueta_bp.route('/')
@etiqueta_bp.route('/home')
def home():
    """Pagina inicial do modulo Etiqueta"""
    return render_template('etiqueta/home.html')


@etiqueta_bp.route('/gerar', methods=['GET', 'POST'])
def gerar_etiqueta():
    """Pagina para gerar etiquetas"""
    if request.method == 'POST':
        try:
            # Receber dados do formulario
            dados = {
                'descricao': request.form.get('descricao', ''),
                'produto_id': request.form.get('produto_id', ''),
                'codigo_etiqueta': request.form.get('produto_id', ''),
                'peso': request.form.get('peso', ''),
                'data_fabricacao': request.form.get('data_fabricacao', ''),
                'validade_meses': request.form.get('validade_meses', ''),
                'cnpj': request.form.get('cnpj', ''),
                'codigo_barras': request.form.get('codigo_barras', ''),
                'codigo_barras_lote': request.form.get('codigo_barras_lote', ''),
                'lote': request.form.get('lote', '')
            }

            # Configuracoes de dimensoes
            configuracoes = {
                'largura': request.form.get('largura', '100'),
                'altura': request.form.get('altura', '75'),
                'tamanho_fonte': request.form.get('tamanho_fonte', '8')
            }

            # Gerar codigos de barras
            codigo_barras_img = None
            codigo_barras_lote_img = None

            # Codigo de barras DUN
            if dados['codigo_barras'] and dados['codigo_barras'].strip():
                codigo_barras_img = gerar_codigo_barras(dados['codigo_barras'].strip())

            # Codigo de barras Lote
            if dados['codigo_barras_lote'] and dados['codigo_barras_lote'].strip():
                codigo_barras_lote_img = gerar_codigo_barras(dados['codigo_barras_lote'].strip())

            # Formatar data de fabricacao
            if dados['data_fabricacao']:
                try:
                    data_fab = datetime.strptime(dados['data_fabricacao'], '%Y-%m-%d')
                    dados['data_fabricacao_formatada'] = data_fab.strftime('%d/%m/%Y')

                    # Calcular data de validade
                    if dados['validade_meses']:
                        meses = int(dados['validade_meses'])
                        data_val = data_fab + relativedelta(months=meses)
                        dados['data_validade_formatada'] = data_val.strftime('%d/%m/%Y')
                    else:
                        dados['data_validade_formatada'] = ''
                except:
                    dados['data_fabricacao_formatada'] = dados['data_fabricacao']
                    dados['data_validade_formatada'] = ''
            else:
                dados['data_fabricacao_formatada'] = ''
                dados['data_validade_formatada'] = ''

            # Salvar na sessao
            session['etiqueta_dados'] = dados
            session['etiqueta_configuracoes'] = configuracoes

            return render_template('etiqueta/visualizar.html',
                                   dados=dados,
                                   configuracoes=configuracoes,
                                   codigo_barras_img=codigo_barras_img,
                                   codigo_barras_lote_img=codigo_barras_lote_img)

        except Exception as e:
            print(f"Erro ao processar etiqueta: {e}")
            flash(f'Erro interno: {str(e)}', 'error')
            return redirect(url_for('etiqueta.gerar_etiqueta'))

    # GET - carregar dados salvos
    dados_salvos = session.get('etiqueta_dados', {})
    configuracoes_salvas = session.get('etiqueta_configuracoes', {})

    return render_template('etiqueta/gerar.html',
                           dados_salvos=dados_salvos,
                           configuracoes_salvas=configuracoes_salvas)


@etiqueta_bp.route('/nova')
def nova_etiqueta():
    """Limpa sessao e redireciona para nova etiqueta"""
    session.pop('etiqueta_dados', None)
    session.pop('etiqueta_configuracoes', None)
    return redirect(url_for('etiqueta.gerar_etiqueta'))


# ========== CADASTRO DE PRODUTOS ==========

@etiqueta_bp.route('/produtos')
def listar_produtos_view():
    """Lista todos os produtos cadastrados"""
    produtos = listar_produtos()
    return render_template('etiqueta/produtos.html', produtos=produtos)


@etiqueta_bp.route('/produtos/novo', methods=['GET', 'POST'])
def novo_produto():
    """Cadastra novo produto"""
    if request.method == 'POST':
        try:
            numero = int(request.form.get('numero', 0))
            descricao = request.form.get('descricao', '').strip()
            peso = request.form.get('peso', '').strip()
            validade_meses = request.form.get('validade_meses', '')
            cnpj = request.form.get('cnpj', '').strip()
            dun = request.form.get('dun', '').strip()

            if not numero:
                flash('Numero do produto e obrigatorio', 'error')
                return render_template('etiqueta/produto_form.html')

            if not descricao:
                flash('Descricao e obrigatoria', 'error')
                return render_template('etiqueta/produto_form.html')

            validade = int(validade_meses) if validade_meses else None

            produto, erro = criar_produto(descricao, numero, peso, validade, cnpj, dun)

            if erro:
                flash(erro, 'error')
                return render_template('etiqueta/produto_form.html')

            flash('Produto cadastrado com sucesso!', 'success')
            return redirect(url_for('etiqueta.listar_produtos_view'))

        except Exception as e:
            flash(f'Erro ao cadastrar: {str(e)}', 'error')
            return render_template('etiqueta/produto_form.html')

    return render_template('etiqueta/produto_form.html')


@etiqueta_bp.route('/produtos/<int:produto_id>/editar', methods=['GET', 'POST'])
def editar_produto(produto_id):
    """Edita produto existente"""
    if request.method == 'POST':
        try:
            numero = int(request.form.get('numero', 0))
            descricao = request.form.get('descricao', '').strip()
            peso = request.form.get('peso', '').strip()
            validade_meses = request.form.get('validade_meses', '')
            cnpj = request.form.get('cnpj', '').strip()
            dun = request.form.get('dun', '').strip()

            validade = int(validade_meses) if validade_meses else None

            produto, erro = atualizar_produto(produto_id, numero, descricao, peso, validade, cnpj, dun)

            if erro:
                flash(erro, 'error')
                return redirect(url_for('etiqueta.editar_produto', produto_id=produto_id))

            flash('Produto atualizado com sucesso!', 'success')
            return redirect(url_for('etiqueta.listar_produtos_view'))

        except Exception as e:
            flash(f'Erro ao atualizar: {str(e)}', 'error')
            return redirect(url_for('etiqueta.editar_produto', produto_id=produto_id))

    # GET
    produto = buscar_produto_por_id(produto_id)
    if not produto:
        flash('Produto nao encontrado', 'error')
        return redirect(url_for('etiqueta.listar_produtos_view'))

    return render_template('etiqueta/produto_form.html', produto=produto)


@etiqueta_bp.route('/produtos/<int:produto_id>/deletar', methods=['POST'])
def deletar_produto_view(produto_id):
    """Deleta produto"""
    produto, erro = deletar_produto(produto_id)

    if erro:
        flash(erro, 'error')
    else:
        flash('Produto deletado com sucesso!', 'success')

    return redirect(url_for('etiqueta.listar_produtos_view'))


# ========== APIs ==========

@etiqueta_bp.route('/api/produto/<int:numero>')
def api_buscar_produto(numero):
    """API para buscar produto pelo numero"""
    produto = buscar_produto_por_numero(numero)

    if not produto:
        return jsonify({
            'success': False,
            'message': f'Produto com numero {numero} nao encontrado'
        }), 404

    return jsonify({
        'success': True,
        'produto': produto
    })


@etiqueta_bp.route('/api/codigo-barras')
def api_codigo_barras():
    """API para gerar codigo de barras"""
    codigo = request.args.get('codigo')
    if not codigo:
        return jsonify({'erro': 'Codigo nao fornecido'}), 400

    try:
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(codigo, writer=ImageWriter())

        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.2,
            'module_height': 15.0,
            'quiet_zone': 6.5,
            'font_size': 10,
            'text_distance': 5.0,
            'background': 'white',
            'foreground': 'black'
        })
        buffer.seek(0)

        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'image/png'
        return response

    except Exception as e:
        return jsonify({'erro': str(e)}), 500


# ========== FUNCOES AUXILIARES ==========

def gerar_codigo_barras(codigo):
    """Gera codigo de barras em base64"""
    try:
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(str(codigo), writer=ImageWriter())

        buffer = io.BytesIO()
        barcode_instance.write(buffer, options={
            'module_width': 0.22,
            'module_height': 7.0,
            'quiet_zone': 2.5,
            'font_size': 0,
            'text_distance': 0,
            'background': 'white',
            'foreground': 'black',
            'dpi': 300
        })
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

    except Exception as e:
        print(f"Erro ao gerar codigo de barras: {e}")
        return None
