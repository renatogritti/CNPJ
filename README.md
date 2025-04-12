# Analisador de CNPJ em Código-Fonte

Uma ferramenta para analisar bases de código e identificar impactos da mudança de CNPJ numérico para alfanumérico.

## Sobre o Projeto

Este analisador examina código-fonte em múltiplas linguagens (Java, C#, Python, JavaScript, etc.) para identificar como o CNPJ é usado e qual o impacto potencial da mudança do formato numérico para alfanumérico.

### Contexto da Mudança do CNPJ

A Receita Federal do Brasil está implementando mudanças no formato do CNPJ, passando de apenas números para um formato alfanumérico. Esta ferramenta ajuda equipes de desenvolvimento a identificar e planejar as adaptações necessárias em seus sistemas.

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
- Pelo menos uma das seguintes opções:
  - API key da Anthropic (Claude AI)
  - API key da Mistral AI
  - Ollama instalado localmente (com modelo Codestral)

## Configuração

1. Clone o repositório
   ```
   git clone https://github.com/seu-usuario/analisador-cnpj.git
   cd analisador-cnpj
   ```
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure seu provedor de IA de preferência:
   
   **Opção 1: Anthropic (Claude)**
   ```
   ANTHROPIC_API_KEY=sua_chave_aqui
   AI_PROVIDER=anthropic
   ```
   
   **Opção 2: Mistral AI**
   ```
   MISTRAL_API_KEY=sua_chave_aqui
   AI_PROVIDER=mistral
   ```
   
   **Opção 3: Ollama Local (Codestral)**
   ```
   OLLAMA_URL=http://localhost:11434
   AI_PROVIDER=ollama
   OLLAMA_MODEL=codestral
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

### Via Linha de Comando

```bash
python analyzer_cli.py --path /caminho/para/codigo --output relatorio.xlsx
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

### Exemplo de Saída

O relatório Excel inclui as seguintes informações para cada ocorrência de CNPJ:

| Arquivo | Linha | Tipo de Uso | Severidade | Horas Estimadas | Sugestão de Adaptação |
|---------|-------|-------------|------------|-----------------|----------------------|
| App.java | 42 | Numérico | Alta | 3 | Converter para string e remover operações aritméticas |
| utils.py | 156 | Textual | Baixa | 0.5 | Já trata como string, apenas revisar validações |

## Estrutura do Projeto

- `app.py` - Aplicação Flask para interface web
- `generic_cnpj_analyzer.py` - Analisador principal
- `analyzer_cli.py` - Interface de linha de comando
- `static/` - Arquivos CSS e JavaScript
- `templates/` - Templates HTML
- `reports/` - Relatórios gerados em Excel

## Contribuindo

Contribuições são bem-vindas! Por favor, siga estes passos:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## FAQ

### O que é a mudança de CNPJ alfanumérico?
A Receita Federal está planejando alterar o formato dos CNPJs de puramente numérico para alfanumérico, o que impactará sistemas que assumem que CNPJs são apenas números.

### A ferramenta modifica meu código?
Não, a ferramenta apenas analisa e reporta os possíveis impactos, sem modificar o código-fonte.

### Quão precisa é a análise?
A análise é baseada em padrões comuns de uso de CNPJ e assistida por IA, mas recomendamos revisão humana dos resultados.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

Para dúvidas ou suporte, entre em contato através de issues no GitHub ou pelo email: seu-email@exemplo.com
