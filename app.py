from flask import Flask, render_template, request, jsonify, send_file
from java_cnpj_analyzer import JavaCNPJAnalyzer
from datetime import datetime
import os
from pathlib import Path
import re

app = Flask(__name__)
analyzer = JavaCNPJAnalyzer()

# Criar diretório reports se não existir
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'directory' not in request.form:
        return jsonify({'error': 'Diretório não especificado'}), 400
        
    directory = request.form['directory']
    if not os.path.exists(directory):
        return jsonify({'error': 'Diretório não encontrado'}), 404

    try:
        analyzer.scan_directory(directory)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Gerar relatórios no diretório reports
        excel_file = os.path.join(REPORTS_DIR, f'analise_cnpj_{timestamp}.xlsx')
        analyzer.export_to_excel(excel_file)
        
        return jsonify({
            'status': 'success',
            'data': analyzer.findings,
            'excel_file': os.path.basename(excel_file)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/pre-analyze', methods=['POST'])
def pre_analyze():
    if 'directory' not in request.form:
        return jsonify({'error': 'Diretório não especificado'}), 400
        
    directory = request.form['directory']
    if not os.path.exists(directory):
        return jsonify({'error': 'Diretório não encontrado'}), 404

    try:
        stats = {
            'files': 0,
            'lines': 0,
            'methods': 0,
            'subdirs': 0
        }
        
        # Contagem de arquivos Java e subdiretórios
        for root, dirs, files in os.walk(directory):
            java_files = [f for f in files if f.endswith('.java')]
            stats['files'] += len(java_files)
            stats['subdirs'] += len(dirs)
            
            for file in java_files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['lines'] += len(content.splitlines())
                    # Conta métodos com CNPJ
                    stats['methods'] += len(re.findall(r'\b(public|private|protected)\s+\w+\s+\w+\s*\([^)]*\)\s*\{[^}]*cnpj[^}]*\}', content, re.IGNORECASE))
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_file(
        os.path.join(REPORTS_DIR, filename),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)
