import re
from pathlib import Path
import pandas as pd
import json
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

class AnaliseResponse(BaseModel):
    tipo_uso: str = Field(description="Como o CNPJ é usado: NUMERICO, TEXTO, ou MISTO")
    operacoes_numericas: List[str] = Field(description="Operações matemáticas realizadas com CNPJ")
    impactos: List[str] = Field(description="Impactos da mudança para alfanumérico")
    riscos: List[str] = Field(description="Riscos de compatibilidade")
    modificacoes: List[str] = Field(description="Modificações necessárias no código")
    severidade: str = Field(description="ALTA (quebra código), MEDIA (requer adaptação) ou BAIXA (mudança simples)")
    esforco_adaptacao: int = Field(description="Estimativa em dias para adaptação")

class JavaCNPJAnalyzer:
    def __init__(self):
        self.findings = []
        self.llm = Ollama(base_url="http://localhost:11434", model="gemma3:4b")
        self.parser = PydanticOutputParser(pydantic_object=AnaliseResponse)
        
        self.prompt = PromptTemplate(
            template="""
            Você é um especialista em análise de impacto de sistemas Java. Analise este código que manipula CNPJ:
            {code}

            CONTEXTO:
            - Atualmente o CNPJ é tratado como número (long/int/numeric)
            - No futuro será alfanumérico, permitindo letras e números
            - Precisamos identificar todos os impactos desta mudança

            ANALISE:
            1. Identifique se o código trata CNPJ como número e faz operações matemáticas
            2. Verifique manipulações numéricas como divisão, módulo, comparação
            3. Avalie impactos em banco de dados, APIs e integrações
            4. Considere problemas de compatibilidade e quebras de código
            
            {format_instructions}
            """,
            input_variables=["code"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def scan_directory(self, directory):
        java_files = Path(directory).rglob("*.java")
        for file in java_files:
            self.analyze_file(file)

    def analyze_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Usar regex para encontrar métodos que contêm CNPJ
        method_pattern = r'(public|private|protected)?\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{[^}]*cnpj[^}]*\}'
        methods = re.finditer(method_pattern, content, re.IGNORECASE | re.MULTILINE)
        
        for method in methods:
            self.analyze_with_llm(method.group(), str(file_path))

    def analyze_with_llm(self, node, file_path):
        try:
            _input = self.prompt.format_prompt(code=node)
            output = self.llm.invoke(_input.to_string())
            analysis = self.parser.parse(output)
            
            self.findings.append({
                'arquivo': file_path,
                'metodo': self.extract_method_name(node),
                'tipo_uso': analysis.tipo_uso,
                'operacoes_numericas': "\n".join(analysis.operacoes_numericas),
                'impactos': "\n".join(analysis.impactos),
                'riscos': "\n".join(analysis.riscos),
                'modificacoes': "\n".join(analysis.modificacoes),
                'severidade': analysis.severidade,
                'esforco_dias': analysis.esforco_adaptacao
            })
        except Exception as e:
            print(f"Erro na análise: {str(e)}")
            self.findings.append({
                'arquivo': file_path,
                'metodo': self.extract_method_name(node),
                'tipo_uso': 'ERRO',
                'operacoes_numericas': 'Erro na análise',
                'impactos': 'Erro na análise',
                'riscos': 'Erro na análise',
                'modificacoes': 'Erro na análise',
                'severidade': 'N/A',
                'esforco_dias': 0
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
        
        for idx, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(idx, idx, max_length)
            
        # Adicionar formatação condicional para severidade
        fmt_high = workbook.add_format({'bg_color': '#FFC7CE'})
        fmt_medium = workbook.add_format({'bg_color': '#FFEB9C'})
        fmt_low = workbook.add_format({'bg_color': '#C6EFCE'})
        
        sev_col = df.columns.get_loc('severidade')
        worksheet.conditional_format(1, sev_col, len(df)+1, sev_col, {
            'type': 'text',
            'criteria': 'containing',
            'value': 'ALTA',
            'format': fmt_high
        })
        
        writer.close()
