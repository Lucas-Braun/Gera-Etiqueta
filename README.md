# Sistema de Etiquetas

Sistema web para geracao e impressao de etiquetas com codigo de barras.

## Funcionalidades

- Cadastro de produtos (armazenamento em JSON)
- Geracao de etiquetas personalizadas
- Codigo de barras DUN e Lote
- Configuracao de tamanho da etiqueta
- Impressao otimizada

## Requisitos

- Python 3.8+
- Flask
- python-barcode
- Pillow

## Instalacao

```bash
# Clonar repositorio
git clone https://github.com/Lucas-Braun/Gera-Etiqueta.git
cd Gera-Etiqueta

# Instalar dependencias
pip install -r requirements.txt

# Executar
python app.py
```

## Acesso

Abra o navegador em: http://localhost:5000

## Estrutura

```
├── app.py                     # Aplicacao principal
├── requirements.txt           # Dependencias
├── lib/
│   ├── backend/
│   │   ├── data/
│   │   │   └── produtos.json  # Dados dos produtos
│   │   ├── data_service.py    # CRUD JSON
│   │   └── routes/
│   │       └── etiqueta.py    # Rotas Flask
│   └── frontend/
│       ├── static/            # CSS e JS
│       └── templates/         # Templates HTML
```

## Uso

1. Cadastre produtos em **Produtos > Novo Produto**
2. Gere etiquetas em **Gerar Etiqueta**
3. Digite o ID do produto e clique em **Buscar**
4. Configure o tamanho da etiqueta
5. Clique em **Gerar Etiqueta**
6. Imprima com **Ctrl+P** ou botao **Imprimir**
