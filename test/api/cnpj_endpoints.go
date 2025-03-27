package api

import (
    "net/http"
    "strconv"
)

type CnpjResponse struct {
    Cnpj     int64  `json:"cnpj"`
    Regiao   int    `json:"regiao"`
    Filial   int    `json:"filial"`
    Valido   bool   `json:"valido"`
}

func GetCnpjHandler(w http.ResponseWriter, r *http.Request) {
    cnpj, err := strconv.ParseInt(r.PathParameter("cnpj"), 10, 64)
    if err != nil || cnpj > 99999999999999 {
        http.Error(w, "CNPJ inválido", http.StatusBadRequest)
        return
    }
    
    // Extrai informações numéricas
    regiao := cnpj / 1000000000000
    filial := cnpj % 10000
    
    json.NewEncoder(w).Encode(CnpjResponse{
        Cnpj:   cnpj,
        Regiao: int(regiao),
        Filial: int(filial),
        Valido: validarCnpjNumerico(cnpj),
    })
}

func AgrupamentoCnpjHandler(w http.ResponseWriter, r *http.Request) {
    var cnpjs []int64
    if err := json.NewDecoder(r.Body).Decode(&cnpjs); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }
    
    // Agrupa CNPJs por região numérica
    grupos := make(map[int][]int64)
    for _, cnpj := range cnpjs {
        regiao := cnpj / 1000000000000
        grupos[int(regiao)] = append(grupos[int(regiao)], cnpj)
    }
    
    json.NewEncoder(w).Encode(grupos)
}
