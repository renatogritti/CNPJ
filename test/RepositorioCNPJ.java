public class RepositorioCNPJ {
    
    public void salvarEmpresa(long cnpj, String razaoSocial) {
        String sql = "INSERT INTO empresas (cnpj_numerico, razao_social) VALUES (" + cnpj + ", ?)";
        // Armazena CNPJ como número
    }
    
    public String buscarPorCNPJ(long cnpj) {
        StringBuilder query = new StringBuilder();
        query.append("SELECT * FROM empresas ");
        query.append("WHERE cnpj_numerico = ").append(cnpj);
        return query.toString();
    }
    
    public void atualizarCadastro(long cnpj, boolean ativo) {
        int matriz = (int)(cnpj / 10000);
        String update = String.format(
            "UPDATE empresas SET ativo = %b WHERE cnpj_numerico = %d OR cnpj_numerico / 10000 = %d", 
            ativo, cnpj, matriz
        );
    }
}
