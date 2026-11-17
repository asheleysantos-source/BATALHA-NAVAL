"""Batalha Naval no terminal."""

from batalha_naval import (FROTA, LETRAS, TAMANHO, Jogador, Partida, Ranking,
                           ler_casa, texto)


def _celula_inimigo(tab, casa):
    """O que o jogador enxerga no tabuleiro do computador (navios ficam escondidos)."""
    if casa not in tab.tiros:
        return "."
    if casa not in tab.navios:
        return "o"
    return "#" if tab.afundado(casa) else "X"


def _celula_propria(tab, casa):
    """O que o jogador enxerga no próprio tabuleiro (navios aparecem)."""
    if casa in tab.tiros:
        if casa not in tab.navios:
            return "o"
        return "#" if tab.afundado(casa) else "X"
    if casa in tab.navios:
        return tab.navios[casa][0]
    return "."


def desenhar(partida):
    cabecalho = "    " + " ".join(LETRAS)
    print()
    print(f"{'COMPUTADOR':<23}      SEU TABULEIRO")
    print(f"{cabecalho}      {cabecalho}")
    for l in range(TAMANHO):
        esquerda = " ".join(_celula_inimigo(partida.tab_computador, (l, c)) for c in range(TAMANHO))
        direita = " ".join(_celula_propria(partida.tab_jogador, (l, c)) for c in range(TAMANHO))
        print(f"{l + 1:>2}  {esquerda}      {l + 1:>2}  {direita}")
    print()


def mostrar_instrucoes():
    print("=== BATALHA NAVAL ===")
    print("Digite a casa para atirar, por exemplo: B5   (ou 'sair' para encerrar)")
    print(".=desconhecido  o=água  X=acertou  #=afundado")
    print("Sua frota: " + ", ".join(f"{nome[0]}={nome} ({tam})" for nome, tam in FROTA.items()))


def jogar_uma_partida(jogador, ranking):
    """Devolve False se o jogador quis sair no meio da partida."""
    partida = Partida()
    mostrar_instrucoes()

    while not partida.terminou:
        desenhar(partida)
        entrada = input("Seu tiro: ").strip()
        if entrada.lower() in ("sair", "s"):
            return False

        casa = ler_casa(entrada)
        if casa is None:
            print("Casa inválida. Use uma letra de A a J e um número de 1 a 10 (ex: B5).")
            continue

        resposta = partida.jogador_atira(casa)
        if resposta is None:
            print("Você já atirou aí.")
            continue
        print(texto(jogador.nickname, casa, *resposta))

        if partida.terminou:
            break
        casa_pc, resultado, nome = partida.computador_atira()
        print(texto("Computador", casa_pc, resultado, nome))

    desenhar(partida)
    venceu = partida.vencedor == "jogador"
    print(f"{jogador.nickname} venceu!" if venceu else partida.mensagem_final)
    ranking.registrar(jogador, venceu)
    ranking.exibir()
    return True


def iniciar():
    print("=== BATALHA NAVAL ===")
    jogador = Jogador.pedir_dados()
    ranking = Ranking()
    print(f"\nBem-vindo(a), {jogador.nickname}!")
    ranking.exibir()

    while jogar_uma_partida(jogador, ranking):
        if input("\nJogar de novo? (s/n): ").strip().lower() != "s":
            break
    print("Até a próxima!")
