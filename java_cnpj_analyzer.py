import re
from pathlib import Path
import pandas as pd
import json
import anthropic
from pydantic import BaseModel, Field
from typing import List
from langchain.output_parsers import PydanticOutputParser  # Ensure this library is installed
import os
from dotenv import load_dotenv
import logging

# Configurar logging no início do arquivo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analyzer.log'),
        logging.StreamHandler()
    ]
)

load_dotenv()  # Carregar variáveis do .env

class AnaliseResponse(BaseModel):
    tipo_uso: str = Field(description="Como o CNPJ é usado: NUMERICO, TEXTO, ou MISTO")
    operacoes_numericas: List[str] = Field(description="Operações matemáticas realizadas com CNPJ")
    impactos: List[str] = Field(description="Impactos da mudança para alfanumérico")
    riscos: List[str] = Field(description="Riscos de compatibilidade")
    modificacoes: List[str] = Field(description="Modificações necessárias no código")
    severidade: str = Field(description="ALTA (quebra código), MEDIA (requer adaptação) ou BAIXA (mudança simples)")
    horas_desenvolvimento: int = Field(description="Estimativa em horas para desenvolvimento")
    horas_testes: int = Field(description="Estimativa em horas para testes unitários")

class JavaCNPJAnalyzer:
    def __init__(self):
        self.findings = []
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.parser = PydanticOutputParser(pydantic_object=AnaliseResponse)
        
        # Corrigir formatação do prompt usando uma raw string
        self.prompt = r"""
Analise este código Java que manipula CNPJ:

{code}

Retorne APENAS um JSON válido com o seguinte formato, sem texto adicional.
IMPORTANTE: Faça uma análise criteriosa das horas, considerando:
- Complexidade do código
- Necessidade de refatoração
- Testes de regressão
- Impacto em outras partes do sistema
- Tempo de implementação realista
- Cobertura adequada de testes

{{
    "tipo_uso": "NUMERICO|TEXTO|MISTO",
    "operacoes_numericas": ["lista", "de", "operacoes"],
    "impactos": ["lista", "de", "impactos"],
    "riscos": ["lista", "de", "riscos"],
    "modificacoes": ["lista", "de", "modificacoes"],
    "severidade": "ALTA|MEDIA|BAIXA",
    "horas_desenvolvimento": 0,
    "horas_testes": 0
}}"""

    def scan_directory(self, directory):
        java_files = Path(directory).rglob("*.java")
        for file in java_files:
            self.analyze_file(file)

    def analyze_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
            
        # Usar regex para encontrar métodos que contêm CNPJ
        method_pattern = r'(public|private|protected)?\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{[^}]*cnpj[^}]*\}'
        for match in re.finditer(method_pattern, content, re.IGNORECASE | re.MULTILINE):
            # Calcular linha inicial do método
            start_line = content.count('\n', 0, match.start()) + 1
            self.analyze_with_llm(match.group(), str(file_path), start_line)

    def analyze_with_llm(self, node, file_path, start_line):
        try:
            logging.info(f"Iniciando análise do arquivo: {file_path}")
            logging.info(f"Enviando request para Claude...")
            
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                temperature=0,  # Reduzir variabilidade
                system="Você é um analisador de código que responde APENAS com JSON válido em uma única linha, sem formatação ou textos adicionais.",
                messages=[
                    {
                        "role": "user",
                        "content": self.prompt.format(code=node)
                    }
                ]
            )
            
            logging.info("Resposta recebida do Claude")
            logging.info(f"Resposta bruta: {message.content[0].text}")
            
            # Extrair e limpar JSON da resposta
            response_text = message.content[0].text
            
            # Debug da resposta
            if not response_text:
                raise ValueError("Resposta vazia do Claude")
                
            logging.info(f"Resposta após limpeza: {response_text}")
            
            # Encontrar o JSON na string
            json_match = re.search(r'\{.*\}', response_text)
            if not json_match:
                raise ValueError("JSON não encontrado na resposta")
                
            json_str = json_match.group()
            
            # Parse do JSON
            try:
                analysis = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"JSON inválido: {json_str}")
                raise ValueError(f"Erro no parse do JSON: {str(e)}")

            # Validar campos obrigatórios
            required_fields = ['tipo_uso', 'operacoes_numericas', 'impactos', 
                             'riscos', 'modificacoes', 'severidade', 'horas_desenvolvimento', 'horas_testes']
            missing_fields = [field for field in required_fields if field not in analysis]
            if missing_fields:
                raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")

            self.findings.append({
                'arquivo': file_path,
                'metodo': self.extract_method_name(node),
                'linha': start_line,
                'tipo_uso': analysis['tipo_uso'],
                'operacoes_numericas': "\n".join(analysis['operacoes_numericas']),
                'impactos': "\n".join(analysis['impactos']),
                'riscos': "\n".join(analysis['riscos']),
                'modificacoes': "\n".join(analysis['modificacoes']),
                'severidade': analysis['severidade'],
                'horas_dev': analysis['horas_desenvolvimento'],
                'horas_teste': analysis['horas_testes'],
                'horas_total': analysis['horas_desenvolvimento'] + analysis['horas_testes']
            })
        except Exception as e:
            logging.error(f"Erro na análise: {str(e)}", exc_info=True)
            self.findings.append({
                'arquivo': file_path,
                'metodo': self.extract_method_name(node),
                'tipo_uso': 'ERRO',
                'operacoes_numericas': f'Erro na análise: {str(e)}',
                'impactos': 'Erro na análise',
                'riscos': 'Erro na análise',
                'modificacoes': 'Erro na análise',
                'severidade': 'N/A',
                'horas_dev': 0,
                'horas_teste': 0,
                'horas_total': 0
            })

    def extract_method_name(self, method_code):
        match = re.search(r'\w+\s+(\w+)\s*\(', method_code)
        return match.group(1) if match else "unknown"

    def generate_report(self):
        df = pd.DataFrame(self.findings)
        return df

    def export_to_excel(self, filename):
        df = self.generate_report()
        
        # Configurar formatação do Excel
        writer = pd.ExcelWriter(filename, engine='xlsxwriter')
        df.to_excel(writer, sheet_name='Análise CNPJ', index=False)
        
        # Ajustar largura das colunas
        workbook = writer.book
        worksheet = writer.sheets['Análise CNPJ']
        
        # Formatos
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'text_wrap': True,
            'valign': 'top'
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'num_format': '0.0',
            'align': 'right'
        })
        
        # Aplicar formatos
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            
        # Larguras das colunas
        col_widths = {
            'arquivo': 40,
            'metodo': 20,
            'linha': 8,
            'tipo_uso': 12,
            'operacoes_numericas': 30,
            'impactos': 40,
            'riscos': 40,
            'modificacoes': 40,
            'severidade': 12,
            'horas_dev': 12,
            'horas_teste': 12,
            'horas_total': 12
        }
        
        for col_name, width in col_widths.items():
            col_idx = df.columns.get_loc(col_name)
            worksheet.set_column(col_idx, col_idx, width)
        
        # Formatar células de dados
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                if df.columns[col_num] in ['horas_dev', 'horas_teste', 'horas_total']:
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], number_format)
                else:
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], cell_format)
        
        writer.close()
