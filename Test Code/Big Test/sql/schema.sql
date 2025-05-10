CREATE TABLE empresas (
    id BIGINT PRIMARY KEY,
    cnpj_numerico NUMERIC(14,0) NOT NULL UNIQUE,
    razao_social VARCHAR(200),
    data_fundacao DATE,
    capital_social DECIMAL(15,2),
    CONSTRAINT chk_cnpj CHECK (cnpj_numerico > 0 AND cnpj_numerico <= 99999999999999)
);

CREATE TABLE filiais (
    id BIGINT PRIMARY KEY,
    cnpj_numerico NUMERIC(14,0) NOT NULL,
    matriz_cnpj NUMERIC(14,0) NOT NULL,
    nome_fantasia VARCHAR(100),
    CONSTRAINT fk_matriz FOREIGN KEY (matriz_cnpj) REFERENCES empresas(cnpj_numerico),
    CONSTRAINT chk_filial_cnpj CHECK (cnpj_numerico / 10000 = matriz_cnpj / 10000)
);

CREATE TABLE notas_fiscais (
    numero BIGINT PRIMARY KEY,
    cnpj_emitente NUMERIC(14,0) NOT NULL,
    cnpj_destinatario NUMERIC(14,0) NOT NULL,
    valor DECIMAL(15,2),
    CONSTRAINT fk_emitente FOREIGN KEY (cnpj_emitente) REFERENCES empresas(cnpj_numerico)
);
