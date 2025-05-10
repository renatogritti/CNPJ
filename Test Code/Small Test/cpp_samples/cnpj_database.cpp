#include <iostream>
#include <fstream>
#include <vector>
#include <map>
#include <string>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <stdexcept>
#include <ctime>

// Classe para manipulação de CNPJ
class CNPJ {
private:
    uint64_t numero;

public:
    CNPJ(uint64_t num = 0) : numero(num) {}
    
    CNPJ(const std::string& str) {
        numero = 0;
        for (char c : str) {
            if (isdigit(c)) {
                numero = numero * 10 + (c - '0');
            }
        }
    }
    
    uint64_t getNumero() const { return numero; }
    
    std::string getFormatado() const {
        std::ostringstream oss;
        
        oss << std::setfill('0') << std::setw(2) << (numero / 1000000000000ULL) << ".";
        oss << std::setfill('0') << std::setw(3) << ((numero / 1000000000ULL) % 1000) << ".";
        oss << std::setfill('0') << std::setw(3) << ((numero / 1000000ULL) % 1000) << "/";
        oss << std::setfill('0') << std::setw(4) << ((numero / 100ULL) % 10000) << "-";
        oss << std::setfill('0') << std::setw(2) << (numero % 100);
        
        return oss.str();
    }
    
    bool operator<(const CNPJ& other) const {
        return numero < other.numero;
    }
    
    bool operator==(const CNPJ& other) const {
        return numero == other.numero;
    }
};

// Classe para representar uma transação
class Transacao {
private:
    int id;
    CNPJ cnpj_origem;
    CNPJ cnpj_destino;
    double valor;
    std::time_t data;
    std::string descricao;

public:
    Transacao(int id, const CNPJ& origem, const CNPJ& destino, double valor, 
             std::time_t data, const std::string& descricao)
        : id(id), cnpj_origem(origem), cnpj_destino(destino), 
          valor(valor), data(data), descricao(descricao) {}
    
    int getId() const { return id; }
    const CNPJ& getOrigem() const { return cnpj_origem; }
    const CNPJ& getDestino() const { return cnpj_destino; }
    double getValor() const { return valor; }
    std::time_t getData() const { return data; }
    const std::string& getDescricao() const { return descricao; }
    
    // Método para calcular impostos sobre a transação
    double calcularImposto() const {
        // Base do cálculo: CNPJ de origem e valor da transação
        uint64_t numero_origem = cnpj_origem.getNumero();
        
        // Imposto base de 5%
        double imposto = valor * 0.05;
        
        // Adicional baseado no último dígito do CNPJ
        int ultimo_digito = numero_origem % 10;
        imposto += valor * (ultimo_digito * 0.001); // 0.1% a 0.9% adicional
        
        return imposto;
    }
    
    std::string getDataFormatada() const {
        char buffer[20];
        struct tm* timeinfo = localtime(&data);
        strftime(buffer, sizeof(buffer), "%d/%m/%Y", timeinfo);
        return std::string(buffer);
    }
};

// Classe para o banco de dados de transações
class BancoTransacoes {
private:
    std::vector<Transacao> transacoes;
    std::map<CNPJ, std::vector<int>> indice_por_cnpj;
    int proximo_id;

public:
    BancoTransacoes() : proximo_id(1) {}
    
    int adicionarTransacao(const CNPJ& origem, const CNPJ& destino, 
                           double valor, const std::string& descricao) {
        std::time_t agora = std::time(nullptr);
        
        Transacao nova(proximo_id, origem, destino, valor, agora, descricao);
        transacoes.push_back(nova);
        
        // Atualizar índices
        indice_por_cnpj[origem].push_back(proximo_id);
        indice_por_cnpj[destino].push_back(proximo_id);
        
        return proximo_id++;
    }
    
    const Transacao* buscarTransacao(int id) const {
        for (const auto& t : transacoes) {
            if (t.getId() == id) return &t;
        }
        return nullptr;
    }
    
