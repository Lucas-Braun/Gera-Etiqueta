from flask import Blueprint, render_template, request, jsonify, make_response, session, redirect, url_for, flash
from lib.app.decorators.decorador import permissao_necessaria
from lib.app.decorators.perm_sidebar import configure_etiqueta
from db import get_db_connection_mega, return_db_connection_mega
import barcode
from barcode.writer import ImageWriter
import io
import base64
from datetime import datetime

etiqueta_home_bp = Blueprint('etiqueta_home_bp', __name__)

@etiqueta_home_bp.route('/home')
#@permissao_necessaria('etiqueta_home', 'visualizar')
def etiqueta_home():
    """Página inicial do módulo Etiqueta"""
    configure_etiqueta()
    return render_template('etiqueta/home.html')

@etiqueta_home_bp.route('/gerar', methods=['GET', 'POST'])
#@permissao_necessaria('etiqueta_gerar', 'inserir')
def gerar_etiqueta():
    """Página para gerar etiquetas"""
    configure_etiqueta()
    
    if request.method == 'POST':
        try:
            # Receber dados do formulário
            dados = {
                'descricao': request.form.get('descricao', ''),
                'produto_id': request.form.get('produto_id', ''),
                'codigo_etiqueta': request.form.get('produto_id', ''),  # Usar produto_id como código
                'peso': request.form.get('peso', ''),
                'data_fabricacao': request.form.get('data_fabricacao', ''),
                'validade_meses': request.form.get('validade_meses', ''),
                'cnpj': request.form.get('cnpj', ''),
                'codigo_barras': request.form.get('codigo_barras', ''),
                'codigo_barras_lote': request.form.get('codigo_barras_lote', '')
            }
            
            # Debug para verificar os códigos
            print(f"DEBUG - Código DUN: '{dados['codigo_barras']}'")
            print(f"DEBUG - Código Lote: '{dados['codigo_barras_lote']}'")
            print(f"DEBUG - São iguais? {dados['codigo_barras'] == dados['codigo_barras_lote']}")
            print(f"DEBUG - DUN vazio? {not dados['codigo_barras']}")
            print(f"DEBUG - Lote vazio? {not dados['codigo_barras_lote']}")
            
            # Se os códigos são iguais, vamos forçar diferentes para teste
            if dados['codigo_barras'] and dados['codigo_barras_lote'] and dados['codigo_barras'] == dados['codigo_barras_lote']:
                print("AVISO - Códigos iguais detectados! Forçando diferença...")
                dados['codigo_barras_lote'] = dados['codigo_barras_lote'] + "L"  # Adiciona "L" de Lote
                print(f"DEBUG - Novo código Lote: '{dados['codigo_barras_lote']}'")
            
            # Receber configurações de dimensões
            configuracoes = {
                'largura': request.form.get('largura', '100'),
                'altura': request.form.get('altura', '75'),
                'tamanho_fonte': request.form.get('tamanho_fonte', '8')
            }
            
            # Gerar códigos de barras se fornecidos
            codigo_barras_img = None
            codigo_barras_lote_img = None
            
            # Gerar código de barras do produto (DUN)
            if dados['codigo_barras'] and dados['codigo_barras'].strip():
                try:
                    print(f"DEBUG - Gerando código DUN: '{dados['codigo_barras']}'")
                    # Usar Code128 para código de barras
                    code128 = barcode.get_barcode_class('code128')
                    barcode_instance = code128(str(dados['codigo_barras']).strip(), writer=ImageWriter())
                    
                    # Gerar imagem em memória
                    buffer_dun = io.BytesIO()
                    barcode_instance.write(buffer_dun, options={
                        'module_width': 0.22,
                        'module_height': 7.0,
                        'quiet_zone': 2.5,
                        'font_size': 0,
                        'text_distance': 0,
                        'background': 'white',
                        'foreground': 'black',
                        'dpi': 300
                    })
                    buffer_dun.seek(0)
                    
                    # Converter para base64 para usar no HTML
                    codigo_barras_img = base64.b64encode(buffer_dun.getvalue()).decode()
                    print(f"DEBUG - Código DUN gerado, tamanho: {len(buffer_dun.getvalue())} bytes")
                    
                except Exception as e:
                    print(f"Erro ao gerar código de barras do produto: {e}")
                    return jsonify({'erro': f'Erro ao gerar código de barras do produto: {str(e)}'}), 400
            
            # Gerar código de barras do lote
            if dados['codigo_barras_lote'] and dados['codigo_barras_lote'].strip():
                try:
                    print(f"DEBUG - Gerando código Lote: '{dados['codigo_barras_lote']}'")
                    # Usar Code128 para código de barras do lote
                    code128 = barcode.get_barcode_class('code128')
                    barcode_instance = code128(str(dados['codigo_barras_lote']).strip(), writer=ImageWriter())
                    
                    # Gerar imagem em memória
                    buffer_lote = io.BytesIO()
                    barcode_instance.write(buffer_lote, options={
                        'module_width': 0.22,
                        'module_height': 7.0,
                        'quiet_zone': 2.5,
                        'font_size': 0,
                        'text_distance': 0,
                        'background': 'white',
                        'foreground': 'black',
                        'dpi': 300
                    })
                    buffer_lote.seek(0)
                    
                    # Converter para base64 para usar no HTML
                    codigo_barras_lote_img = base64.b64encode(buffer_lote.getvalue()).decode()
                    print(f"DEBUG - Código Lote gerado, tamanho: {len(buffer_lote.getvalue())} bytes")
                    
                except Exception as e:
                    print(f"Erro ao gerar código de barras do lote: {e}")
                    return jsonify({'erro': f'Erro ao gerar código de barras do lote: {str(e)}'}), 400
            
            # Formatar datas para exibição
            if dados['data_fabricacao']:
                try:
                    # Converter de yyyy-mm-dd para dd/mm/yyyy
                    data_fab = datetime.strptime(dados['data_fabricacao'], '%Y-%m-%d')
                    dados['data_fabricacao_formatada'] = data_fab.strftime('%d/%m/%Y')
                except:
                    dados['data_fabricacao_formatada'] = dados['data_fabricacao']
            else:
                dados['data_fabricacao_formatada'] = ''

            # Salvar dados na sessão para o botão "Editar"
            session['etiqueta_dados'] = dados
            session['etiqueta_configuracoes'] = configuracoes

            # Debug final das imagens
            print(f"DEBUG - Imagem DUN gerada? {codigo_barras_img is not None}")
            print(f"DEBUG - Imagem Lote gerada? {codigo_barras_lote_img is not None}")
            if codigo_barras_img and codigo_barras_lote_img:
                print(f"DEBUG - Imagens são iguais? {codigo_barras_img == codigo_barras_lote_img}")
                print(f"DEBUG - Tamanho DUN: {len(codigo_barras_img)} chars")
                print(f"DEBUG - Tamanho Lote: {len(codigo_barras_lote_img)} chars")
            
            # Retornar dados para visualização da etiqueta
            return render_template('etiqueta/visualizar.html', 
                                 dados=dados, 
                                 configuracoes=configuracoes,
                                 codigo_barras_img=codigo_barras_img,
                                 codigo_barras_lote_img=codigo_barras_lote_img)
            
        except Exception as e:
            print(f"Erro ao processar etiqueta: {e}")
            return jsonify({'erro': f'Erro interno: {str(e)}'}), 500
    
    # Verificar se há dados salvos na sessão para preenchimento
    dados_salvos = session.get('etiqueta_dados', {})
    configuracoes_salvas = session.get('etiqueta_configuracoes', {})
    
    return render_template('etiqueta/gerar.html', 
                         dados_salvos=dados_salvos,
                         configuracoes_salvas=configuracoes_salvas)

