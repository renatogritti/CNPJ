function validarFormulario() {
    const cnpj = document.getElementById('cnpj').value;
    const matrizCnpj = document.getElementById('matrizCnpj').value;

    if (cnpj.length !== 14) {
        alert('CNPJ deve ter 14 dígitos');
        return false;
    }

    if (matrizCnpj) {
        // Verifica se é filial da matriz (8 primeiros dígitos iguais)
        if (Math.floor(cnpj / 10000) !== Math.floor(matrizCnpj / 10000)) {
            alert('CNPJ não pertence à matriz informada');
            return false;
        }
    }

    return calcularDigitosVerificadores(cnpj);
}

function formatarCNPJ(input) {
    let valor = input.value.replace(/\D/g, '');
    if (valor.length > 14) valor = valor.substr(0, 14);
    
    // Mantém apenas números
    input.value = valor;
}

function calcularDigitosVerificadores(cnpj) {
    const base = Math.floor(cnpj / 100);
    const digitosInformados = cnpj % 100;
    
    // Simulação de cálculo numérico dos dígitos
    return (base % 100) === digitosInformados;
}
