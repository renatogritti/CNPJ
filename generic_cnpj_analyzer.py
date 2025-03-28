import re
from pathlib import Path
import pandas as pd
import json
import anthropic
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain.output_parsers import PydanticOutputParser
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
    dependencias: List[str] = Field(description="Outros métodos/classes que dependem ou são chamados")
    sistemas_impactados: List[str] = Field(description="Outros sistemas/integrações impactados")

class GenericCNPJAnalyzer:
    def __init__(self):
        self.findings = []
        self.client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.parser = PydanticOutputParser(pydantic_object=AnaliseResponse)
        self.all_methods = {}  # Armazenar todos os métodos para análise de dependências
        
        # Mapeamento de extensões para linguagens suportadas (corrigido)
        self.supported_extensions = {
            'java': ['.java'],
            'csharp': ['.cs', '.cshtml', '.csx'],
            'c': ['.c', '.h'],
            'cpp': ['.cpp', '.hpp', '.cc', '.cxx', '.h', '.hxx', '.hh'],
            'html': ['.html', '.htm', '.xhtml', '.aspx'],
            'javascript': ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'],
            'python': ['.py', '.pyw', '.ipynb', '.pyc'],
            'go': ['.go'],
            'sql': ['.sql']
        }
        
        # Regex para encontrar menções a CNPJ em qualquer contexto (padrões separados para cada linguagem)
        self.cnpj_pattern = r'(?:cnpj|cadastro\s+nacional\s+(?:de|da)\s+pessoa\s+jur[íi]dica|\b\d{2}[.-]?\d{3}[.-]?\d{3}[/]?\d{4}[-]?\d{2}\b)'
        
        # Padrões específicos por linguagem para melhor detecção
        self.cnpj_language_patterns = {
            'java': r'(?:cnpj|CNPJ|getCnpj|setCnpj|validaCnpj|cadastro\s+nacional)',
            'csharp': r'(?:cnpj|CNPJ|GetCnpj|SetCnpj|ValidaCnpj|cadastro\s+nacional)',
            'python': r'(?:cnpj|CNPJ|get_cnpj|set_cnpj|valida_cnpj|cadastro\s+nacional)',
            'javascript': r'(?:cnpj|CNPJ|getCnpj|setCnpj|validaCnpj|cadastro\s+nacional)',
            'c': r'(?:cnpj|CNPJ|get_cnpj|set_cnpj|valida_cnpj|cadastro\s+nacional)',
            'cpp': r'(?:cnpj|CNPJ|getCnpj|setCnpj|validaCnpj|cadastro\s+nacional)',
            'go': r'(?:cnpj|CNPJ|GetCnpj|SetCnpj|ValidaCnpj|cadastro\s+nacional)',
            'sql': r'(?:cnpj|CNPJ|cadastro\s+nacional)',
            'html': r'(?:cnpj|CNPJ|cadastro\s+nacional)'
        }
        
        # Padrões de detecção para cada linguagem (refinados)
        self.patterns = {
            'java': {
                'class': r'class\s+(\w+)',
                'method': r'(?:public|private|protected)?\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:\{|throws)',
                'cnpj_method': None  # Definido dinamicamente no método analyze_file
            },
            'csharp': {
                'class': r'class\s+(\w+)',
                # Melhorado para capturar métodos C# mais precisamente, incluindo async/readonly/override
                'method': r'(?:public|private|protected|internal)?\s+(?:static\s+|virtual\s+|async\s+|override\s+|readonly\s+)?[\w<>\[\]\.]+\s+(\w+)\s*\([^)]*\)\s*(?:\{|=>|\s*where)',
                'cnpj_method': None
            },
            'c': {
                'class': r'struct\s+(\w+)',
                'method': r'[\w\*]+\s+(\w+)\s*\([^;]*\)\s*\{',
                'cnpj_method': None
            },
            'cpp': {
                'class': r'(?:class|struct)\s+(\w+)',
                'method': r'(?:virtual\s+)?[\w:~\*<>\[\]]+\s+(\w+)\s*\([^;]*\)(?:\s*const)?\s*(?:\{|override|final)',
                'cnpj_method': None
            },
            'html': {
                'class': r'<[^>]*class=["\'](.*?)["\']',
                'method': r'(?:<script[^>]*>.*?)?function\s+(\w+)|(\w+)\s*=\s*function',
                'cnpj_method': None
            },
            'javascript': {
                'class': r'class\s+(\w+)|function\s+(\w+)',
                'method': r'(?:function\s+(\w+)|const\s+(\w+)\s*=|let\s+(\w+)\s*=|var\s+(\w+)\s*=|(\w+)\s*:\s*function)\s*\([^)]*\)',
                'cnpj_method': None
            },
            'python': {
                'class': r'class\s+(\w+)',
                'method': r'def\s+(\w+)\s*\([^)]*\)\s*:',
                'cnpj_method': None
            },
            'go': {
                'class': r'type\s+(\w+)\s+struct',
                'method': r'func\s+(?:\([^)]*\))?\s*(\w+)',
                'cnpj_method': None
            },
            'sql': {
                'class': r'CREATE\s+TABLE\s+(\w+)',
                'method': r'CREATE\s+(?:OR\s+REPLACE\s+)?(?:PROCEDURE|FUNCTION)\s+(\w+)',
                'cnpj_method': None
            }
        }
        
        # Prompt genérico para análise de código
        self.prompt = r"""
Analise este código de {language} que manipula CNPJ e suas dependências:

{code}

Retorne APENAS um JSON válido com o seguinte formato, sem texto adicional.
IMPORTANTE: 
- Identifique chamadas para outros métodos/classes
- Analise integrações com outros sistemas
- Verifique dependências em cascata
- Considere impactos em APIs e serviços

{{
    "tipo_uso": "NUMERICO|TEXTO|MISTO",
    "operacoes_numericas": ["lista", "de", "operacoes"],
    "impactos": ["lista", "de", "impactos"],
    "riscos": ["lista", "de", "riscos"],
    "modificacoes": ["lista", "de", "modificacoes"],
    "severidade": "ALTA|MEDIA|BAIXA",
    "horas_desenvolvimento": 0,
    "horas_testes": 0,
    "dependencias": ["lista", "de", "dependencias"],
    "sistemas_impactados": ["lista", "de", "sistemas"]
}}"""

    def scan_directory(self, directory):
        # Criar uma lista com todas as extensões para procurar
        all_extensions = []
        for ext_list in self.supported_extensions.values():
            all_extensions.extend(ext_list)
            
        # Contar arquivos processados por linguagem para depuração
        processed_count = {lang: 0 for lang in self.supported_extensions.keys()}
        cnpj_count = {lang: 0 for lang in self.supported_extensions.keys()}
        
        for file in Path(directory).rglob("*"):
            if file.suffix.lower() in all_extensions:
                language = self.detect_language(file.suffix.lower())
                if language:
                    processed_count[language] += 1
                    has_cnpj = self.analyze_file(file, language)
                    if has_cnpj:
                        cnpj_count[language] += 1
        
        # Log das estatísticas para ajudar na depuração
        logging.info("Estatísticas de processamento:")
        for lang in processed_count:
            if processed_count[lang] > 0:
                logging.info(f"{lang}: {cnpj_count[lang]} arquivos com CNPJ de {processed_count[lang]} processados")
    
    def detect_language(self, extension):
        for language, extensions in self.supported_extensions.items():
            if extension in extensions:
                return language
        return None  # Linguagem não suportada
    
    def analyze_file(self, file_path, language):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not language or language not in self.patterns:
                logging.warning(f"Linguagem não suportada para o arquivo: {file_path}")
                return False
                
            logging.info(f"Analisando arquivo {language}: {file_path}")
            
            # Usar o padrão específico para a linguagem, se disponível
            lang_cnpj_pattern = self.cnpj_language_patterns.get(language, self.cnpj_pattern)
            
            # Verificar se o arquivo contém CNPJ antes de prosseguir
            has_cnpj = bool(re.search(lang_cnpj_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL))
            if not has_cnpj:
                return False
                
            logging.info(f"CNPJ encontrado no arquivo: {file_path}")
            
            # Obter padrões específicos da linguagem
            patterns = self.patterns[language]
            
            # Construir dinamicamente o padrão para métodos com CNPJ
            # Tratamento especial para Java, restaurando o padrão original que funcionava
            if language == 'java':
                # Restaurar o padrão original do JavaCNPJAnalyzer que funcionava bem
                patterns['cnpj_method'] = r'(?:public|private|protected)?\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\([^)]*\)\s*(?:\{|throws)[^}]*cnpj[^}]*\}'
            elif language == 'csharp':
                # Padrão específico e mais abrangente para C#
                patterns['cnpj_method'] = r'(?:public|private|protected|internal)?\s+(?:static\s+|virtual\s+|async\s+|override\s+|readonly\s+)?[\w<>\[\]\.]+\s+(\w+)\s*\([^)]*\)\s*(?:\{|=>|\s*where)[^}]*(?:cnpj|CNPJ|Cnpj)[^}]*\}'
            elif language == 'cpp':
                patterns['cnpj_method'] = patterns['method'].replace(')', r')[^}]*(?:' + lang_cnpj_pattern + r')[^}]*\}')
            elif language == 'python':
                patterns['cnpj_method'] = patterns['method'] + r'(?:[^#]*?(?:' + lang_cnpj_pattern + r'))'
            elif language == 'sql':
                patterns['cnpj_method'] = patterns['method'] + r'(?:[^;]*?(?:' + lang_cnpj_pattern + r')[^;]*?;)'
            elif language == 'html' or language == 'javascript':
                patterns['cnpj_method'] = patterns['method'].replace(')', r')[^}]*(?:' + lang_cnpj_pattern + r')[^}]*\}')
            elif language == 'go':
                patterns['cnpj_method'] = patterns['method'] + r'(?:[^}]*?(?:' + lang_cnpj_pattern + r')[^}]*?\})'
            elif language == 'c':
                patterns['cnpj_method'] = patterns['method'].replace('{', r'{[^}]*(?:' + lang_cnpj_pattern + r')[^}]*\}')
            
            # Primeira passagem: coletar todos os métodos/funções
            current_class = None
            for match in re.finditer(patterns['class'], content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                # Diferentes linguagens podem ter diferentes grupos para o nome da classe
                for group in match.groups():
                    if group:
                        current_class = group
                        break
            
            # Encontrar todos os métodos
            for match in re.finditer(patterns['method'], content, re.IGNORECASE | re.MULTILINE | re.DOTALL):
                method_name = None
                # Diferentes linguagens podem ter diferentes grupos para o nome do método
                for group in match.groups():
                    if group and not re.match(r'(public|private|protected|internal|static|const|let|var)', group):
                        method_name = group
                        break
                
                if method_name:
                    full_name = f"{current_class}.{method_name}" if current_class else method_name
                    self.all_methods[full_name] = {
                        'file': str(file_path),
                        'content': match.group(0),
                        'line': content.count('\n', 0, match.start()) + 1,
                        'language': language
                    }
            
            # Variável para rastrear se algum método com CNPJ foi encontrado
            found_cnpj_method = False
            
            # Segunda passagem: verificar blocos de código para CNPJ
            if language == 'python':
                # Para Python, precisamos considerar a indentação, não chaves
                lines = content.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i]
                    match = re.search(patterns['method'], line)
                    if match:
                        method_name = None
                        for group in match.groups():
                            if group:
                                method_name = group
                                break
                        
                        # Encontrar o fim do método baseado na indentação
                        method_start = i
                        method_indent = len(line) - len(line.lstrip())
                        i += 1
                        method_body = [line]
                        
                        while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > method_indent):
                            method_body.append(lines[i])
                            i += 1
                            
                        method_content = '\n'.join(method_body)
                        
                        # Usar flags como parâmetros, não como parte do padrão
                        if re.search(self.cnpj_pattern, method_content, re.IGNORECASE):
                            found_cnpj_method = True
                            method_signature = f"{str(file_path)}:{method_name}"
                            
                            # Encontrar chamadas para outros métodos
                            calls = re.findall(r'(\w+)\s*\(', method_content)
                            dependencies = []
                            for call in calls:
                                for full_name, details in self.all_methods.items():
                                    if call in full_name:
                                        dependencies.append(f"{full_name} ({details['file']}:{details['line']})")
                            
                            self.analyze_with_llm(method_content, str(file_path), method_start + 1, language, dependencies)
                        continue
                    i += 1
            else:
                # Para outras linguagens, usar o regex definido
                if patterns['cnpj_method']:
                    try:
                        cnpj_methods = re.finditer(
                            patterns['cnpj_method'], 
                            content, 
                            re.IGNORECASE | re.MULTILINE | re.DOTALL
                        )
                        
                        # Usar set para evitar métodos duplicados
                        analyzed_methods = set()
                        
                        for method in cnpj_methods:
                            found_cnpj_method = True
                            method_name = self.extract_method_name(method.group(), language)
                            method_signature = f"{str(file_path)}:{method_name}"
                            
                            # Pular se já analisou este método
                            if method_signature in analyzed_methods:
                                continue
                                
                            analyzed_methods.add(method_signature)
                            
                            start_line = content.count('\n', 0, method.start()) + 1
                            method_content = method.group()
                            
                            # Encontrar chamadas para outros métodos (padrão genérico)
                            calls = re.findall(r'(\w+)\s*\([^)]*\)', method_content)
                            dependencies = []
                            for call in calls:
                                for full_name, details in self.all_methods.items():
                                    if call in full_name:
                                        dependencies.append(f"{full_name} ({details['file']}:{details['line']})")
                            
                            self.analyze_with_llm(method_content, str(file_path), start_line, language, dependencies)
                    except Exception as e:
                        logging.error(f"Erro ao analisar métodos com CNPJ: {str(e)}")
            
            # FALLBACK: Se não encontrou métodos específicos, mas o arquivo contém CNPJ,
            # analisar o arquivo como um todo para linguagens específicas
            if not found_cnpj_method and has_cnpj:
                logging.info(f"Nenhum método específico com CNPJ encontrado, analisando arquivo completo: {file_path}")
                
                # Verificação especial para Java
                if language == 'java':
                    # Tentar encontrar métodos de forma menos restritiva
                    fallback_pattern = r'(?:public|private|protected)?\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{[^}]*(?:cnpj|CNPJ)[^}]*\}'
                    try:
                        fallback_methods = list(re.finditer(fallback_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL))
                        if fallback_methods:
                            for method in fallback_methods:
                                method_name = self.extract_method_name(method.group(), 'java')
                                start_line = content.count('\n', 0, method.start()) + 1
                                self.analyze_with_llm(method.group(), str(file_path), start_line, 'java', [])
                            return has_cnpj
                    except Exception as e:
                        logging.error(f"Erro ao tentar fallback Java: {str(e)}")
                
                # Verificação especial para C#
                elif language == 'csharp':
                    # Tentar encontrar métodos de forma menos restritiva
                    fallback_pattern = r'(?:public|private|protected|internal)?\s+[\w<>\[\]\.]+\s+(\w+)\s*\([^)]*\)\s*\{[^}]*(?:cnpj|CNPJ|Cnpj)[^}]*\}'
                    try:
                        fallback_methods = list(re.finditer(fallback_pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL))
                        if fallback_methods:
                            for method in fallback_methods:
                                method_name = self.extract_method_name(method.group(), 'csharp')
                                start_line = content.count('\n', 0, method.start()) + 1
                                self.analyze_with_llm(method.group(), str(file_path), start_line, 'csharp', [])
                            return has_cnpj
                    except Exception as e:
                        logging.error(f"Erro ao tentar fallback C#: {str(e)}")
                
                # Arquivos especiais como HTML, SQL que podem não ter métodos
                if language in ['html', 'sql'] or (
                   language in ['javascript', 'python', 'c', 'cpp'] and 
                   len(content) < 5000):  # Limitar tamanho para evitar tokens demais
                    
                    # Extrai um trecho relevante contendo CNPJ
                    cnpj_sections = []
                    # Usar flags como parâmetros em vez de inline
                    for match in re.finditer(self.cnpj_pattern, content, re.IGNORECASE):
                        # Pegar contexto de 500 caracteres antes e depois
                        start = max(0, match.start() - 500)
                        end = min(len(content), match.end() + 500)
                        cnpj_context = content[start:end]
                        cnpj_sections.append(cnpj_context)
                    
                    if cnpj_sections:
                        # Juntar seções com contexto para criar um trecho representativo
                        context_sample = "\n\n[...]\n\n".join(cnpj_sections[:3])  # Limitar a 3 seções
                        self.analyze_with_llm(context_sample, str(file_path), 1, language, [])
            
            return has_cnpj
                
        except Exception as e:
            logging.error(f"Erro ao analisar arquivo {file_path}: {str(e)}", exc_info=True)
            return False

    def analyze_with_llm(self, node, file_path, start_line, language, dependencies=None):
        try:
            logging.info(f"Analisando código {language}: {file_path}")
            
            # Incluir dependências encontradas no prompt
            contexto_extra = ""
            if dependencies:
                contexto_extra = "\nDependências encontradas:\n" + "\n".join(dependencies)

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                temperature=0,
                system="Você é um analisador de código que responde APENAS com JSON válido em uma única linha, sem formatação ou textos adicionais.",
                messages=[
                    {
                        "role": "user",
                        "content": self.prompt.format(language=language, code=node + contexto_extra)
                    }
                ]
            )
            
            # Extrair e limpar JSON da resposta
            response_text = message.content[0].text
            
            if not response_text:
                raise ValueError("Resposta vazia do Claude")
            
            # Encontrar o JSON na string
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("JSON não encontrado na resposta")
                
            json_str = json_match.group()
            
            # Parse do JSON
            try:
                analysis = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Erro no parse do JSON: {str(e)}")

            # Validar campos obrigatórios
            required_fields = ['tipo_uso', 'operacoes_numericas', 'impactos', 
                             'riscos', 'modificacoes', 'severidade', 'horas_desenvolvimento', 'horas_testes']
            missing_fields = [field for field in required_fields if field not in analysis]
            if missing_fields:
                raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")

            self.findings.append({
                'arquivo': file_path,
                'linguagem': language,
                'metodo': self.extract_method_name(node, language),
                'linha': start_line,
                'tipo_uso': analysis['tipo_uso'],
                'operacoes_numericas': "\n".join(analysis['operacoes_numericas']),
                'impactos': "\n".join(analysis['impactos']),
                'riscos': "\n".join(analysis['riscos']),
                'modificacoes': "\n".join(analysis['modificacoes']),
                'severidade': analysis['severidade'],
                'horas_dev': analysis['horas_desenvolvimento'],
                'horas_teste': analysis['horas_testes'],
                'horas_total': analysis['horas_desenvolvimento'] + analysis['horas_testes'],
                'dependencias': "\n".join(dependencies) if dependencies else "Nenhuma dependência encontrada",
                'sistemas_impactados': "\n".join(analysis.get('sistemas_impactados', []))
            })
        except Exception as e:
            logging.error(f"Erro na análise: {str(e)}")
            self.findings.append({
                'arquivo': file_path,
                'linguagem': language,
                'metodo': self.extract_method_name(node, language),
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

    def extract_method_name(self, method_code, language):
        # Padrões específicos para cada linguagem
        patterns = {
            'java': r'(?:public|private|protected)?\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(',
            'csharp': r'(?:public|private|protected|internal)?\s+(?:static\s+|virtual\s+|async\s+|override\s+|readonly\s+)?[\w<>\[\]\.]+\s+(\w+)\s*\(',
            'c': r'[\w\*]+\s+(\w+)\s*\(',
            'cpp': r'(?:virtual\s+)?[\w:~\*<>\[\]]+\s+(\w+)\s*\(',
            'html': r'function\s+(\w+)|(\w+)\s*=\s*function',
            'javascript': r'function\s+(\w+)|const\s+(\w+)|let\s+(\w+)|var\s+(\w+)|(\w+)\s*:\s*function',
            'python': r'def\s+(\w+)\s*\(',
            'go': r'func\s+(?:\([^)]*\))?\s*(\w+)',
            'sql': r'(?:PROCEDURE|FUNCTION)\s+(\w+)'
        }
        
        pattern = patterns.get(language, r'\w+\s+(\w+)\s*\(')  # Padrão genérico como fallback
        match = re.search(pattern, method_code, re.IGNORECASE)
        
        if match:
            # Verificar todos os grupos para encontrar o nome do método
            for group in match.groups():
                if group and not re.match(r'(public|private|protected|internal|static|const|let|var)', group):
                    return group
        
        return "unknown"

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
            'border': 1,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter'
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
            'linguagem': 12,
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
            'horas_total': 12,
            'dependencias': 50,
            'sistemas_impactados': 30
        }
        
        for col_name, width in col_widths.items():
            if col_name in df.columns:
                col_idx = df.columns.get_loc(col_name)
                worksheet.set_column(col_idx, col_idx, width)
        
        # Formatar células de dados
        for row_num in range(1, len(df) + 1):
            for col_num in range(len(df.columns)):
                if df.columns[col_num] in ['horas_dev', 'horas_teste', 'horas_total']:
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], number_format)
                else:
                    worksheet.write(row_num, col_num, df.iloc[row_num-1, col_num], cell_format)
        
        # Adicionar uma nova aba para dependências
        dep_sheet = workbook.add_worksheet('Dependências')
        dep_sheet.write(0, 0, 'Linguagem', header_format)
        dep_sheet.write(0, 1, 'Método', header_format)
        dep_sheet.write(0, 2, 'Dependências', header_format)
        
        row = 1
        for finding in self.findings:
            if 'linguagem' in finding:
                dep_sheet.write(row, 0, finding['linguagem'])
            dep_sheet.write(row, 1, finding['metodo'])
            dep_sheet.write(row, 2, finding['dependencias'])
            row += 1
        
        dep_sheet.set_column(0, 0, 15)
        dep_sheet.set_column(1, 1, 30)
        dep_sheet.set_column(2, 2, 100)
        
        writer.close()
