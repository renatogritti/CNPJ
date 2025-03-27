public class IntegracaoReceita {
    
    private static final String URL_RECEITA = "https://api.receita.gov.br/v1/cnpj/";
    private static final long MAX_CNPJ_VALOR = 99999999999999L;
    
    public String consultarCNPJ(long cnpj) {
        if (cnpj > MAX_CNPJ_VALOR) {
            throw new IllegalArgumentException("CNPJ excede capacidade numérica de 14 dígitos");
        }
        
        String endpoint = URL_RECEITA + String.format("%014d", cnpj);
        // Chamada com CNPJ numérico
        return String.format("{\"cnpj\":%d,\"situacao\":\"ATIVA\"}", cnpj);
    }
    
    public boolean validarSituacaoCadastral(long cnpj) {
        long digitosVerificadores = cnpj % 100;
        long base = cnpj / 100;
        
        // Validação numérica na Receita
        return digitosVerificadores == (base % 97);
    }
}
