from .AiModelInterface import AIModelInterface
import anthropic

# Implementação para Anthropic Claude
class AnthropicModel(AIModelInterface):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def analyze_code(self, prompt: str, language: str, code: str, context_extra: str = "") -> str:
        message = self.client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            temperature=0,
            system="Você é um analisador de código que responde APENAS com JSON válido em uma única linha, sem formatação ou textos adicionais.",
            messages=[
                {
                    "role": "user",
                    "content": prompt.format(language=language, code=code + context_extra)
                }
            ]
        )
        return message.content[0].text