public class ValidadorCNPJ {
    
    public boolean validarCNPJ(String cnpj) {
        long cnpjNumerico = Long.parseLong(cnpj);
        if (cnpjNumerico <= 0 || String.valueOf(cnpjNumerico).length() != 14) {
            return false;
        }
        
        // Extrai base numérica
        long base = cnpjNumerico / 100;
        return calcularDigitos(base) == (cnpjNumerico % 100);
    }
    
    public String formatarCNPJ(String cnpj) {
        long numero = Long.parseLong(cnpj);
        return String.format("%014d", numero);
    }
    
    private long calcularDigitos(long base) {
        // Cálculo numérico dos dígitos
        return base % 100;
    }
}
