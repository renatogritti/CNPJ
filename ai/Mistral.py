from .AiModelInterface import AIModelInterface
import requests  # Faltava esta importação
import logging
import time
import random

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
        
        # Implementar retry com exponential backoff
        max_retries = 5
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.post(self.api_url, headers=headers, json=payload)
                response.raise_for_status()
                
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    raise ValueError("Formato de resposta inesperado da API Mistral")
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    retry_count += 1
                    if retry_count >= max_retries:
                        logging.error("Limite máximo de tentativas atingido para Mistral API")
                        raise
                    
                    # Exponential backoff com jitter
                    wait_time = (2 ** retry_count) + random.uniform(0, 1)
                    logging.warning(f"Erro 429 - Rate limit atingido. Aguardando {wait_time:.2f}s antes de tentar novamente...")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Erro HTTP na API Mistral: {str(e)}")
                    raise
            except Exception as e:
                logging.error(f"Erro na comunicação com a API Mistral: {str(e)}")
                raise
                
        raise Exception("Falha após múltiplas tentativas na API Mistral")
