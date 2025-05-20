
from flask import Flask, render_template, request, redirect
import pandas as pd
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.csv'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(f'/dashboard?file={filename}')
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    filename = request.args.get('file')
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(filepath)

    df['Email'] = df['Email'].str.lower()
    paid = df[df['Status'] == 'paid']
    abandoned = df[df['Status'] != 'paid']

    real_emails = paid['Email'].unique()
    filtered_abandoned = abandoned[~abandoned['Email'].isin(real_emails)]

    total_faturado = paid['Valor da compra em moeda da conta'].sum()
    lucro_estimado = total_faturado * 0.90

    criativos = paid['Tracking sck'].value_counts().to_dict()
    origens = paid['Tracking utm_source'].value_counts().to_dict()

    return render_template(
        'dashboard.html',
        faturamento=round(total_faturado, 2),
        lucro=round(lucro_estimado, 2),
        criativos=criativos,
        origens=origens,
        oportunidades=len(filtered_abandoned),
        vendas=len(paid)
    )

if __name__ == '__main__':
    app.run(debug=True)
