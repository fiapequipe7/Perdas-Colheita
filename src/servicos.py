"""
Módulo de serviços (regras de negócio).

Contém funções responsáveis pelo processamento dos dados do sistema,
como cálculos de produção, perda, classificação e geração de resumos.

Também inclui manipulação de arquivos JSON e geração de logs.


"""
import json
from datetime import datetime
from pathlib import Path

FAIXAS_ALERTA = (5.0, 10.0)


def carregar_talhoes_json(caminho: Path):
    with caminho.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def calcular_producao_esperada(talhao):
    """
        Calcula a produção esperada de um talhão.

        Args:
            talhao (dict): Dicionário contendo dados do talhão.

        Returns:
            float: Produção esperada em toneladas.
    """
    return talhao["hectares"] * talhao["produtividade_esperada_t_ha"]


def calcular_perda(esperado, colhido):
    """
    Calcula a perda percentual da colheita.

    Args:
        esperado (float): Produção esperada.
        colhido (float): Produção real colhida.

    Returns:
        float: Percentual de perda (0 ou mais).
    """
    if esperado == 0:
        return 0.0
    return max(((esperado - colhido) / esperado) * 100, 0)


def classificar_perda(perda):
    """
    Classifica a perda percentual em níveis.

    Args:
        perda (float): Percentual de perda.

    Returns:
        str: Classificação da perda (BAIXA, MODERADA ou ALTA).
    """
    if perda <= FAIXAS_ALERTA[0]:
        return "BAIXA"
    if perda <= FAIXAS_ALERTA[1]:
        return "MODERADA"
    return "ALTA"


def montar_resumo(colheitas):
    """
    Gera um resumo estatístico das colheitas.

    Args:
        colheitas (list): Lista de registros de colheita.

    Returns:
        dict: Dicionário com totais e métricas agregadas.
    """
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
    """
    Registra uma mensagem de log em arquivo texto.

    Args:
        msg (str): Mensagem a ser registrada.
        caminho (Path): Caminho do arquivo de log.
    """
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with caminho.open("a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")