"""Ponto de entrada da Batalha Naval.

Uso:
    python main.py              -> pergunta se quer terminal ou janela
    python main.py --janela     -> abre direto a janela
    python main.py --terminal   -> joga direto no terminal
"""

import sys

import interface_terminal

def perguntar_modo():
    print("=== BATALHA NAVAL ===")
    print("1 - Janela (interface gráfica)")
    print("2 - Terminal")
    while True:
        escolha = input("Escolha 1 ou 2: ").strip()
        if escolha == "1":
            return "janela"
        if escolha == "2":
            return "terminal"


def abrir_janela():
    """Abre a janela. Devolve False se não for possível (sem tkinter ou sem tela)."""
    try:
        import tkinter
    except ImportError:
        print("O tkinter não está instalado. Usando o terminal.")
        return False

    from interface_grafica import iniciar
    try:
        iniciar()
    except tkinter.TclError as erro:
        print(f"Não foi possível abrir a janela ({erro}). Usando o terminal.")
        return False
    return True


def main():
    argumentos = sys.argv[1:]
    if "--terminal" in argumentos or "-t" in argumentos:
        modo = "terminal"
    elif "--janela" in argumentos or "-j" in argumentos:
        modo = "janela"
    else:
        modo = perguntar_modo()

    if modo == "janela" and abrir_janela():
        return
    interface_terminal.iniciar()


if __name__ == "__main__":
    main()
