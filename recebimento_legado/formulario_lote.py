from flask import render_template, request, jsonify, send_file
from db import get_db_connection_mega, return_db_connection_mega
from lib.app.decorators.perm_sidebar import configure_compras
from . import compras_bp
import cx_Oracle
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import mm
import io
from datetime import datetime
import qrcode
from PIL import Image
import random
import string

logger = logging.getLogger(__name__)

@compras_bp.route('/formulario-lote')
def formulario_lote():
    """Página do formulário de lote/laudo"""
    try:
        configure_compras()
        return render_template('compras/formulario_lote/formulario_lote.html')
    except Exception as e:
        logger.error(f"Erro na página de formulário de lote: {str(e)}")
        return jsonify({'error': str(e)}), 500

@compras_bp.route('/api/formulario-lote/salvar', methods=['POST'])
def api_formulario_lote_salvar():
    """API para salvar dados do formulário de lote/laudo"""
    conn = None
    cursor = None
    try:
        dados = request.json
        
        numero_lote = dados.get('numero_lote', '').strip()
        data_recebimento = dados.get('data_recebimento', '').strip()
        data_fabricacao = dados.get('data_fabricacao', '').strip()
        data_validade = dados.get('data_validade', '').strip()
        quantidade = dados.get('quantidade', '').strip()
        observacao = dados.get('observacao', '').strip()
        numero_nota_fiscal = dados.get('numero_nota_fiscal', '').strip()
        
        logger.info(f"Dados recebidos:")
        logger.info(f"  numero_lote: '{numero_lote}'")
        logger.info(f"  data_recebimento: '{data_recebimento}'")
        logger.info(f"  data_fabricacao: '{data_fabricacao}'")
        logger.info(f"  data_validade: '{data_validade}'")
        logger.info(f"  quantidade: '{quantidade}'")
        logger.info(f"  observacao: '{observacao}'")
        logger.info(f"  numero_nota_fiscal: '{numero_nota_fiscal}'")
        
        if not numero_lote:
            return jsonify({'error': 'Número do lote é obrigatório'}), 400
        
        if not data_recebimento:
            return jsonify({'error': 'Data de recebimento é obrigatória'}), 400
        
        conn = get_db_connection_mega()
        cursor = conn.cursor()
        
        # Inserir na tabela
        insert_sql = """
            INSERT INTO BARBAREX.CONTROLE_LOTES (
                NUMERO_LOTE,
                DATA_RECEBIMENTO,
                DATA_FABRICACAO,
                DATA_VALIDADE,
                QUANTIDADE,
                OBSERVACAO,
                NUMERO_NOTA_FISCAL
            ) VALUES (
                :numero_lote,
                TO_DATE(:data_recebimento, 'DD/MM/YYYY'),
                CASE WHEN :data_fabricacao IS NOT NULL THEN TO_DATE(:data_fabricacao, 'DD/MM/YYYY') ELSE NULL END,
                CASE WHEN :data_validade IS NOT NULL THEN TO_DATE(:data_validade, 'DD/MM/YYYY') ELSE NULL END,
                :quantidade,
                :observacao,
                :numero_nota_fiscal
            )
        """
        
        # Tratar quantidade
        quantidade_valor = None
        if quantidade and quantidade.strip():
            try:
                quantidade_valor = float(quantidade.strip())
            except ValueError:
                return jsonify({'error': 'Quantidade deve ser um número válido'}), 400
        
        params = {
            'numero_lote': numero_lote,
            'data_recebimento': data_recebimento,
            'data_fabricacao': data_fabricacao if data_fabricacao else None,
            'data_validade': data_validade if data_validade else None,
            'quantidade': quantidade_valor,
            'observacao': observacao if observacao else None,
            'numero_nota_fiscal': numero_nota_fiscal if numero_nota_fiscal else None
        }
        
        logger.info(f"Parâmetros para inserção:")
        logger.info(f"  quantidade_valor processada: {quantidade_valor} (tipo: {type(quantidade_valor)})")
        logger.info(f"  params: {params}")
        
        cursor.execute(insert_sql, params)
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lote/laudo salvo com sucesso!'
        })
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logger.error(f"Erro no banco de dados: {str(error)}")
        if conn:
            conn.rollback()
        return jsonify({'error': f'Erro no banco: {str(error)}'}), 500
    except Exception as e:
        logger.error(f"Erro ao salvar lote: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection_mega(conn)

@compras_bp.route('/api/formulario-lote/consultar')
def api_formulario_lote_consultar():
    """API para consultar lotes salvos"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection_mega()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                ID,
                NUMERO_LOTE,
                TO_CHAR(DATA_RECEBIMENTO, 'DD/MM/YYYY') AS DATA_RECEBIMENTO,
                TO_CHAR(DATA_FABRICACAO, 'DD/MM/YYYY') AS DATA_FABRICACAO,
                TO_CHAR(DATA_VALIDADE, 'DD/MM/YYYY') AS DATA_VALIDADE,
                QUANTIDADE,
                OBSERVACAO,
                NUMERO_NOTA_FISCAL,
                TO_CHAR(DATA_CADASTRO, 'DD/MM/YYYY HH24:MI:SS') AS DATA_CADASTRO
            FROM BARBAREX.CONTROLE_LOTES
            ORDER BY DATA_CADASTRO DESC
        """
        
        cursor.execute(query)
        
        dados = []
        for row in cursor:
            dados.append({
                'id': int(row[0]) if row[0] else 0,
                'numero_lote': str(row[1]) if row[1] else '',
                'data_recebimento': str(row[2]) if row[2] else '',
                'data_fabricacao': str(row[3]) if row[3] else '',
                'data_validade': str(row[4]) if row[4] else '',
                'quantidade': float(row[5]) if row[5] else 0,
                'observacao': str(row[6]) if row[6] else '',
                'numero_nota_fiscal': str(row[7]) if row[7] else '',
                'data_cadastro': str(row[8]) if row[8] else ''
            })
        
        return jsonify({
            'dados': dados,
            'total_registros': len(dados)
        })
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logger.error(f"Erro no banco de dados: {str(error)}")
        return jsonify({'error': f'Erro no banco: {str(error)}'}), 500
    except Exception as e:
        logger.error(f"Erro ao consultar lotes: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection_mega(conn)

@compras_bp.route('/api/formulario-lote/gerar-etiqueta', methods=['POST'])
def api_formulario_lote_gerar_etiqueta():
    """API para gerar etiqueta em PDF"""
    try:
        dados = request.json
        
        logger.info(f"Gerando etiqueta com dados: {dados}")
        
        # Configurações da etiqueta
        largura_mm = float(dados.get('largura', 100))
        altura_mm = float(dados.get('altura', 75))
        tamanho_fonte_base = int(dados.get('tamanho_fonte', 8))
        
        # Converter mm para pontos (1mm = 2.834645669 pontos)
        largura = largura_mm * mm
        altura = altura_mm * mm
        
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Criar o canvas PDF
        c = canvas.Canvas(buffer, pagesize=(largura, altura))
        
        # === LAYOUT MELHORADO DA ETIQUETA ===
        
        # === SISTEMA ADAPTATIVO COMPLETO ===
        if largura <= 60 * mm or altura <= 50 * mm:
            # ETIQUETAS PEQUENAS (50x40mm, etc.)
            x_margin = 1.5 * mm
            y_margin = 1.5 * mm
            tamanho_fonte = max(4, tamanho_fonte_base - 2)  # Fonte menor
            titulo_fonte = tamanho_fonte + 1  # Título apenas 1pt maior
            lote_fonte = tamanho_fonte + 1    # Lote igual ao título
            rodape_fonte = tamanho_fonte - 1  # Rodapé menor
            line_height = tamanho_fonte * 1.0  # Bem próximo
            section_space = line_height * 0.2  # Mínimo espaço
        elif largura <= 90 * mm or altura <= 70 * mm:
            # ETIQUETAS MÉDIAS (70x50mm, 80x60mm, etc.)
            x_margin = 2 * mm
            y_margin = 2 * mm
            tamanho_fonte = max(5, tamanho_fonte_base - 1)  # Fonte um pouco menor
            titulo_fonte = tamanho_fonte + 2  # Título 2pts maior
            lote_fonte = tamanho_fonte + 2    # Lote igual ao título
            rodape_fonte = tamanho_fonte - 1  # Rodapé menor
            line_height = tamanho_fonte * 1.05
            section_space = line_height * 0.3
        else:
            # ETIQUETAS GRANDES (100x75mm+)
            x_margin = 3 * mm
            y_margin = 3 * mm
            tamanho_fonte = tamanho_fonte_base  # Fonte original
            titulo_fonte = tamanho_fonte + 3    # Título bem maior
            lote_fonte = tamanho_fonte + 2      # Lote destacado
            rodape_fonte = tamanho_fonte - 2    # Rodapé bem menor
            line_height = tamanho_fonte * 1.1
            section_space = line_height * 0.4
        
        # Área útil (descontando margens)
        area_util_largura = largura - (2 * x_margin)
        area_util_altura = altura - (2 * y_margin)
        y_start = altura - y_margin - (titulo_fonte + 2)
        
        # Gerar código para QR Code (lote + valores aleatórios)
        numero_lote = dados.get('numero_lote', '').strip()
        valores_aleatorios = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # QR Code suporta letras, números e símbolos - sem problemas
        if numero_lote:
            # Remove espaços e caracteres problemáticos se houver
            lote_limpo = numero_lote.replace(' ', '_').replace('\n', '').replace('\r', '')
            codigo_qr = f"{lote_limpo}-{valores_aleatorios}"
        else:
            codigo_qr = f"LOTE_VAZIO-{valores_aleatorios}"
        
        logger.info(f"Código QR gerado: {codigo_qr}")
        
        # Gerar QR Code com qualidade melhorada
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Melhor correção de erro
            box_size=4,  # Maior resolução
            border=2,    # Borda mais visível
        )
        qr.add_data(codigo_qr)
        qr.make(fit=True)
        
        # Criar imagem do QR Code
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # === ÁREA DE TEXTO (largura total) ===
        texto_largura = area_util_largura  # Agora usa toda a largura
        y = y_start
        
        # TÍTULO PRINCIPAL - CENTRALIZADO
        c.setFont("Helvetica-Bold", titulo_fonte)
        titulo = "CONTROLE DE LOTE"
        titulo_largura = c.stringWidth(titulo, "Helvetica-Bold", titulo_fonte)
        titulo_x = (largura - titulo_largura) / 2
        c.drawString(titulo_x, y, titulo)
        y -= titulo_fonte * 1.0  # Espaçamento proporcional
        
        # Importar colors para usar depois
        from reportlab.lib import colors
        
        # NÚMERO DO LOTE - CENTRALIZADO (destaque máximo)
        if numero_lote:
            c.setFont("Helvetica-Bold", lote_fonte)
            lote_texto = f"LOTE: {numero_lote}"
            lote_largura = c.stringWidth(lote_texto, "Helvetica-Bold", lote_fonte)
            lote_x = (largura - lote_largura) / 2
            c.drawString(lote_x, y, lote_texto)
            y -= line_height * 1.0  # Mais próximo
        
        # INFORMAÇÕES PRINCIPAIS - CENTRALIZADAS
        c.setFont("Helvetica", tamanho_fonte)
        
        # Datas organizadas
        data_recebimento = dados.get('data_recebimento', '')
        data_fabricacao = dados.get('data_fabricacao', '')
        data_validade = dados.get('data_validade', '')
        
        if data_recebimento:
            rec_texto = f"Recebimento: {data_recebimento}"
            rec_largura = c.stringWidth(rec_texto, "Helvetica", tamanho_fonte)
            rec_x = (largura - rec_largura) / 2
            c.drawString(rec_x, y, rec_texto)
            y -= line_height
        
        if data_fabricacao:
            fab_texto = f"Fabricação: {data_fabricacao}"
            fab_largura = c.stringWidth(fab_texto, "Helvetica", tamanho_fonte)
            fab_x = (largura - fab_largura) / 2
            c.drawString(fab_x, y, fab_texto)
            y -= line_height
        
        if data_validade:
            c.setFont("Helvetica-Bold", tamanho_fonte)
            val_texto = f"Validade: {data_validade}"
            val_largura = c.stringWidth(val_texto, "Helvetica-Bold", tamanho_fonte)
            val_x = (largura - val_largura) / 2
            c.drawString(val_x, y, val_texto)
            c.setFont("Helvetica", tamanho_fonte)
            y -= line_height
        
        # Nota Fiscal - CENTRALIZADA
        numero_nota_fiscal = dados.get('numero_nota_fiscal', '')
        
        if numero_nota_fiscal:
            nf_texto = f"Nota Fiscal: {numero_nota_fiscal}"
            nf_largura = c.stringWidth(nf_texto, "Helvetica", tamanho_fonte)
            nf_x = (largura - nf_largura) / 2
            c.drawString(nf_x, y, nf_texto)
            y -= line_height
        
        # Observação - CENTRALIZADA (se houver espaço)
        observacao = dados.get('observacao', '')
        if observacao and len(observacao) > 0 and y > (y_margin + line_height * 3):
            y -= section_space * 0.5
            obs_fonte = max(3, tamanho_fonte - 1)  # Fonte da observação
            c.setFont("Helvetica", obs_fonte)
            
            # Calcular quantos caracteres cabem
            obs_max = max(30, int(texto_largura / (obs_fonte * 0.5)))
            obs_texto = observacao[:obs_max] + "..." if len(observacao) > obs_max else observacao
            obs_completo = f"Obs: {obs_texto}"
            
            obs_largura = c.stringWidth(obs_completo, "Helvetica", obs_fonte)
            obs_x = (largura - obs_largura) / 2
            c.drawString(obs_x, y, obs_completo)
            y -= line_height * 1.2
        
        # === ÁREA ESPECÍFICA PARA QR CODE ===
        # Definir área fixa para QR code (entre conteúdo e rodapé)
        rodape_altura = rodape_fonte + (2 * y_margin)  # Altura do rodapé
        area_qr_inicio = y_margin + rodape_altura + (3 * mm)   # Início da área QR
        area_qr_fim = y - (2 * mm)                             # Fim da área QR (abaixo do conteúdo)
        area_qr_altura = area_qr_fim - area_qr_inicio          # Altura disponível para QR
        
        # Calcular tamanho proporcional à etiqueta - AJUSTADO PARA ETIQUETAS PEQUENAS
        if largura <= 60 * mm or altura <= 50 * mm:
            # Etiquetas pequenas (50x40mm, etc.) - QR code menor
            qr_size_largura = largura * 0.25  # 25% da largura
            qr_size_altura = area_qr_altura * 0.60  # 60% da área disponível
        elif largura <= 90 * mm or altura <= 70 * mm:
            # Etiquetas médias - QR code moderado
            qr_size_largura = largura * 0.30  # 30% da largura
            qr_size_altura = area_qr_altura * 0.70  # 70% da área disponível
        else:
            # Etiquetas grandes - QR code padrão
            qr_size_largura = largura * 0.35  # 35% da largura
            qr_size_altura = area_qr_altura * 0.85  # 85% da área disponível
        
        # Usar o menor para manter proporção
        qr_size = min(qr_size_largura, qr_size_altura)
        
        # Limites ajustados para diferentes tamanhos
        if largura <= 60 * mm or altura <= 50 * mm:
            # Etiquetas pequenas: QR code entre 8-18mm
            qr_size = max(8 * mm, min(qr_size, 18 * mm))
        elif largura <= 90 * mm or altura <= 70 * mm:
            # Etiquetas médias: QR code entre 10-25mm
            qr_size = max(10 * mm, min(qr_size, 25 * mm))
        else:
            # Etiquetas grandes: QR code entre 12-40mm
            qr_size = max(12 * mm, min(qr_size, 40 * mm))
        
        # Posicionar centralizado na área definida
        qr_x = (largura - qr_size) / 2  # Centro horizontal
        qr_y = area_qr_inicio + ((area_qr_altura - qr_size) / 2)  # Centro vertical da área
        
        # Área de debug removida - QR code posicionado corretamente
        
        # Desenhar QR Code na área definida
        c.drawInlineImage(qr_img, qr_x, qr_y, qr_size, qr_size)
        
        # === RODAPÉ COMPACTO E CENTRALIZADO ===
        from datetime import timedelta
        
        # Horário de Brasília
        agora_brasilia = datetime.now() - timedelta(hours=3)
        data_geracao = agora_brasilia.strftime('%d/%m/%Y %H:%M')
        
        # Posição do rodapé
        rodape_y = y_margin + rodape_fonte
        
        # Texto do rodapé junto e centralizado
        c.setFont("Helvetica", rodape_fonte)
        rodape_texto = f"QR: {codigo_qr}  •  Gerado: {data_geracao}"
        rodape_largura = c.stringWidth(rodape_texto, "Helvetica", rodape_fonte)
        rodape_x = (largura - rodape_largura) / 2
        c.drawString(rodape_x, rodape_y, rodape_texto)
        
        logger.info(f"Horário UTC: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        logger.info(f"Horário Brasília: {data_geracao}")
        
        # Borda removida - layout limpo sem bordas
        
        # Finalizar o PDF
        c.save()
        
        # Preparar arquivo para envio
        buffer.seek(0)
        
        nome_arquivo = f'etiqueta_{numero_lote or "sem_lote"}_{agora_brasilia.strftime("%Y%m%d_%H%M%S")}.pdf'
        
        logger.info(f"Etiqueta gerada: {nome_arquivo}")
        
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nome_arquivo
        )
        
    except Exception as e:
        logger.error(f"Erro ao gerar etiqueta: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@compras_bp.route('/api/formulario-lote/buscar/<int:lote_id>')
def api_formulario_lote_buscar(lote_id):
    """API para buscar dados de um lote específico"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection_mega()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                ID,
                NUMERO_LOTE,
                TO_CHAR(DATA_RECEBIMENTO, 'YYYY-MM-DD') AS DATA_RECEBIMENTO,
                TO_CHAR(DATA_FABRICACAO, 'YYYY-MM-DD') AS DATA_FABRICACAO,
                TO_CHAR(DATA_VALIDADE, 'YYYY-MM-DD') AS DATA_VALIDADE,
                QUANTIDADE,
                OBSERVACAO,
                NUMERO_NOTA_FISCAL
            FROM BARBAREX.CONTROLE_LOTES
            WHERE ID = :lote_id
        """
        
        cursor.execute(query, {'lote_id': lote_id})
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Lote não encontrado'}), 404
        
        dados_lote = {
            'id': int(row[0]),
            'numero_lote': str(row[1]) if row[1] else '',
            'data_recebimento': str(row[2]) if row[2] else '',
            'data_fabricacao': str(row[3]) if row[3] else '',
            'data_validade': str(row[4]) if row[4] else '',
            'quantidade': str(row[5]) if row[5] else '',
            'observacao': str(row[6]) if row[6] else '',
            'numero_nota_fiscal': str(row[7]) if row[7] else ''
        }
        
        return jsonify(dados_lote)
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logger.error(f"Erro no banco de dados: {str(error)}")
        return jsonify({'error': f'Erro no banco: {str(error)}'}), 500
    except Exception as e:
        logger.error(f"Erro ao buscar lote: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection_mega(conn)

@compras_bp.route('/api/formulario-lote/atualizar/<int:lote_id>', methods=['PUT'])
def api_formulario_lote_atualizar(lote_id):
    """API para atualizar dados de um lote existente"""
    conn = None
    cursor = None
    try:
        dados = request.json
        
        numero_lote = dados.get('numero_lote', '').strip()
        data_recebimento = dados.get('data_recebimento', '').strip()
        data_fabricacao = dados.get('data_fabricacao', '').strip()
        data_validade = dados.get('data_validade', '').strip()
        quantidade = dados.get('quantidade', '').strip()
        observacao = dados.get('observacao', '').strip()
        numero_nota_fiscal = dados.get('numero_nota_fiscal', '').strip()
        
        logger.info(f"Atualizando lote ID {lote_id}:")
        logger.info(f"  numero_lote: '{numero_lote}'")
        
        if not numero_lote:
            return jsonify({'error': 'Número do lote é obrigatório'}), 400
        
        if not data_recebimento:
            return jsonify({'error': 'Data de recebimento é obrigatória'}), 400
        
        conn = get_db_connection_mega()
        cursor = conn.cursor()
        
        # Verificar se o lote existe
        cursor.execute("SELECT ID FROM BARBAREX.CONTROLE_LOTES WHERE ID = :lote_id", {'lote_id': lote_id})
        if not cursor.fetchone():
            return jsonify({'error': 'Lote não encontrado'}), 404
        
        # Tratar quantidade
        quantidade_valor = None
        if quantidade and quantidade.strip():
            try:
                quantidade_valor = float(quantidade.strip())
            except ValueError:
                return jsonify({'error': 'Quantidade deve ser um número válido'}), 400
        
        # Query de atualização
        update_sql = """
            UPDATE BARBAREX.CONTROLE_LOTES SET
                NUMERO_LOTE = :numero_lote,
                DATA_RECEBIMENTO = TO_DATE(:data_recebimento, 'DD/MM/YYYY'),
                DATA_FABRICACAO = CASE WHEN :data_fabricacao IS NOT NULL THEN TO_DATE(:data_fabricacao, 'DD/MM/YYYY') ELSE NULL END,
                DATA_VALIDADE = CASE WHEN :data_validade IS NOT NULL THEN TO_DATE(:data_validade, 'DD/MM/YYYY') ELSE NULL END,
                QUANTIDADE = :quantidade,
                OBSERVACAO = :observacao,
                NUMERO_NOTA_FISCAL = :numero_nota_fiscal
            WHERE ID = :lote_id
        """
        
        params = {
            'lote_id': lote_id,
            'numero_lote': numero_lote,
            'data_recebimento': data_recebimento,
            'data_fabricacao': data_fabricacao if data_fabricacao else None,
            'data_validade': data_validade if data_validade else None,
            'quantidade': quantidade_valor,
            'observacao': observacao if observacao else None,
            'numero_nota_fiscal': numero_nota_fiscal if numero_nota_fiscal else None
        }
        
        cursor.execute(update_sql, params)
        conn.commit()
        
        logger.info(f"Lote {lote_id} atualizado com sucesso!")
        
        return jsonify({
            'success': True,
            'message': 'Lote atualizado com sucesso!',
            'lote_id': lote_id
        })
        
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        logger.error(f"Erro no banco de dados: {str(error)}")
        if conn:
            conn.rollback()
        return jsonify({'error': f'Erro no banco: {str(error)}'}), 500
    except Exception as e:
        logger.error(f"Erro ao atualizar lote: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            return_db_connection_mega(conn)