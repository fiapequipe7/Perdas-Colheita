import json
from datetime import datetime
from pathlib import Path

FAIXAS_ALERTA: tuple[float, float] = (5.0, 10.0)


def carregar_talhoes_json(caminho: Path) -> list[dict]:
    with caminho.open("r", encoding="utf-8-sig") as arquivo:
        return json.load(arquivo)


def calcular_producao_esperada(talhao: dict) -> float:
    return talhao["hectares"] * talhao["produtividade_esperada_t_ha"]


def classificar_perda(perda_percentual: float) -> str:
    if perda_percentual <= FAIXAS_ALERTA[0]:
        return "BAIXA"
    if perda_percentual <= FAIXAS_ALERTA[1]:
        return "MODERADA"
    return "ALTA"


def montar_resumo(colheitas: list[dict]) -> dict:
    if not colheitas:
        return {
            "quantidade_registros": 0,
            "total_esperado_t": 0.0,
            "total_colhido_t": 0.0,
            "perda_media_percentual": 0.0,
            "registros": [],
        }

    total_esperado = sum(item["esperado_t"] for item in colheitas)
    total_colhido = sum(item["colhido_t"] for item in colheitas)
    perda_media = sum(item["perda_percentual"] for item in colheitas) / len(colheitas)

    return {
        "quantidade_registros": len(colheitas),
        "total_esperado_t": total_esperado,
        "total_colhido_t": total_colhido,
        "perda_media_percentual": perda_media,
        "registros": colheitas,
    }


def gerar_tabela_memoria(colheitas: list[dict]) -> list[dict]:
    tabela: list[dict] = []
    acumulado = 0.0

    for indice, item in enumerate(colheitas, start=1):
        acumulado += item["colhido_t"]
        tabela.append(
            {
                "iteracao": indice,
                "talhao": item["talhao_nome"],
                "acumulado_colhido_t": acumulado,
            }
        )

    return tabela


def registrar_log_texto(mensagem: str, caminho_log: Path) -> None:
    caminho_log.parent.mkdir(parents=True, exist_ok=True)
    registro = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensagem}\n"
    with caminho_log.open("a", encoding="utf-8") as arquivo:
        arquivo.write(registro)
