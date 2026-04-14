import json
from pathlib import Path

from db_oracle import buscar_colheitas_oracle, inserir_colheitas_oracle
from servicos import (
    calcular_producao_esperada,
    carregar_talhoes_json,
    classificar_perda,
    gerar_tabela_memoria,
    montar_resumo,
    registrar_log_texto,
)
##Definir
BASE_DIR = Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"
TALHOES_JSON = DADOS_DIR / "talhoes_iniciais.json"
HISTORICO_JSON = DADOS_DIR / "historico_colheitas.json"
LOG_TXT = DADOS_DIR / "log_operacoes.txt"
RELATORIO_TXT = DADOS_DIR / "relatorio_resumo.txt"

## Criação do Menu
def procedimento_exibir_menu() -> None:
    print("\n=== COLHEITA DE CANA ===")
    print("1 - Listar talhoes")
    print("2 - Registrar colheita")
    print("3 - Ver resumo (busca no Oracle)")
    print("4 - Exportar resumo em TXT")
    print("5 - Salvar historico em JSON")
    print("6 - Enviar registros para Oracle")
    print("0 - Sair")


def pausar_tela() -> None:
    input("\nPressione ENTER para voltar ao menu...")

## Input Menu
def ler_inteiro(mensagem: str, minimo: int | None = None, maximo: int | None = None) -> int | None:
    while True:
        entrada = input(mensagem).strip()
        if not entrada.isdigit():
            print("Entrada invalida. Digite apenas numeros inteiros.")
            continue

        valor = int(entrada)
        if minimo is not None and valor < minimo:
            print(f"Digite um valor maior ou igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"Digite um valor menor ou igual a {maximo}.")
            continue
        return valor


def ler_float_positivo(mensagem: str) -> float | None:
    while True:
        entrada = input(mensagem).strip().replace(",", ".")
        try:
            valor = float(entrada)
        except ValueError:
            print("Valor invalido. Use apenas numeros.")
            continue

        if valor <= 0:
            print("Digite um numero maior que zero.")
            continue
        return valor


def listar_talhoes(talhoes: list[dict]) -> None:
    print("\nTalhoes cadastrados:")
    if not talhoes:
        print("Nenhum talhao cadastrado.")
        return

    for talhao in talhoes:
        esperado = calcular_producao_esperada(talhao)
        print(
            f"ID {talhao['id']}: {talhao['nome']} | "
            f"{talhao['hectares']} ha | "
            f"{talhao['produtividade_esperada_t_ha']} t/ha | "
            f"Esperado: {esperado:.2f} t"
        )


def selecionar_talhao(talhoes: list[dict]) -> dict:
    listar_talhoes(talhoes)
    ids_validos = {talhao["id"] for talhao in talhoes}

    while True:
        talhao_id = ler_inteiro("Escolha o ID do talhao: ")
        if talhao_id in ids_validos:
            for talhao in talhoes:
                if talhao["id"] == talhao_id:
                    return talhao
        print("ID nao encontrado. Tente novamente.")


def registrar_colheita_interativa(talhoes: list[dict], colheitas: list[dict]) -> None:
    talhao = selecionar_talhao(talhoes)
    toneladas_colhidas = ler_float_positivo("Toneladas colhidas: ")

    esperado = calcular_producao_esperada(talhao)
    perda_percentual = ((esperado - toneladas_colhidas) / esperado) * 100
    perda_percentual = max(perda_percentual, 0)

    registro = {
        "talhao_id": talhao["id"],
        "talhao_nome": talhao["nome"],
        "esperado_t": round(esperado, 2),
        "colhido_t": round(toneladas_colhidas, 2),
        "perda_percentual": round(perda_percentual, 2),
        "classificacao": classificar_perda(perda_percentual),
        "enviado_oracle": False,
    }
    colheitas.append(registro)

    registrar_log_texto(
        f"Registro salvo: talhao={talhao['nome']}, colhido={toneladas_colhidas:.2f}t, perda={perda_percentual:.2f}%",
        LOG_TXT,
    )

    print("\nRegistro realizado com sucesso.")
    print(
        f"Perda calculada: {registro['perda_percentual']:.2f}% "
        f"({registro['classificacao']})"
    )

## Salvar Json
def salvar_historico_json(colheitas: list[dict]) -> None:
    with HISTORICO_JSON.open("w", encoding="utf-8") as arquivo:
        json.dump(colheitas, arquivo, indent=2, ensure_ascii=False)

    registrar_log_texto("Historico exportado para JSON.", LOG_TXT)
    print(f"Historico salvo em: {HISTORICO_JSON}")

## exportar resumo
def exportar_resumo_txt(colheitas: list[dict]) -> None:
    resumo = montar_resumo(colheitas)
    tabela_memoria = gerar_tabela_memoria(colheitas)

    linhas = [
        "=== RESUMO OPERACIONAL ===",
        f"Registros: {resumo['quantidade_registros']}",
        f"Total esperado (t): {resumo['total_esperado_t']:.2f}",
        f"Total colhido (t): {resumo['total_colhido_t']:.2f}",
        f"Perda media (%): {resumo['perda_media_percentual']:.2f}",
        "",
        "=== TABELA DE MEMORIA (cumulativo) ===",
    ]

    for linha in tabela_memoria:
        linhas.append(
            f"Iteracao {linha['iteracao']}: talhao={linha['talhao']} | "
            f"acumulado_colhido={linha['acumulado_colhido_t']:.2f}"
        )

    RELATORIO_TXT.write_text("\n".join(linhas), encoding="utf-8")

    registrar_log_texto("Resumo exportado para TXT.", LOG_TXT)
    print(f"Resumo exportado em: {RELATORIO_TXT}")

## Imprimir resumo
def exibir_resumo_console(colheitas: list[dict]) -> None:
    resumo = montar_resumo(colheitas)
    print("\n=== RESUMO ===")
    print(f"Quantidade de registros: {resumo['quantidade_registros']}")
    print(f"Total esperado: {resumo['total_esperado_t']:.2f} t")
    print(f"Total colhido: {resumo['total_colhido_t']:.2f} t")
    print(f"Perda media: {resumo['perda_media_percentual']:.2f}%")

    if resumo["quantidade_registros"] > 0:
        print("\nDetalhes:")
        for registro in resumo["registros"]:
            print(
                f"- {registro['talhao_nome']}: colhido {registro['colhido_t']:.2f} t | "
                f"perda {registro['perda_percentual']:.2f}% ({registro['classificacao']})"
            )
    else:
        print("Nenhuma colheita registrada ainda.")


def buscar_registros_para_visualizacao(colheitas_memoria: list[dict]) -> list[dict]:
    pendentes = [item for item in colheitas_memoria if not item.get("enviado_oracle", False)]

    def limpar_registro(item: dict) -> dict:
        return {
            "talhao_id": item["talhao_id"],
            "talhao_nome": item["talhao_nome"],
            "esperado_t": item["esperado_t"],
            "colhido_t": item["colhido_t"],
            "perda_percentual": item["perda_percentual"],
            "classificacao": item["classificacao"],
        }

    try:
        colheitas_oracle = buscar_colheitas_oracle()
        print(
            f"\nFonte dos dados: Oracle ({len(colheitas_oracle)}) + "
            f"Sessao pendente ({len(pendentes)})."
        )
        return colheitas_oracle + [limpar_registro(item) for item in pendentes]
    except Exception as erro:  # noqa: BLE001
        print(f"\nFalha ao buscar no Oracle ({erro}). Exibindo dados da sessao atual.")
        return [limpar_registro(item) for item in colheitas_memoria]


def enviar_para_oracle(colheitas: list[dict]) -> None:
    pendentes = [item for item in colheitas if not item.get("enviado_oracle", False)]
    if not pendentes:
        print("Nenhum registro pendente para enviar.")
        return

    quantidade = inserir_colheitas_oracle(pendentes)
    for item in pendentes:
        item["enviado_oracle"] = True

    registrar_log_texto(f"{quantidade} registros enviados ao Oracle.", LOG_TXT)
    print(f"{quantidade} registros enviados ao Oracle com sucesso.")


def main() -> None:
    talhoes = carregar_talhoes_json(TALHOES_JSON)
    colheitas: list[dict] = []

    while True:
        procedimento_exibir_menu()
        opcao = ler_inteiro("Escolha uma opcao: ", minimo=0, maximo=6)

        try:
            if opcao == 1:
                listar_talhoes(talhoes)
                pausar_tela()
            elif opcao == 2:
                registrar_colheita_interativa(talhoes, colheitas)
                pausar_tela()
            elif opcao == 3:
                registros = buscar_registros_para_visualizacao(colheitas)
                exibir_resumo_console(registros)
                pausar_tela()
            elif opcao == 4:
                registros = buscar_registros_para_visualizacao(colheitas)
                exportar_resumo_txt(registros)
                pausar_tela()
            elif opcao == 5:
                salvar_historico_json(colheitas)
                pausar_tela()
            elif opcao == 6:
                enviar_para_oracle(colheitas)
                pausar_tela()
            elif opcao == 0:
                print("Encerrando o sistema. Bons resultados no campo!")
                break
        except Exception as erro:  # noqa: BLE001
            print(f"Ocorreu um erro na opcao {opcao}: {erro}")
            pausar_tela()


if __name__ == "__main__":
    main()
