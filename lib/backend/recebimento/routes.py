# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, request, jsonify, send_file
from datetime import datetime
import io
import qrcode
from PIL import Image
import random
import string

from lib.backend.recebimento.service import (
    listar_lotes,
    buscar_lote_por_id,
    criar_lote,
    atualizar_lote,
    deletar_lote
)

recebimento_bp = Blueprint('recebimento', __name__, url_prefix='/recebimento')


# ========== PAGINAS PRINCIPAIS ==========

@recebimento_bp.route('/')
@recebimento_bp.route('/home')
def home():
    """Pagina inicial do modulo Recebimento"""
    return render_template('recebimento/home.html')


@recebimento_bp.route('/formulario')
def formulario_lote():
    """Pagina do formulario de lote"""
    return render_template('recebimento/formulario.html')


# ========== APIs ==========

@recebimento_bp.route('/api/lotes')
def api_listar_lotes():
    """API para listar todos os lotes"""
    try:
        lotes = listar_lotes()
        return jsonify({
            'dados': lotes,
            'total_registros': len(lotes)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recebimento_bp.route('/api/lotes/<int:lote_id>')
def api_buscar_lote(lote_id):
    """API para buscar lote pelo ID"""
    try:
        lote = buscar_lote_por_id(lote_id)
        if not lote:
            return jsonify({'error': 'Lote nao encontrado'}), 404
        return jsonify(lote)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recebimento_bp.route('/api/lotes', methods=['POST'])
def api_criar_lote():
    """API para criar novo lote"""
    try:
        dados = request.json

        numero_lote = dados.get('numero_lote', '').strip()
        data_recebimento = dados.get('data_recebimento', '').strip()

        if not numero_lote:
            return jsonify({'error': 'Numero do lote e obrigatorio'}), 400

        # Tratar quantidade
        quantidade = dados.get('quantidade', '').strip()
        quantidade_valor = None
        if quantidade:
            try:
                quantidade_valor = float(quantidade)
            except ValueError:
                return jsonify({'error': 'Quantidade deve ser um numero valido'}), 400

        lote, erro = criar_lote(
            numero_lote=numero_lote,
            id_item=dados.get('id_item', '').strip() or None,
            data_recebimento=data_recebimento or None,
            data_fabricacao=dados.get('data_fabricacao', '').strip() or None,
            data_validade=dados.get('data_validade', '').strip() or None,
            quantidade=quantidade_valor,
            numero_nota_fiscal=dados.get('numero_nota_fiscal', '').strip() or None,
            observacao=dados.get('observacao', '').strip() or None
        )

        if erro:
            return jsonify({'error': erro}), 400

        return jsonify({
            'success': True,
            'message': 'Lote salvo com sucesso!',
            'lote': lote
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recebimento_bp.route('/api/lotes/<int:lote_id>', methods=['PUT'])
def api_atualizar_lote(lote_id):
    """API para atualizar lote existente"""
    try:
        dados = request.json

        numero_lote = dados.get('numero_lote', '').strip()
        data_recebimento = dados.get('data_recebimento', '').strip()

        if not numero_lote:
            return jsonify({'error': 'Numero do lote e obrigatorio'}), 400

        # Tratar quantidade
        quantidade = dados.get('quantidade', '').strip()
        quantidade_valor = None
        if quantidade:
            try:
                quantidade_valor = float(quantidade)
            except ValueError:
                return jsonify({'error': 'Quantidade deve ser um numero valido'}), 400

        lote, erro = atualizar_lote(
            lote_id=lote_id,
            numero_lote=numero_lote,
            id_item=dados.get('id_item', '').strip() or None,
            data_recebimento=data_recebimento or None,
            data_fabricacao=dados.get('data_fabricacao', '').strip() or None,
            data_validade=dados.get('data_validade', '').strip() or None,
            quantidade=quantidade_valor,
            numero_nota_fiscal=dados.get('numero_nota_fiscal', '').strip() or None,
            observacao=dados.get('observacao', '').strip() or None
        )

        if erro:
            return jsonify({'error': erro}), 400

        return jsonify({
            'success': True,
            'message': 'Lote atualizado com sucesso!',
            'lote': lote
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recebimento_bp.route('/api/lotes/<int:lote_id>', methods=['DELETE'])
def api_deletar_lote(lote_id):
    """API para deletar lote - BLOQUEADO"""
    return jsonify({'error': 'Exclusao de lotes esta desabilitada'}), 403


@recebimento_bp.route('/api/gerar-etiqueta', methods=['POST'])
def api_gerar_etiqueta():
    """API para gerar etiqueta em PDF com QR Code"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import mm
        from datetime import timedelta

        dados = request.json

        # Configuracoes da etiqueta
        largura_mm = float(dados.get('largura', 100))
        altura_mm = float(dados.get('altura', 75))
        tamanho_fonte_base = int(dados.get('tamanho_fonte', 8))
        quantidade_etiquetas = int(dados.get('quantidade_etiquetas', 1))
        quantidade_etiquetas = max(1, quantidade_etiquetas)

        # Converter mm para pontos
        largura = largura_mm * mm
        altura = altura_mm * mm

        # Criar buffer para o PDF
        buffer = io.BytesIO()

        # Criar o canvas PDF
        c = canvas.Canvas(buffer, pagesize=(largura, altura))

        # Sistema adaptativo de fonte
        if largura <= 60 * mm or altura <= 50 * mm:
            x_margin = 1.5 * mm
            y_margin = 1.5 * mm
            tamanho_fonte = max(4, tamanho_fonte_base - 2)
            titulo_fonte = tamanho_fonte + 1
            lote_fonte = tamanho_fonte + 1
            rodape_fonte = tamanho_fonte - 1
            line_height = tamanho_fonte * 1.0
            section_space = line_height * 0.2
        elif largura <= 90 * mm or altura <= 70 * mm:
            x_margin = 2 * mm
            y_margin = 2 * mm
            tamanho_fonte = max(5, tamanho_fonte_base - 1)
            titulo_fonte = tamanho_fonte + 2
            lote_fonte = tamanho_fonte + 2
            rodape_fonte = tamanho_fonte - 1
            line_height = tamanho_fonte * 1.05
            section_space = line_height * 0.3
        else:
            x_margin = 3 * mm
            y_margin = 3 * mm
            tamanho_fonte = tamanho_fonte_base
            titulo_fonte = tamanho_fonte + 3
            lote_fonte = tamanho_fonte + 2
            rodape_fonte = tamanho_fonte - 2
            line_height = tamanho_fonte * 1.1
            section_space = line_height * 0.4

        area_util_largura = largura - (2 * x_margin)
        area_util_altura = altura - (2 * y_margin)
        y_start = altura - y_margin - (titulo_fonte + 2)

        # Gerar codigo para QR Code - somente ID do Item
        numero_lote = dados.get('numero_lote', '').strip()
        id_item_qr = dados.get('id_item', '').strip()

        # QR Code contem apenas o ID do Item
        codigo_qr = id_item_qr if id_item_qr else 'SEM_ID'
        # Garantir que e ASCII puro
        codigo_qr = codigo_qr.encode('ascii', 'replace').decode('ascii')

        # Gerar QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=4,
            border=2,
        )
        qr.add_data(codigo_qr)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")

        # Loop para gerar multiplas etiquetas
        for etiqueta_num in range(quantidade_etiquetas):
            texto_largura = area_util_largura
            y = y_start

            # TITULO PRINCIPAL
            c.setFont("Helvetica-Bold", titulo_fonte)
            titulo = "CONTROLE DE LOTE"
            titulo_largura = c.stringWidth(titulo, "Helvetica-Bold", titulo_fonte)
            titulo_x = (largura - titulo_largura) / 2
            c.drawString(titulo_x, y, titulo)
            y -= titulo_fonte * 1.0

            # NUMERO DO LOTE
            if numero_lote:
                c.setFont("Helvetica-Bold", lote_fonte)
                lote_texto = f"LOTE: {numero_lote}"
                lote_largura = c.stringWidth(lote_texto, "Helvetica-Bold", lote_fonte)
                lote_x = (largura - lote_largura) / 2
                c.drawString(lote_x, y, lote_texto)
                y -= line_height * 1.0

            # ID DO ITEM
            id_item = dados.get('id_item', '')
            if id_item:
                c.setFont("Helvetica-Bold", tamanho_fonte)
                item_texto = f"ID Item: {id_item}"
                item_largura = c.stringWidth(item_texto, "Helvetica-Bold", tamanho_fonte)
                item_x = (largura - item_largura) / 2
                c.drawString(item_x, y, item_texto)
                y -= line_height

            # DESCRICAO DO ITEM
            descricao_item = dados.get('descricao_item', '')
            if descricao_item:
                c.setFont("Helvetica", tamanho_fonte)
                # Limitar descricao para caber na etiqueta
                desc_max = max(40, int(texto_largura / (tamanho_fonte * 0.5)))
                desc_texto = descricao_item[:desc_max] + "..." if len(descricao_item) > desc_max else descricao_item
                desc_largura = c.stringWidth(desc_texto, "Helvetica", tamanho_fonte)
                desc_x = (largura - desc_largura) / 2
                c.drawString(desc_x, y, desc_texto)
                y -= line_height

            # INFORMACOES
            c.setFont("Helvetica", tamanho_fonte)

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
                fab_texto = f"Fabricacao: {data_fabricacao}"
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

            # Nota Fiscal
            numero_nota_fiscal = dados.get('numero_nota_fiscal', '')
            if numero_nota_fiscal:
                nf_texto = f"Nota Fiscal: {numero_nota_fiscal}"
                nf_largura = c.stringWidth(nf_texto, "Helvetica", tamanho_fonte)
                nf_x = (largura - nf_largura) / 2
                c.drawString(nf_x, y, nf_texto)
                y -= line_height

            # Quantidade
            quantidade_prod = dados.get('quantidade', '')
            if quantidade_prod:
                qtd_texto = f"Quantidade: {quantidade_prod}"
                qtd_largura = c.stringWidth(qtd_texto, "Helvetica", tamanho_fonte)
                qtd_x = (largura - qtd_largura) / 2
                c.drawString(qtd_x, y, qtd_texto)
                y -= line_height

            # Observacao
            observacao = dados.get('observacao', '')
            if observacao and len(observacao) > 0 and y > (y_margin + line_height * 3):
                y -= section_space * 0.5
                obs_fonte = max(3, tamanho_fonte - 1)
                c.setFont("Helvetica", obs_fonte)
                obs_max = max(30, int(texto_largura / (obs_fonte * 0.5)))
                obs_texto = observacao[:obs_max] + "..." if len(observacao) > obs_max else observacao
                obs_completo = f"Obs: {obs_texto}"
                obs_largura = c.stringWidth(obs_completo, "Helvetica", obs_fonte)
                obs_x = (largura - obs_largura) / 2
                c.drawString(obs_x, y, obs_completo)
                y -= line_height * 1.2

            # QR CODE
            rodape_altura = rodape_fonte + (2 * y_margin)
            area_qr_inicio = y_margin + rodape_altura + (3 * mm)
            area_qr_fim = y - (2 * mm)
            area_qr_altura = area_qr_fim - area_qr_inicio

            if largura <= 60 * mm or altura <= 50 * mm:
                qr_size_largura = largura * 0.25
                qr_size_altura = area_qr_altura * 0.60
            elif largura <= 90 * mm or altura <= 70 * mm:
                qr_size_largura = largura * 0.30
                qr_size_altura = area_qr_altura * 0.70
            else:
                qr_size_largura = largura * 0.35
                qr_size_altura = area_qr_altura * 0.85

            qr_size = min(qr_size_largura, qr_size_altura)

            if largura <= 60 * mm or altura <= 50 * mm:
                qr_size = max(8 * mm, min(qr_size, 18 * mm))
            elif largura <= 90 * mm or altura <= 70 * mm:
                qr_size = max(10 * mm, min(qr_size, 25 * mm))
            else:
                qr_size = max(12 * mm, min(qr_size, 40 * mm))

            qr_x = (largura - qr_size) / 2
            qr_y = area_qr_inicio + ((area_qr_altura - qr_size) / 2)

            c.drawInlineImage(qr_img, qr_x, qr_y, qr_size, qr_size)

            # RODAPE
            agora_brasilia = datetime.now() - timedelta(hours=3)
            data_geracao = agora_brasilia.strftime('%d/%m/%Y %H:%M')

            rodape_y = y_margin + rodape_fonte

            c.setFont("Helvetica", rodape_fonte)
            rodape_texto = f"ID: {codigo_qr}  |  Gerado: {data_geracao}"
            rodape_largura = c.stringWidth(rodape_texto, "Helvetica", rodape_fonte)
            rodape_x = (largura - rodape_largura) / 2
            c.drawString(rodape_x, rodape_y, rodape_texto)

            # Criar nova pagina se nao for a ultima etiqueta
            if etiqueta_num < quantidade_etiquetas - 1:
                c.showPage()

        # Finalizar
        c.save()
        buffer.seek(0)

        nome_arquivo = f'etiqueta_{numero_lote or "sem_lote"}_{agora_brasilia.strftime("%Y%m%d_%H%M%S")}.pdf'

        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nome_arquivo
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
