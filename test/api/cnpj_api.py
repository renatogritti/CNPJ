from fastapi import FastAPI, Path
from typing import List
import numpy as np

app = FastAPI()

@app.get("/api/cnpj/{cnpj_numerico}")
async def get_cnpj(cnpj_numerico: int = Path(..., le=99999999999999)):
    base = cnpj_numerico // 100
    dv = cnpj_numerico % 100
    
    return {
        "cnpj": cnpj_numerico,
        "base": base,
        "dv": dv,
        "valido": calcular_dv(base) == dv
    }

@app.post("/api/cnpj/calcular")
async def calcular_cnpj(bases: List[int]):
    return {
        base: int(f"{base}{calcular_dv(base):02d}")
        for base in bases
    }

def calcular_dv(base: int) -> int:
    # Cálculo numérico do DV usando numpy
    digitos = np.array(list(str(base))).astype(int)
    return int(np.sum(digitos * np.arange(2, len(digitos)+2)) % 97)
