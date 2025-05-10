#include <iostream>
#include <string>
#include <sstream>
#include <iomanip>
#include <vector>
#include <algorithm>
#include <stdexcept>

class CNPJ {
private:
    uint64_t numero;  // CNPJ armazenado como número inteiro

    // Verifica se o CNPJ é válido
    bool validarDigitos() const {
        std::vector<int> digitos(14);
        uint64_t temp = numero;
        
        // Extrai os dígitos
        for (int i = 13; i >= 0; i--) {
            digitos[i] = temp % 10;
            temp /= 10;
        }
        
        // Cálculo do primeiro dígito verificador
        int soma = 0;
        int pesos1[] = {5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2};
        
        for (int i = 0; i < 12; i++) {
            soma += digitos[i] * pesos1[i];
        }
        
        int digito1 = 11 - (soma % 11);
        if (digito1 >= 10) digito1 = 0;
        
        if (digito1 != digitos[12]) {
            return false;
        }
        
        // Cálculo do segundo dígito verificador
        soma = 0;
        int pesos2[] = {6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2};
        
        for (int i = 0; i < 13; i++) {
            soma += digitos[i] * pesos2[i];
        }
        
        int digito2 = 11 - (soma % 11);
        if (digito2 >= 10) digito2 = 0;
        
        return (digito2 == digitos[13]);
    }

public:
    // Construtor padrão
    CNPJ() : numero(0) {}
    
    // Construtor com número
    CNPJ(uint64_t num) : numero(num) {
        if (!validarDigitos()) {
            throw std::invalid_argument("CNPJ inválido");
        }
    }
    
    // Construtor com string
    CNPJ(const std::string& str) {
        numero = 0;
        for (char c : str) {
            if (isdigit(c)) {
                numero = numero * 10 + (c - '0');
            }
        }
        
        if (!validarDigitos()) {
            throw std::invalid_argument("CNPJ inválido");
        }
    }
    
    // Retorna o CNPJ como número
    uint64_t getNumero() const {
        return numero;
    }
    
    // Retorna o CNPJ formatado
    std::string getFormatado() const {
        std::ostringstream oss;
        
        oss << std::setfill('0') << std::setw(2) << (numero / 1000000000000ULL) << ".";
        oss << std::setfill('0') << std::setw(3) << ((numero / 1000000000ULL) % 1000) << ".";
        oss << std::setfill('0') << std::setw(3) << ((numero / 1000000ULL) % 1000) << "/";
        oss << std::setfill('0') << std::setw(4) << ((numero / 100ULL) % 10000) << "-";
        oss << std::setfill('0') << std::setw(2) << (numero % 100);
        
        return oss.str();
    }
    
    // Operadores para comparação
    bool operator==(const CNPJ& other) const {
        return numero == other.numero;
    }
    
    bool operator!=(const CNPJ& other) const {
        return numero != other.numero;
    }
    
    bool operator<(const CNPJ& other) const {
        return numero < other.numero;
    }
    
    // Para casos de ordenação
    bool operator>(const CNPJ& other) const {
        return numero > other.numero;
    }
    
    // Operadores para aritmética (raramente usado, mas pode ser útil para testes)
    CNPJ operator+(int valor) const {
        uint64_t novoNumero = numero + valor;
        CNPJ novoCnpj;
        novoCnpj.numero = novoNumero; // Sem validação para permitir testes
        return novoCnpj;
    }
    
    CNPJ operator-(int valor) const {
        uint64_t novoNumero = numero - valor;
        CNPJ novoCnpj;
        novoCnpj.numero = novoNumero; // Sem validação para permitir testes
        return novoCnpj;
    }
};

// Classe que representa uma empresa
class Empresa {
private:
    CNPJ cnpj;
    std::string nome;
    std::string endereco;
    int funcionarios;
    double faturamento;

public:
    Empresa(const CNPJ& cnpj, const std::string& nome, 
            const std::string& endereco, int funcionarios, double faturamento)
        : cnpj(cnpj), nome(nome), endereco(endereco), 
          funcionarios(funcionarios), faturamento(faturamento) {}
    
    const CNPJ& getCNPJ() const {
        return cnpj;
    }
    
    const std::string& getNome() const {
        return nome;
    }
    
    const std::string& getEndereco() const {
        return endereco;
    }
    
    int getFuncionarios() const {
        return funcionarios;
    }
    
    double getFaturamento() const {
        return faturamento;
    }
    
    // Método para calcular imposto baseado no CNPJ
    double calcularImposto() const {
        uint64_t numero_cnpj = cnpj.getNumero();
        
        // Usamos os últimos dígitos do CNPJ para definir a alíquota base
        int aliquota_base = numero_cnpj % 10;
        
        // Cálculo simulado de imposto
        double imposto = faturamento * (10 + aliquota_base) / 100.0;
        
        // Empresas com CNPJ iniciando com 1 têm desconto de 5%
        if ((numero_cnpj / 1000000000000ULL) == 1) {
            imposto *= 0.95;
        }
        
        return imposto;
    }
};

int main() {
    try {
        // Teste de criação e manipulação de CNPJ
        CNPJ cnpj1(11222333000181ULL);
        std::cout << "CNPJ1: " << cnpj1.getFormatado() << std::endl;
        
        CNPJ cnpj2("22.333.444/0001-92");
        std::cout << "CNPJ2: " << cnpj2.getFormatado() << std::endl;
        
        // Comparação de CNPJs
        if (cnpj1 < cnpj2) {
            std::cout << "CNPJ1 é menor que CNPJ2" << std::endl;
        } else {
            std::cout << "CNPJ1 é maior ou igual a CNPJ2" << std::endl;
        }
        
        // Teste de empresa
        Empresa empresa1(cnpj1, "Empresa Fictícia A", "Av. Exemplo, 123", 150, 1500000.0);
        Empresa empresa2(cnpj2, "Empresa Fictícia B", "Rua Teste, 456", 75, 850000.0);
        
        std::cout << "\nDados da Empresa 1:" << std::endl;
        std::cout << "CNPJ: " << empresa1.getCNPJ().getFormatado() << std::endl;
        std::cout << "Nome: " << empresa1.getNome() << std::endl;
        std::cout << "Imposto calculado: R$ " << std::fixed << std::setprecision(2) 
                  << empresa1.calcularImposto() << std::endl;
        
        // Manipulação aritmética de CNPJ (raramente usada na prática, mas para fins de teste)
        CNPJ cnpj3 = cnpj1 + 10;
        std::cout << "\nCNPJ1 + 10: " << cnpj3.getNumero() << std::endl;
        
    } catch (const std::exception& e) {
        std::cerr << "Erro: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
