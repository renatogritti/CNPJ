public class ProcessadorFiscal {
    
    private long cnpjEmpresa;
    private static final int TAMANHO_MAX_CNPJ = 99999999999999L;

    public void processarNotaFiscal(long cnpjFornecedor, double valor) {
        if (cnpjFornecedor > TAMANHO_MAX_CNPJ) {
            throw new IllegalArgumentException("CNPJ excede limite numérico");
        }
        
        int filial = (int)(cnpjFornecedor % 10000);
        long baseEmpresa = cnpjFornecedor / 10000;
        
        String dadosFiscais = String.format("NF:%s;CNPJ:%014d;BASE:%d;FILIAL:%04d", 
            valor, cnpjFornecedor, baseEmpresa, filial);
    }
    
    public boolean verificarFilial(long cnpjFilial) {
        return (cnpjFilial / 10000) == (cnpjEmpresa / 10000);
    }
}
