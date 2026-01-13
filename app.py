from flask import Flask, redirect, url_for
import os

# Criar aplicacao Flask
app = Flask(__name__,
            template_folder='lib/frontend/templates',
            static_folder='lib/frontend/static')

# Chave secreta para sessoes
app.secret_key = 'etiqueta-sistema-2025-chave-secreta'

# Registrar blueprints
from lib.backend.routes.etiqueta import etiqueta_bp
app.register_blueprint(etiqueta_bp)


# Rota raiz redireciona para home
@app.route('/')
def index():
    return redirect(url_for('etiqueta.home'))


if __name__ == '__main__':
    print("=" * 50)
    print("Sistema de Etiquetas")
    print("=" * 50)
    print("Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
