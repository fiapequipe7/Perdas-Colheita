"""
Módulo de interface com o usuário (UI).

Responsável por:
- Exibir o menu principal
- Receber entradas do usuário
- Controlar o fluxo da aplicação
- Chamar funções dos módulos de serviço e banco de dados

Este módulo não contém regras de negócio, apenas interação com o usuário.
"""

import json
import os
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
    """
    Inicia o menu principal do sistema.
    """
    talhoes = carregar_talhoes_json(TALHOES_JSON)
    colheitas = []

    limpar_tela()

    while True:
        print("\n" + "=" * 40)
        print("🌱 SISTEMA DE COLHEITA DE CANA".center(40))
        print("=" * 40)
        print("[1] Listar talhões")
        print("[2] Registrar colheita")
        print("[3] Ver resumo")
        print("[4] Exportar resumo TXT")
        print("[5] Salvar histórico JSON")
        print("[6] Enviar para Oracle")
        print("[0] Sair")
        print("=" * 40)

        opcao = ler_inteiro("Escolha: ", 0, 6)

        try:
            match opcao:
                case 1:
                    limpar_tela()
                    listar_talhoes(talhoes)
                    pausar()

                case 2:
                    limpar_tela()
                    print("📝 REGISTRAR COLHEITA\n")
                    registrar_colheita(talhoes, colheitas)
                    pausar()

                case 3:
                    limpar_tela()
                    registros = buscar_registros(colheitas)
                    exibir_resumo(registros)
                    pausar()

                case 4:
                    limpar_tela()
                    registros = buscar_registros(colheitas)
                    exportar_resumo(registros)
                    pausar()

                case 5:
                    limpar_tela()
                    salvar_json(colheitas)
                    pausar()

                case 6:
                    limpar_tela()
                    enviar_oracle(colheitas)
                    pausar()

                case 0:
                    print("\n🌱 Encerrando o sistema...")
                    break

        except Exception as e:
            print(f"\n❌ Erro: {e}")
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
            print("❌ Entrada inválida")


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def pausar():
    input("\nPressione ENTER para continuar...")
    limpar_tela()


def listar_talhoes(talhoes):
    print("\n📍 TALHÕES DISPONÍVEIS\n" + "-" * 40)

    for t in talhoes:
        esperado = calcular_producao_esperada(t)
        print(f"[{t['id']}] {t['nome']} → {esperado:.2f} t")

    print("-" * 40)


def registrar_colheita(talhoes, colheitas):
    listar_talhoes(talhoes)

    id_escolhido = ler_inteiro("\nID do talhão: ")
    talhao = next(t for t in talhoes if t["id"] == id_escolhido)

    colhido = float(input("Toneladas colhidas: ").replace(",", "."))

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

    print("\n✅ Registro realizado com sucesso!")
    print(f"Perda: {perda:.2f}% ({registro['classificacao']})")


def buscar_registros(memoria):
    try:
        oracle = buscar_colheitas_oracle()
        pendentes = [c for c in memoria if not c["enviado_oracle"]]
        print(f"\n🔗 Oracle: {len(oracle)} | Sessão: {len(pendentes)}")
        return oracle + pendentes
    except:
        print("\n⚠ Usando apenas dados locais.")
        return memoria


def exibir_resumo(colheitas):
    resumo = montar_resumo(colheitas)

    print("\n📊 RESUMO\n" + "-" * 40)
    print(resumo)
    print("-" * 40)


def exportar_resumo(colheitas):
    resumo = montar_resumo(colheitas)
    tabela = gerar_tabela_memoria(colheitas)

    texto = f"Resumo: {resumo}\nTabela: {tabela}"
    RELATORIO_TXT.write_text(texto)

    print("\n✅ Resumo exportado com sucesso!")


def salvar_json(colheitas):
    with HISTORICO_JSON.open("w", encoding="utf-8") as f:
        json.dump(colheitas, f, indent=2)

    print("\n✅ Histórico salvo com sucesso!")


def enviar_oracle(colheitas):
    pendentes = [c for c in colheitas if not c["enviado_oracle"]]
    qtd = inserir_colheitas_oracle(pendentes)

    for c in pendentes:
        c["enviado_oracle"] = True

    print(f"\n✅ {qtd} registros enviados ao Oracle!")