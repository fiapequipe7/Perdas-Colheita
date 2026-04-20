import json
from datetime import datetime
from pathlib import Path

FAIXAS_ALERTA = (5.0, 10.0)


def carregar_talhoes_json(caminho: Path):
    with caminho.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def calcular_producao_esperada(talhao):
    return talhao["hectares"] * talhao["produtividade_esperada_t_ha"]


def calcular_perda(esperado, colhido):
    if esperado == 0:
        return 0.0
    return max(((esperado - colhido) / esperado) * 100, 0)


def classificar_perda(perda):
    if perda <= FAIXAS_ALERTA[0]:
        return "BAIXA"
    if perda <= FAIXAS_ALERTA[1]:
        return "MODERADA"
    return "ALTA"


def montar_resumo(colheitas):
    if not colheitas:
        return {}

    total_esperado = sum(c["esperado_t"] for c in colheitas)
    total_colhido = sum(c["colhido_t"] for c in colheitas)

    return {
        "quantidade": len(colheitas),
        "esperado": total_esperado,
        "colhido": total_colhido,
    }


def gerar_tabela_memoria(colheitas):
    tabela = []
    acumulado = 0

    for i, c in enumerate(colheitas, 1):
        acumulado += c["colhido_t"]
        tabela.append({"iter": i, "acumulado": acumulado})

    return tabela


def registrar_log_texto(msg, caminho: Path):
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")