import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_app.log'),
        logging.StreamHandler()
    ]
)

# Configuração do modelo de IA
AI_MODEL_TYPE = os.getenv("AI_MODEL_TYPE", "anthropic") # Valor padrão: anthropic
print(f"AI_MODEL_TYPE: {AI_MODEL_TYPE}")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-large-latest")

logging.info(f"Configuração do modelo de IA: {AI_MODEL_TYPE} " + 
             (f"(Ollama: {OLLAMA_MODEL} em {OLLAMA_URL})" if AI_MODEL_TYPE.lower() == "ollama" else "") +
             (f"(Mistral: {MISTRAL_MODEL})" if AI_MODEL_TYPE.lower() == "mistral" else ""))