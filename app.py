from flask import Flask, redirect, url_for, render_template
import os

# Criar aplicacao Flask
app = Flask(__name__,
            template_folder='lib/frontend/templates',
            static_folder='lib/frontend/static')

# Chave secreta para sessoes
app.secret_key = 'etiqueta-sistema-2025-chave-secreta'

# Registrar blueprints
from lib.backend.routes.etiqueta import etiqueta_bp
from lib.backend.routes.recebimento import recebimento_bp
from lib.backend.routes.itens import itens_bp
app.register_blueprint(etiqueta_bp)
app.register_blueprint(recebimento_bp)
app.register_blueprint(itens_bp)


# Pagina principal - escolha de modulos
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


if __name__ == '__main__':
    print("=" * 50)
    print("Sistema de Etiquetas")
    print("=" * 50)
    print("Acesse: http://localhost:8030")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=8030)
