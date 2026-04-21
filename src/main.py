"""
Módulo principal do sistema de monitoramento de colheita de cana-de-açúcar.

Este arquivo é responsável apenas por iniciar a aplicação, delegando a
execução do fluxo principal para o módulo de interface com o usuário (ui).

"""

from ui import iniciar_menu

if __name__ == "__main__":
    iniciar_menu()