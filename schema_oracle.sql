CREATE TABLE colheitas_cana (
    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    talhao_id NUMBER NOT NULL,
    talhao_nome VARCHAR2(120) NOT NULL,
    esperado_t NUMBER(10,2) NOT NULL,
    colhido_t NUMBER(10,2) NOT NULL,
    perda_percentual NUMBER(5,2) NOT NULL,
    classificacao VARCHAR2(20) NOT NULL,
    dt_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
