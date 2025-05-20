
from flask import Flask, render_template, request, redirect
import pandas as pd
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def process_csv(filepath):
    df = pd.read_csv(filepath)
    df['Email'] = df['Email'].str.lower()
    vendas = df[df['Status'] == 'paid']
    abandonos = df[df['Status'] != 'paid']
    emails_convertidos = vendas['Email'].unique()
    oportunidades = abandonos[~abandonos['Email'].isin(emails_convertidos)]

    total_faturado = vendas['Valor da compra em moeda da conta'].sum()
    total_liquido = vendas['Valor líquido'].sum() if 'Valor líquido' in vendas else total_faturado * 0.9

    por_pagamento = vendas['Pagamento'].value_counts().to_dict()
    por_criativo = vendas['Tracking sck'].value_counts().to_dict()
    por_origem = vendas['Tracking utm_source'].value_counts().to_dict()
    por_produto = vendas['Produto'].value_counts().to_dict()

    tentativas = df['Pagamento'].value_counts()
    aprovados = vendas['Pagamento'].value_counts()
    taxa_aprovacao = {}
    for metodo in tentativas.index:
        total = tentativas[metodo]
        ok = aprovados.get(metodo, 0)
        taxa_aprovacao[metodo] = round((ok / total) * 100, 1) if total > 0 else 0

    return {
        "faturamento": round(total_faturado, 2),
        "lucro": round(total_liquido, 2),
        "vendas": len(vendas),
        "oportunidades": len(oportunidades),
        "por_pagamento": por_pagamento,
        "por_criativo": por_criativo,
        "por_origem": por_origem,
        "por_produto": por_produto,
        "taxa_aprovacao": taxa_aprovacao
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            return redirect(f'/dashboard?file={file.filename}')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    file = request.args.get('file')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file)
    data = process_csv(filepath)
    return render_template('dashboard.html', **data)

if __name__ == '__main__':
    app.run(debug=True)
