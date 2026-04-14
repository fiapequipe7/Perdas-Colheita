from __future__ import annotations

import os

## Importar Oracle DB
try:
    import oracledb
except ImportError as erro:  # pragma: no cover
    oracledb = None
    IMPORT_ERROR = erro
else:
    IMPORT_ERROR = None


## Definir dados para acesso ao banco

ORACLE_USER_FIXO = "RM570379"
ORACLE_PASSWORD_FIXA = "300484"
ORACLE_HOST_FIXO = "oracle.fiap.com.br"
ORACLE_PORTA_FIXA = "1521"
ORACLE_SID_FIXO = "ORCL"

## Conectar ao Banco de Dados

def _obter_conexao_oracle():
    if oracledb is None:
        raise RuntimeError(
            "Biblioteca oracledb nao instalada. Rode: pip install -r requirements.txt"
        ) from IMPORT_ERROR

    usuario = os.getenv("ORACLE_USER", ORACLE_USER_FIXO)
    senha = os.getenv("ORACLE_PASSWORD", ORACLE_PASSWORD_FIXA)
    dsn = _obter_dsn_oracle()


    if not usuario or not senha:
        raise RuntimeError(
            "Configure as variaveis ORACLE_USER e ORACLE_PASSWORD."
        )

    return oracledb.connect(user=usuario, password=senha, dsn=dsn)


def _obter_dsn_oracle() -> str:
    dsn_direto = os.getenv("ORACLE_DSN")
    if dsn_direto:
        return dsn_direto

    host = os.getenv("ORACLE_HOST", ORACLE_HOST_FIXO)
    porta = os.getenv("ORACLE_PORT", ORACLE_PORTA_FIXA)
    sid = os.getenv("ORACLE_SID", ORACLE_SID_FIXO)
    service_name = os.getenv("ORACLE_SERVICE_NAME")

    if host and sid:
        return (
            f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={porta}))"
            f"(CONNECT_DATA=(SID={sid})))"
        )

    if host and service_name:
        return (
            f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={porta}))"
            f"(CONNECT_DATA=(SERVICE_NAME={service_name})))"
        )

    raise RuntimeError(
        "Configure ORACLE_DSN ou ORACLE_HOST + ORACLE_PORT + ORACLE_SID "
        "(ou ORACLE_SERVICE_NAME)."
    )

##  Tabela
def _garantir_tabela(cursor) -> None:
    cursor.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE '
                CREATE TABLE colheitas_cana (
                    id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    talhao_id NUMBER NOT NULL,
                    talhao_nome VARCHAR2(120) NOT NULL,
                    esperado_t NUMBER(10,2) NOT NULL,
                    colhido_t NUMBER(10,2) NOT NULL,
                    perda_percentual NUMBER(5,2) NOT NULL,
                    classificacao VARCHAR2(20) NOT NULL,
                    dt_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ';
        EXCEPTION
            WHEN OTHERS THEN
                IF SQLCODE != -955 THEN
                    RAISE;
                END IF;
        END;
        """
    )

#Inserir Tabela

def inserir_colheitas_oracle(colheitas: list[dict]) -> int:
    if not colheitas:
        return 0

    with _obter_conexao_oracle() as conexao:
        with conexao.cursor() as cursor:
            _garantir_tabela(cursor)

            dados = [
                (
                    item["talhao_id"],
                    item["talhao_nome"],
                    item["esperado_t"],
                    item["colhido_t"],
                    item["perda_percentual"],
                    item["classificacao"],
                )
                for item in colheitas
            ]

            cursor.executemany(
                """
                INSERT INTO colheitas_cana
                    (talhao_id, talhao_nome, esperado_t, colhido_t, perda_percentual, classificacao)
                VALUES
                    (:1, :2, :3, :4, :5, :6)
                """,
                dados,
            )
        conexao.commit()

    return len(colheitas)

##Consultar Tabela

def buscar_colheitas_oracle() -> list[dict]:
    with _obter_conexao_oracle() as conexao:
        with conexao.cursor() as cursor:
            _garantir_tabela(cursor)
            cursor.execute(
                """
                SELECT
                    talhao_id,
                    talhao_nome,
                    esperado_t,
                    colhido_t,
                    perda_percentual,
                    classificacao
                FROM colheitas_cana
                ORDER BY id DESC
                """
            )
            linhas = cursor.fetchall()

    return [
        {
            "talhao_id": int(linha[0]),
            "talhao_nome": str(linha[1]),
            "esperado_t": float(linha[2]),
            "colhido_t": float(linha[3]),
            "perda_percentual": float(linha[4]),
            "classificacao": str(linha[5]),
        }
        for linha in linhas
    ]
