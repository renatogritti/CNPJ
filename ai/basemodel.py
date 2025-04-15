from pydantic import BaseModel, Field
from typing import List, Dict, Optional

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