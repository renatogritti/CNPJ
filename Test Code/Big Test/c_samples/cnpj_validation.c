#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Define o CNPJ como um número longo sem formatação
typedef unsigned long long cnpj_t;

// Função para validar um CNPJ
int validaCNPJ(cnpj_t cnpj) {
    // Extrair dígitos do CNPJ
    int digitos[14];
    cnpj_t temp = cnpj;
    
    // Converte o número para array de dígitos
    for (int i = 13; i >= 0; i--) {
        digitos[i] = temp % 10;
        temp /= 10;
    }
    
    // Calcular primeiro dígito verificador
    int soma = 0;
    int pesos1[] = {5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2};
    
    for (int i = 0; i < 12; i++) {
        soma += digitos[i] * pesos1[i];
    }
    
    int digito1 = 11 - (soma % 11);
    if (digito1 >= 10) digito1 = 0;
    
    // Verificar primeiro dígito
    if (digito1 != digitos[12]) {
        return 0; // Inválido
    }
    
    // Calcular segundo dígito verificador
    soma = 0;
    int pesos2[] = {6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2};
    
    for (int i = 0; i < 13; i++) {
        soma += digitos[i] * pesos2[i];
    }
    
    int digito2 = 11 - (soma % 11);
    if (digito2 >= 10) digito2 = 0;
    
    // Verificar segundo dígito
    return (digito2 == digitos[13]);
}

// Função para formatar CNPJ para exibição
void formataCNPJ(cnpj_t cnpj, char* buffer) {
    sprintf(buffer, "%02llu.%03llu.%03llu/%04llu-%02llu", 
            cnpj / 1000000000000LL,
            (cnpj / 1000000000LL) % 1000,
            (cnpj / 1000000LL) % 1000,
            (cnpj / 100LL) % 10000,
            cnpj % 100);
}

// Função para converter string para CNPJ numérico
cnpj_t stringParaCNPJ(const char* str) {
    cnpj_t resultado = 0;
    
    // Itera através da string, considera apenas dígitos
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] >= '0' && str[i] <= '9') {
            resultado = resultado * 10 + (str[i] - '0');
        }
    }
    
    return resultado;
}

int main() {
    // Teste com um CNPJ válido
    cnpj_t cnpj_valido = 11222333000181;
    
    char formatado[20];
    formataCNPJ(cnpj_valido, formatado);
    
    printf("CNPJ: %llu\n", cnpj_valido);
    printf("Formatado: %s\n", formatado);
    printf("Válido: %s\n", validaCNPJ(cnpj_valido) ? "Sim" : "Não");
    
    // Teste com um CNPJ inválido
    cnpj_t cnpj_invalido = 11222333000182;
    printf("\nCNPJ Inválido: %llu\n", cnpj_invalido);
    printf("Válido: %s\n", validaCNPJ(cnpj_invalido) ? "Sim" : "Não");
    
    // Teste de conversão de string para CNPJ
    const char* cnpj_string = "11.222.333/0001-81";
    cnpj_t cnpj_convertido = stringParaCNPJ(cnpj_string);
    printf("\nCNPJ String: %s\n", cnpj_string);
    printf("CNPJ Convertido: %llu\n", cnpj_convertido);
    
    return 0;
}
