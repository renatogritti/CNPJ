import re
from pathlib import Path
from typing import Optional

def extract_method_name(method_code: str, language: str) -> str:
    """
    Extrai o nome do método de um trecho de código.
    """
    patterns = {
        'java': r'(?:public|private|protected)?\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(',
        'csharp': r'(?:public|private|protected|internal)?\s+(?:static\s+|virtual\s+|async\s+|override\s+|readonly\s+)?[\w<>\[\]\.]+\s+(\w+)\s*\(',
        'c': r'[\w\*]+\s+(\w+)\s*\(',
        'cpp': r'(?:[\w:~\*<>\[\]&]+\s+)?(\w+)\s*\(',
        'html': r'function\s+(\w+)|(\w+)\s*=\s*function',
        'javascript': r'function\s+(\w+)|const\s+(\w+)|let\s+(\w+)|var\s+(\w+)|(\w+)\s*:\s*function',
        'python': r'def\s+(\w+)\s*\(',
        'go': r'func\s+(?:\([^)]*\))?\s*(\w+)',
        'sql': r'(?:PROCEDURE|FUNCTION)\s+(\w+)'
    }
    pattern = patterns.get(language, r'\w+\s+(\w+)\s*\(')
    match = re.search(pattern, method_code, re.IGNORECASE)
    if match:
        for group in match.groups():
            if group and not re.match(r'(public|private|protected|internal|static|const|let|var)', group):
                return group
    return "unknown"

def detect_language(extension: str, supported_extensions: dict) -> Optional[str]:
    """
    Detecta a linguagem de programação baseada na extensão do arquivo.
    """
    for language, extensions in supported_extensions.items():
        if extension in extensions:
            return language
    return None
