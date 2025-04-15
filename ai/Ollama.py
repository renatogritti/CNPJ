
from .AiModelInterface import AIModelInterface
import requests
import logging
from typing import Optional

# Implementação para Ollama com CodeMistral
class OllamaModel(AIModelInterface):
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "codellama"):
        self.base_url = base_url
        self.model_name = model_name
        
    def analyze_code(self, prompt: str, language: str, code: str, context_extra: str = "") -> str:
        # Formatar o prompt para o Ollama
        formatted_prompt = prompt.format(language=language, code=code + context_extra)
        
        # Preparar a requisição para a API do Ollama
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": formatted_prompt,
            "system": "Você é um analisador de código que responde APENAS com JSON válido em uma única linha, sem formatação ou textos adicionais.",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "response" in data:
                return data["response"]
            else:
                raise ValueError("Formato de resposta inesperado do Ollama")
        except Exception as e:
            logging.error(f"Erro na comunicação com Ollama: {str(e)}")
            raise