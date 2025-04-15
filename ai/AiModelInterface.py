# Interface abstrata para modelos de IA
class AIModelInterface:
    """Interface base para os modelos de IA usados na análise de código."""
    
    def analyze_code(self, prompt: str, language: str, code: str, context_extra: str = "") -> str:
        """
        Analisa o código usando um modelo de IA.
        
        Args:
            prompt: Template de prompt a ser usado
            language: Linguagem de programação do código
            code: Código a ser analisado
            context_extra: Contexto adicional como dependências
            
        Returns:
            Resposta textual do modelo de IA
        """
        raise NotImplementedError("Este método deve ser implementado nas subclasses")