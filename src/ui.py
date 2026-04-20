import json
from pathlib import Path

from db_oracle import buscar_colheitas_oracle, inserir_colheitas_oracle
from servicos import (
    calcular_producao_esperada,
    calcular_perda,
    carregar_talhoes_json,
    classificar_perda,
    gerar_tabela_memoria,
    montar_resumo,
    registrar_log_texto,
)

BASE_DIR = Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"

TALHOES_JSON = DADOS_DIR / "talhoes_iniciais.json"
HISTORICO_JSON = DADOS_DIR / "historico_colheitas.json"
LOG_TXT = DADOS_DIR / "log_operacoes.txt"
RELATORIO_TXT = DADOS_DIR / "relatorio_resumo.txt"


def iniciar_menu():
    talhoes = carregar_talhoes_json(TALHOES_JSON)
    colheitas = []

    while True:
        print("\n" + "=" * 30)
        print("   SISTEMA DE COLHEITA")
        print("=" * 30)
        print("1 - Listar talhões")
        print("2 - Registrar colheita")
        print("3 - Ver resumo")
        print("4 - Exportar resumo TXT")
        print("5 - Salvar histórico JSON")
        print("6 - Enviar para Oracle")
        print("0 - Sair")

        opcao = ler_inteiro("Escolha: ", 0, 6)

        try:
            match opcao:
                case 1:
                    listar_talhoes(talhoes)
                    pausar()

                case 2:
                    registrar_colheita(talhoes, colheitas)
                    pausar()

                case 3:
                    registros = buscar_registros(colheitas)
                    exibir_resumo(registros)
                    pausar()

                case 4:
                    registros = buscar_registros(colheitas)
                    exportar_resumo(registros)
                    pausar()

                case 5:
                    salvar_json(colheitas)
                    pausar()

                case 6:
                    enviar_oracle(colheitas)
                    pausar()

                case 0:
                    print("Encerrando...")
                    break

        except Exception as e:
            print(f"Erro: {e}")
            pausar()

# ======================
# FUNÇÕES AUXILIARES UI
# ======================

def ler_inteiro(msg, min=None, max=None):
    while True:
        try:
            valor = int(input(msg))
            if min is not None and valor < min:
                continue
            if max is not None and valor > max:
                continue
            return valor
        except:
            print("Entrada inválida")


def pausar():
    input("\nPressione ENTER...")


def listar_talhoes(talhoes):
    for t in talhoes:
        esperado = calcular_producao_esperada(t)
        print(f"{t['id']} - {t['nome']} | {esperado:.2f} t")


def registrar_colheita(talhoes, colheitas):
    listar_talhoes(talhoes)
    id_escolhido = ler_inteiro("ID: ")

    talhao = next(t for t in talhoes if t["id"] == id_escolhido)
    colhido = float(input("Toneladas: ").replace(",", "."))

    esperado = calcular_producao_esperada(talhao)
    perda = calcular_perda(esperado, colhido)

    registro = {
        "talhao_id": talhao["id"],
        "talhao_nome": talhao["nome"],
        "esperado_t": round(esperado, 2),
        "colhido_t": round(colhido, 2),
        "perda_percentual": round(perda, 2),
        "classificacao": classificar_perda(perda),
        "enviado_oracle": False,
    }

    colheitas.append(registro)
    registrar_log_texto("Registro criado", LOG_TXT)

    print(f"Perda: {perda:.2f}% ({registro['classificacao']})")


def buscar_registros(memoria):
    try:
        oracle = buscar_colheitas_oracle()
        pendentes = [c for c in memoria if not c["enviado_oracle"]]
        return oracle + pendentes
    except:
        return memoria


def exibir_resumo(colheitas):
    resumo = montar_resumo(colheitas)
    print("\nResumo:")
    print(resumo)


def exportar_resumo(colheitas):
    resumo = montar_resumo(colheitas)
    tabela = gerar_tabela_memoria(colheitas)

    texto = f"Resumo: {resumo}\nTabela: {tabela}"
    RELATORIO_TXT.write_text(texto)

    print("Exportado!")


def salvar_json(colheitas):
    with HISTORICO_JSON.open("w", encoding="utf-8") as f:
        json.dump(colheitas, f, indent=2)

    print("Salvo!")


def enviar_oracle(colheitas):
    pendentes = [c for c in colheitas if not c["enviado_oracle"]]
    qtd = inserir_colheitas_oracle(pendentes)

    for c in pendentes:
        c["enviado_oracle"] = True

    print(f"{qtd} enviados!")