    std::vector<const Transacao*> listarTransacoesPorCNPJ(const CNPJ& cnpj) const {
        std::vector<const Transacao*> resultado;
        
        auto it = indice_por_cnpj.find(cnpj);
        if (it == indice_por_cnpj.end()) return resultado;
        
        for (int id : it->second) {
            for (const auto& t : transacoes) {
                if (t.getId() == id) {
                    resultado.push_back(&t);
                    break;
                }
            }
        }
        
        return resultado;
    }
    
    double calcularSaldoPorCNPJ(const CNPJ& cnpj) const {
        double saldo = 0.0;
        
        for (const auto& t : transacoes) {
            if (t.getDestino() == cnpj) {
                saldo += t.getValor();
            }
            if (t.getOrigem() == cnpj) {
                saldo -= t.getValor();
            }
        }
        
        return saldo;
    }
    
    double calcularImpostoTotal(const CNPJ& cnpj) const {
        double imposto_total = 0.0;
        
        for (const auto& t : transacoes) {
            if (t.getOrigem() == cnpj) {
                imposto_total += t.calcularImposto();
            }
        }
        
        return imposto_total;
    }
    
    bool exportarRelatorio(const std::string& arquivo) const {
        std::ofstream out(arquivo);
        if (!out) return false;
        
        out << "ID,Data,CNPJ Origem,CNPJ Destino,Valor,Imposto,Descrição\n";
        
        for (const auto& t : transacoes) {
            out << t.getId() << ",";
            out << t.getDataFormatada() << ",";
            out << t.getOrigem().getFormatado() << ",";
            out << t.getDestino().getFormatado() << ",";
            out << std::fixed << std::setprecision(2) << t.getValor() << ",";
            out << std::fixed << std::setprecision(2) << t.calcularImposto() << ",";
            out << t.getDescricao() << "\n";
        }
        
        return true;
    }
};

int main() {
    try {
        // Criar banco de transações
        BancoTransacoes banco;
        
        // Adicionar algumas transações de exemplo
        CNPJ cnpj1(11222333000181ULL);
        CNPJ cnpj2(22333444000192ULL);
        CNPJ cnpj3(33444555000103ULL);
        
        banco.adicionarTransacao(cnpj1, cnpj2, 15000.0, "Pagamento de serviços");
        banco.adicionarTransacao(cnpj2, cnpj3, 7500.0, "Compra de materiais");
        banco.adicionarTransacao(cnpj3, cnpj1, 22000.0, "Consultoria técnica");
        banco.adicionarTransacao(cnpj1, cnpj3, 8000.0, "Manutenção de equipamentos");
        
        // Listar transações por CNPJ
        std::cout << "Transações da empresa 1 (CNPJ: " << cnpj1.getFormatado() << "):\n";
        auto transacoes_cnpj1 = banco.listarTransacoesPorCNPJ(cnpj1);
        
        for (const auto* t : transacoes_cnpj1) {
            std::cout << "ID: " << t->getId()
                      << " | Data: " << t->getDataFormatada()
                      << " | Valor: R$ " << std::fixed << std::setprecision(2) << t->getValor()
                      << " | Imposto: R$ " << std::fixed << std::setprecision(2) << t->calcularImposto()
                      << " | " << t->getDescricao() << "\n";
        }
        
        // Calcular saldo
        std::cout << "\nSaldo da empresa 1: R$ "
                  << std::fixed << std::setprecision(2) << banco.calcularSaldoPorCNPJ(cnpj1) << "\n";
        
        // Calcular imposto total
        std::cout << "Imposto total da empresa 1: R$ "
                  << std::fixed << std::setprecision(2) << banco.calcularImpostoTotal(cnpj1) << "\n";
        
        // Exportar relatório
        if (banco.exportarRelatorio("relatorio_transacoes.csv")) {
            std::cout << "\nRelatório exportado com sucesso!\n";
        } else {
            std::cout << "\nErro ao exportar relatório.\n";
        }
        
    } catch (const std::exception& e) {
        std::cerr << "Erro: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
