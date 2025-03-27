from java_cnpj_analyzer import JavaCNPJAnalyzer
import os
from datetime import datetime

def main():
    analyzer = JavaCNPJAnalyzer()
    
    # Criar diretório reports se não existir
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    java_directory = input("Digite o caminho do diretório com códigos Java: ")
    
    print("Iniciando análise...")
    analyzer.scan_directory(java_directory)
    
    # Gerar relatórios
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Salvar relatório HTML
    html_file = os.path.join(reports_dir, f'relatorio_cnpj_{timestamp}.html')
    df = analyzer.generate_report()
    html_report = df.to_html(index=False)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"Relatório HTML gerado: {html_file}")
    
    # Gerar relatório Excel
    excel_file = os.path.join(reports_dir, f'analise_cnpj_{timestamp}.xlsx')
    analyzer.export_to_excel(excel_file)
    
    print(f"Relatório Excel gerado: {excel_file}")

if __name__ == "__main__":
    main()
