# Analisador de CNPJ em Código-Fonte

Uma ferramenta para analisar bases de código e identificar impactos da mudança de CNPJ numérico para alfanumérico.

## Sobre o Projeto

Este analisador examina código-fonte em múltiplas linguagens (Java, C#, Python, JavaScript, etc.) para identificar como o CNPJ é usado e qual o impacto potencial da mudança do formato numérico para alfanumérico.

## Funcionalidades

- Análise automática de bases de código em múltiplas linguagens
- Identificação de métodos e classes que manipulam CNPJ
- Categorização por tipo de uso (Numérico, Textual, Misto)
- Detecção de operações aritméticas com CNPJ
- Estimativa de horas para adaptação e testes
- Classificação por severidade do impacto
- Geração de relatórios em Excel
- Interface web para facilitar o uso

## Requisitos

- Python 3.8+
- API key da Anthropic (Claude AI)

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Crie um arquivo `.env` na raiz do projeto com sua chave API:
   ```
   ANTHROPIC_API_KEY=sua_chave_aqui
   ```

## Uso

### Via Interface Web

1. Inicie o servidor Flask:
   ```
   python app.py
   ```
2. Acesse `http://localhost:5000` no navegador
3. Insira o caminho do diretório a ser analisado
4. Clique em "Analisar"
5. Baixe o relatório em Excel após a conclusão

### Via Código

```python
from generic_cnpj_analyzer import GenericCNPJAnalyzer

analyzer = GenericCNPJAnalyzer()
analyzer.scan_directory("/caminho/para/codigo")
analyzer.export_to_excel("relatorio.xlsx")
```

## Linguagens Suportadas

- Java
- C#
- C/C++
- Python
- JavaScript/TypeScript
- Go
- SQL
- HTML

## Como Funciona

1. A ferramenta percorre recursivamente todos os arquivos no diretório especificado
2. Para cada arquivo com extensão suportada, procura menções a CNPJ
3. Analisa o contexto de uso do CNPJ com o Claude AI
4. Categoriza o impacto e sugere modificações necessárias
5. Compila resultados em relatório detalhado

## Estrutura do Projeto

- `app.py` - Aplicação Flask para interface web
- `generic_cnpj_analyzer.py` - Analisador principal
- `static/` - Arquivos CSS e JavaScript
- `templates/` - Templates HTML
- `reports/` - Relatórios gerados em Excel
