from .AiModelInterface import AIModelInterface
import requests
import logging

# Implementação para API da Mistral
class MistralAPIModel(AIModelInterface):
    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        
    def analyze_code(self, prompt: str, language: str, code: str, context_extra: str = "") -> str:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Formatar o prompt para o Mistral
        formatted_prompt = prompt.format(language=language, code=code + context_extra)
        
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Você é um analisador de código que responde APENAS com JSON válido em uma única linha, sem formatação ou textos adicionais."
                },
                {
                    "role": "user",
                    "content": formatted_prompt
                }
            ],
            "temperature": 0.0,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "choices" in data and len(data["choices"]) > 0:
                message_content = data["choices"][0]["message"]["content"]
                return message_content
            else:
                raise ValueError("Formato de resposta inesperado da API Mistral")
        except Exception as e:
            logging.error(f"Erro na comunicação com API Mistral: {str(e)}")
            raise
