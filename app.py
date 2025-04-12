"""
Aplicação Flask para interface web do analisador de CNPJ.

Este módulo fornece uma interface web para o GenericCNPJAnalyzer,
permitindo que usuários realizem análises de código através do navegador.
"""

from flask import Flask, render_template, request, jsonify, send_file
from generic_cnpj_analyzer import GenericCNPJAnalyzer
from datetime import datetime
import os
from pathlib import Path
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_app.log'),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Configuração do modelo de IA
AI_MODEL_TYPE = os.getenv("AI_MODEL_TYPE", "anthropic")  # Valor padrão: anthropic
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

logging.info(f"Configuração do modelo de IA: {AI_MODEL_TYPE} " + 
             (f"(Ollama: {OLLAMA_MODEL} em {OLLAMA_URL})" if AI_MODEL_TYPE.lower() == "ollama" else "") +
             (f"(Mistral: {MISTRAL_MODEL})" if AI_MODEL_TYPE.lower() == "mistral" else ""))

# Criar diretório reports se não existir
REPORTS_DIR = os.path.join(os.path.dirname(__file__), 'reports')
os.makedirs(REPORTS_DIR, exist_ok=True)

@app.route('/')
def index():
    """
    Rota principal que renderiza a página inicial.

    Returns:
        str: HTML da página inicial
    """
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Rota para executar a análise completa de um diretório.

    Espera receber o caminho do diretório via POST.
    Gera um relatório Excel com os resultados.

    Returns:
        Response: JSON com status da análise e caminho do relatório
    """
    logging.info("Iniciando nova análise")
    if 'directory' not in request.form:
        logging.error("Diretório não especificado")
        return jsonify({'error': 'Diretório não especificado'}), 400
        
    directory = request.form['directory']
    logging.info(f"Analisando diretório: {directory}")
    
    if not os.path.exists(directory):
        logging.error("Diretório não encontrado")
        return jsonify({'error': 'Diretório não encontrado'}), 404

    try:
        # Inicializar analisador com o modelo de IA configurado
        analyzer = GenericCNPJAnalyzer(
            model_type=AI_MODEL_TYPE,
            ollama_url=OLLAMA_URL,
            ollama_model=OLLAMA_MODEL,
            mistral_model=MISTRAL_MODEL
        )
        analyzer.scan_directory(directory)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Gerar relatórios no diretório reports
        excel_file = os.path.join(REPORTS_DIR, f'analise_cnpj_{timestamp}.xlsx')
        analyzer.export_to_excel(excel_file)
        
        logging.info(f"Análise concluída com sucesso. Relatório salvo em: {excel_file}")
        return jsonify({
            'status': 'success',
            'data': analyzer.findings,
            'excel_file': os.path.basename(excel_file)
        })
    except Exception as e:
        logging.error(f"Erro durante a análise: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/pre-analyze', methods=['POST'])
def pre_analyze():
    """
    Rota para análise prévia do diretório.

    Realiza uma análise rápida para contar arquivos e métodos,
    sem executar a análise completa.

    Returns:
        Response: JSON com estatísticas preliminares
    """
    if 'directory' not in request.form:
        return jsonify({'error': 'Diretório não especificado'}), 400
        
    directory = request.form['directory']
    if not os.path.exists(directory):
        return jsonify({'error': 'Diretório não encontrado'}), 404

    try:
        # Obter extensões suportadas do analisador com configuração do modelo
        analyzer = GenericCNPJAnalyzer(
            model_type=AI_MODEL_TYPE,
            ollama_url=OLLAMA_URL,
            ollama_model=OLLAMA_MODEL,
            mistral_model=MISTRAL_MODEL
        )
        supported_extensions = []
        for ext_list in analyzer.supported_extensions.values():
            supported_extensions.extend(ext_list)
        
        stats = {
            'files': 0,
            'lines': 0,
            'methods': 0,
            'subdirs': 0,
            'by_language': {}
        }
        
        # Inicializar contagens por linguagem
        for language in analyzer.supported_extensions.keys():
            stats['by_language'][language] = 0
        
        # Contagem de arquivos e subdiretórios
        for root, dirs, files in os.walk(directory):
            stats['subdirs'] += len(dirs)
            
            # Filtrar apenas arquivos com extensões suportadas
            code_files = []
            for file in files:
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in supported_extensions:
                    code_files.append(file)
            
            stats['files'] += len(code_files)
            
            # Padrão para encontrar CNPJ em qualquer contexto (usar o mesmo do analisador)
            cnpj_pattern = analyzer.cnpj_pattern
            
            for file in code_files:
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()
                
                # Determinar a linguagem pela extensão
                file_language = None
                for language, extensions in analyzer.supported_extensions.items():
                    if file_ext in extensions:
                        file_language = language
                        break
                
                if file_language:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.splitlines()
                            stats['lines'] += len(lines)
                            
                            # Verificar se contém CNPJ - usar flags como parâmetros
                            if re.search(cnpj_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                                stats['by_language'][file_language] += 1
                                
                                # Tentar contar métodos com CNPJ usando os padrões do analisador
                                if file_language in analyzer.patterns:
                                    # Definir o método pattern para métodos com CNPJ
                                    method_pattern = analyzer.patterns[file_language]['method']
                                    
                                    # Contagem específica para Python
                                    if file_language == 'python':
                                        method_matches = re.finditer(method_pattern, content, re.IGNORECASE | re.MULTILINE)
                                        for method_match in method_matches:
                                            # Extrair o método e seu conteúdo indentado
                                            method_start_line = content.count('\n', 0, method_match.start())
                                            if method_start_line < len(lines):
                                                method_line = lines[method_start_line]
                                                method_indent = len(method_line) - len(method_line.lstrip())
                                                
                                                # Construir o corpo do método
                                                method_body = [method_line]
                                                for i in range(method_start_line + 1, len(lines)):
                                                    if not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > method_indent:
                                                        method_body.append(lines[i])
                                                    else:
                                                        break
                                                
                                                method_text = '\n'.join(method_body)
                                                # Usar flags como parâmetros
                                                if re.search(cnpj_pattern, method_text, re.IGNORECASE):
                                                    stats['methods'] += 1
                                    else:
                                        # Para outras linguagens
                                        method_matches = list(re.finditer(method_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL))
                                        
                                        for i, method_match in enumerate(method_matches):
                                            method_start = method_match.start()
                                            
                                            # Encontrar o final do método - ou próximo método ou fim do arquivo
                                            if i < len(method_matches) - 1:
                                                method_end = method_matches[i+1].start()
                                            else:
                                                method_end = len(content)
                                            
                                            method_content = content[method_start:method_end]
                                            
                                            # Verifique se contém CNPJ no conteúdo do método
                                            if re.search(cnpj_pattern, method_content, re.IGNORECASE):
                                                stats['methods'] += 1
                    except Exception as e:
                        logging.warning(f"Erro ao analisar arquivo {file_path}: {str(e)}")
        
        return jsonify(stats)
    except Exception as e:
        logging.error(f"Erro na pré-análise: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    """
    Rota para download do relatório Excel gerado.

    Args:
        filename (str): Nome do arquivo a ser baixado

    Returns:
        Response: Arquivo Excel para download
    """
    return send_file(
        os.path.join(REPORTS_DIR, filename),
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True)
