#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Estrutura que representa uma empresa
typedef struct {
    unsigned long long cnpj;  // CNPJ como número (14 dígitos numéricos)
    char nome[100];
    char endereco[200];
    int funcionarios;
    double faturamento;
} Empresa;

// Base de dados simulada (array de empresas)
#define MAX_EMPRESAS 1000
Empresa* banco_dados[MAX_EMPRESAS];
int num_empresas = 0;

// Adiciona uma empresa ao banco de dados
int adicionarEmpresa(Empresa* empresa) {
    if (num_empresas >= MAX_EMPRESAS) {
        return 0; // Banco de dados cheio
    }
    
    // Verifica se o CNPJ já existe
    for (int i = 0; i < num_empresas; i++) {
        if (banco_dados[i]->cnpj == empresa->cnpj) {
            return 0; // CNPJ duplicado
        }
    }
    
    banco_dados[num_empresas++] = empresa;
    return 1; // Sucesso
}

// Busca uma empresa pelo CNPJ
Empresa* buscarPorCnpj(unsigned long long cnpj) {
    for (int i = 0; i < num_empresas; i++) {
        if (banco_dados[i]->cnpj == cnpj) {
            return banco_dados[i];
        }
    }
    return NULL; // Não encontrado
}

// Calcula imposto baseado no CNPJ e faturamento
double calcularImposto(unsigned long long cnpj, double faturamento) {
    // Usamos os últimos dígitos do CNPJ para definir a alíquota base
    int aliquota_base = cnpj % 10;
    
    // Cálculo simulado de imposto
    double imposto = faturamento * (10 + aliquota_base) / 100.0;
    
    // Empresas com CNPJ iniciando com 1 têm desconto de 5%
    if ((cnpj / 1000000000000ULL) == 1) {
        imposto *= 0.95;
    }
    
    return imposto;
}

// Exporta relatório de empresas para arquivo CSV
void exportarRelatorio(const char* arquivo) {
    FILE* f = fopen(arquivo, "w");
    if (!f) {
        printf("Erro ao abrir arquivo para escrita\n");
        return;
    }
    
    // Cabeçalho do CSV
    fprintf(f, "CNPJ,Nome,Funcionarios,Faturamento,Imposto\n");
    
    for (int i = 0; i < num_empresas; i++) {
        Empresa* e = banco_dados[i];
        
        // Calcula o imposto
        double imposto = calcularImposto(e->cnpj, e->faturamento);
        
        // Formata CNPJ como 00.000.000/0000-00
        fprintf(f, "%02llu.%03llu.%03llu/%04llu-%02llu,%s,%d,%.2f,%.2f\n",
                e->cnpj / 1000000000000ULL,
                (e->cnpj / 1000000000ULL) % 1000,
                (e->cnpj / 1000000ULL) % 1000,
                (e->cnpj / 100ULL) % 10000,
                e->cnpj % 100,
                e->nome,
                e->funcionarios,
                e->faturamento,
                imposto);
    }
    
    fclose(f);
    printf("Relatório exportado com sucesso!\n");
}

int main() {
    // Adicionar algumas empresas de exemplo
    Empresa* e1 = malloc(sizeof(Empresa));
    e1->cnpj = 11222333000181;
    strcpy(e1->nome, "Empresa Fictícia A");
    strcpy(e1->endereco, "Av. Exemplo, 123");
    e1->funcionarios = 150;
    e1->faturamento = 1500000.0;
    adicionarEmpresa(e1);
    
    Empresa* e2 = malloc(sizeof(Empresa));
    e2->cnpj = 22333444000192;
    strcpy(e2->nome, "Empresa Fictícia B");
    strcpy(e2->endereco, "Rua Teste, 456");
    e2->funcionarios = 75;
    e2->faturamento = 850000.0;
    adicionarEmpresa(e2);
    
    // Buscar e exibir dados de uma empresa
    unsigned long long cnpj_busca = 11222333000181;
    Empresa* encontrada = buscarPorCnpj(cnpj_busca);
    
    if (encontrada) {
        printf("Empresa encontrada:\n");
        printf("CNPJ: %llu\n", encontrada->cnpj);
        printf("Nome: %s\n", encontrada->nome);
        printf("Funcionários: %d\n", encontrada->funcionarios);
        printf("Faturamento: R$ %.2f\n", encontrada->faturamento);
        
        double imposto = calcularImposto(encontrada->cnpj, encontrada->faturamento);
        printf("Imposto calculado: R$ %.2f\n", imposto);
    } else {
        printf("Empresa com CNPJ %llu não encontrada\n", cnpj_busca);
    }
    
    // Exportar relatório
    exportarRelatorio("relatorio_empresas.csv");
    
    // Liberar memória
    for (int i = 0; i < num_empresas; i++) {
        free(banco_dados[i]);
    }
    
    return 0;
}