@etiqueta_home_bp.route('/nova')
#@permissao_necessaria('etiqueta_gerar', 'inserir')
def nova_etiqueta():
    """Limpa a sessão e redireciona para gerar nova etiqueta"""
    # Limpar dados da sessão
    session.pop('etiqueta_dados', None)
    session.pop('etiqueta_configuracoes', None)
    
    # Redirecionar para a página de geração
    from flask import redirect, url_for
    return redirect(url_for('etiqueta_home_bp.gerar_etiqueta'))

@etiqueta_home_bp.route('/api/codigo-barras')
#@permissao_necessaria('etiqueta_gerar', 'visualizar')
def api_codigo_barras():
    """API para gerar código de barras"""
    try:
        codigo = request.args.get('codigo')
        if not codigo:
            return jsonify({'erro': 'Código não fornecido'}), 400
        
        # Gerar código de barras
        code128 = barcode.get_barcode_class('code128')
        barcode_instance = code128(codigo, writer=ImageWriter())
        
        # Gerar imagem em memória
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
        
        # Retornar imagem
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'image/png'
        response.headers['Content-Disposition'] = f'inline; filename=barcode_{codigo}.png'
        
        return response
        
    except Exception as e:
        print(f"Erro ao gerar código de barras via API: {e}")
        return jsonify({'erro': f'Erro ao gerar código de barras: {str(e)}'}), 500

# ========== CADASTRO DE ITENS ==========

@etiqueta_home_bp.route('/itens')
#@permissao_necessaria('etiqueta_itens', 'visualizar')
def listar_itens():
    """Lista todos os itens cadastrados"""
    configure_etiqueta()
    
    try:
        connection = get_db_connection_mega()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT proe_id, proe_in_numero, proe_descricao, proe_peso, proe_validade, 
                   proe_cnpj, proe_dun, dt_criacao
            FROM barbarex.pro_etiqueta
            ORDER BY dt_criacao DESC
        """)
        
        itens = []
        for row in cursor.fetchall():
            itens.append({
                'id': row[0],
                'numero': row[1],
                'descricao': row[2],
                'peso': row[3],
                'validade': row[4] if row[4] else '',
                'cnpj': row[5],
                'dun': row[6],
                'dt_criacao': row[7].strftime('%d/%m/%Y %H:%M') if row[7] else ''
            })
        
        return render_template('etiqueta/itens.html', itens=itens)
        
    except Exception as e:
        print(f"Erro ao listar itens: {e}")
        flash(f'Erro ao carregar itens: {str(e)}', 'error')
        return render_template('etiqueta/itens.html', itens=[])
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            return_db_connection_mega(connection)

@etiqueta_home_bp.route('/itens/novo', methods=['GET', 'POST'])
#@permissao_necessaria('etiqueta_itens', 'inserir')
def novo_item():
    """Cadastra um novo item"""
    configure_etiqueta()
    
    if request.method == 'POST':
        try:
            # Receber dados do formulário
            numero = request.form.get('numero', '').strip()
            descricao = request.form.get('descricao', '').strip()
            peso = request.form.get('peso', '').strip()
            validade = request.form.get('validade', '').strip()
            cnpj = request.form.get('cnpj', '').strip().replace('.', '').replace('-', '').replace('/', '')
            dun = request.form.get('dun', '').strip()
            
            # Validações
            if not numero:
                flash('ID do produto é obrigatório', 'error')
                return render_template('etiqueta/item_form.html')
            
            if not descricao:
                flash('Descrição é obrigatória', 'error')
                return render_template('etiqueta/item_form.html')
            
            connection = get_db_connection_mega()
            cursor = connection.cursor()
            
            # Preparar query
            sql = """
                INSERT INTO barbarex.pro_etiqueta 
                (proe_in_numero, proe_descricao, proe_peso, proe_validade, proe_cnpj, proe_dun)
                VALUES (:numero, :descricao, :peso, :validade, :cnpj, :dun)
            """
            
            # Preparar parâmetros
            params = {
                'numero': int(numero),
                'descricao': descricao,
                'peso': float(peso) if peso else None,
                'validade': validade if validade else None,
                'cnpj': cnpj if cnpj else None,
                'dun': dun if dun else None
            }
            
            cursor.execute(sql, params)
            connection.commit()
            
            flash('Item cadastrado com sucesso!', 'success')
            return redirect(url_for('etiqueta_home_bp.listar_itens'))
            
        except Exception as e:
            print(f"Erro ao cadastrar item: {e}")
            error_msg = str(e)
            if 'unique constraint' in error_msg.lower() or 'unq_pro_etiqueta_numero' in error_msg:
                flash(f'Erro: Já existe um item com o número {numero}. Use um número diferente.', 'error')
            else:
                flash(f'Erro ao cadastrar item: {error_msg}', 'error')
            return render_template('etiqueta/item_form.html')
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                return_db_connection_mega(connection)
    
    return render_template('etiqueta/item_form.html')

@etiqueta_home_bp.route('/itens/<int:item_id>/editar', methods=['GET', 'POST'])
#@permissao_necessaria('etiqueta_itens', 'editar')
def editar_item(item_id):
    """Edita um item existente"""
    configure_etiqueta()
    
    if request.method == 'POST':
        try:
            # Para edição, só permitir alterar campos específicos
            peso = request.form.get('peso', '').strip()
            validade = request.form.get('validade', '').strip()
            cnpj = request.form.get('cnpj', '').strip().replace('.', '').replace('-', '').replace('/', '')
            
            # Buscar dados atuais do item (não alteráveis)
            connection = get_db_connection_mega()
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT proe_in_numero, proe_descricao, proe_dun
                FROM barbarex.pro_etiqueta
                WHERE proe_id = :item_id
            """, {'item_id': item_id})
            
            row = cursor.fetchone()
            if not row:
                flash('Item não encontrado', 'error')
                return redirect(url_for('etiqueta_home_bp.listar_itens'))
            
            # Usar dados existentes para campos não editáveis
            numero = row[0]
            descricao = row[1]
            dun = row[2]
            
            # Atualizar apenas campos editáveis
            sql = """
                UPDATE barbarex.pro_etiqueta 
                SET proe_peso = :peso,
                    proe_validade = :validade,
                    proe_cnpj = :cnpj,
                    dt_atualizacao = SYSDATE
                WHERE proe_id = :item_id
            """
            
            params = {
                'peso': float(peso) if peso else None,
                'validade': validade if validade else None,
                'cnpj': cnpj if cnpj else None,
                'item_id': item_id
            }
            
            cursor.execute(sql, params)
            connection.commit()
            
            flash('Item atualizado com sucesso!', 'success')
            return redirect(url_for('etiqueta_home_bp.listar_itens'))
            
        except Exception as e:
            print(f"Erro ao atualizar item: {e}")
            flash(f'Erro ao atualizar item: {str(e)}', 'error')
            return redirect(url_for('etiqueta_home_bp.editar_item', item_id=item_id))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                return_db_connection_mega(connection)
    
    # GET - Carregar dados do item
    try:
        connection = get_db_connection_mega()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT proe_id, proe_in_numero, proe_descricao, proe_peso, proe_validade, 
                   proe_cnpj, proe_dun
            FROM barbarex.pro_etiqueta
            WHERE proe_id = :item_id
        """, {'item_id': item_id})
        
        row = cursor.fetchone()
        if not row:
            flash('Item não encontrado', 'error')
            return redirect(url_for('etiqueta_home_bp.listar_itens'))
        
        item = {
            'id': row[0],
            'numero': row[1],
            'descricao': row[2],
            'peso': row[3],
            'validade': row[4] if row[4] else '',
            'cnpj': row[5],
            'dun': row[6]
        }
        
        return render_template('etiqueta/item_form.html', item=item)
        
    except Exception as e:
        print(f"Erro ao carregar item: {e}")
        flash(f'Erro ao carregar item: {str(e)}', 'error')
        return redirect(url_for('etiqueta_home_bp.listar_itens'))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            return_db_connection_mega(connection)

@etiqueta_home_bp.route('/itens/<int:item_id>/deletar', methods=['POST'])
#@permissao_necessaria('etiqueta_itens', 'excluir')
def deletar_item(item_id):
    """Deleta um item"""
    try:
        connection = get_db_connection_mega()
        cursor = connection.cursor()
        
        cursor.execute("""
            DELETE FROM barbarex.pro_etiqueta
            WHERE proe_id = :item_id
        """, {'item_id': item_id})
        
        connection.commit()
        
        flash('Item deletado com sucesso!', 'success')
        
    except Exception as e:
        print(f"Erro ao deletar item: {e}")
        flash(f'Erro ao deletar item: {str(e)}', 'error')
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            return_db_connection_mega(connection)
    
    return redirect(url_for('etiqueta_home_bp.listar_itens'))

@etiqueta_home_bp.route('/api/produto/<int:produto_id>')
#@permissao_necessaria('etiqueta_gerar', 'visualizar')
def api_buscar_produto(produto_id):
    """API para buscar dados de um produto pelo ID"""
    try:
        connection = get_db_connection_mega()
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT proe_id, proe_in_numero, proe_descricao, proe_peso, 
                   proe_validade, proe_cnpj, proe_dun
            FROM barbarex.pro_etiqueta
            WHERE proe_in_numero = :produto_id
        """, {'produto_id': produto_id})
        
        row = cursor.fetchone()
        if not row:
            return jsonify({
                'success': False,
                'message': f'Produto com ID {produto_id} não encontrado.'
            }), 404
        
        produto = {
            'id': row[0],
            'numero': row[1],
            'descricao': row[2],
            'peso': row[3],
            'validade': row[4] if row[4] else None,
            'cnpj': row[5],
            'dun': row[6]
        }
        
        return jsonify({
            'success': True,
            'produto': produto
        })
        
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        return jsonify({
            'success': False,
            'message': f'Erro interno: {str(e)}'
        }), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            return_db_connection_mega(connection)