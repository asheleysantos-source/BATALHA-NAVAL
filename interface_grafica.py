"""Batalha Naval na janela (tkinter)."""

import tkinter as tk
from tkinter import messagebox, simpledialog

from batalha_naval import FROTA, LETRAS, TAMANHO, Jogador, Partida, Ranking, texto


class JogoGrafico:
    def __init__(self, janela, jogador):
        self.janela = janela
        self.jogador = jogador
        self.ranking = Ranking()
        self.agendado = None
        janela.title("Batalha Naval")

        self.msg_eu = tk.Label(janela, font=("Arial", 14, "bold"))
        self.msg_eu.grid(row=0, column=0, columnspan=2, pady=(8, 0))
        self.msg_pc = tk.Label(janela, font=("Arial", 11), fg="gray")
        self.msg_pc.grid(row=1, column=0, columnspan=2)

        tk.Label(janela, text="Tabuleiro do computador (clique para atirar)").grid(row=2, column=0)
        tk.Label(janela, text=f"Tabuleiro de {jogador.nickname}").grid(row=2, column=1)
        self.celulas_pc = self._criar_grade(0, clicavel=True)
        self.celulas_eu = self._criar_grade(1, clicavel=False)

        self.painel_ranking = tk.Label(janela, font=("Courier", 10), justify="left",
                                       anchor="n", relief="groove", padx=10, pady=8)
        self.painel_ranking.grid(row=2, column=2, rowspan=2, padx=10, sticky="n")
        self._atualizar_ranking()

        legenda = ", ".join(f"{nome[0]} = {nome} ({tam})" for nome, tam in FROTA.items())
        tk.Label(janela, text=legenda).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(janela, text="Novo jogo", command=self.novo_jogo).grid(
            row=5, column=0, columnspan=2, pady=(0, 8))

        self.novo_jogo()

    # --- montagem da tela ---

    def _criar_grade(self, coluna, clicavel):
        quadro = tk.Frame(self.janela, padx=10, pady=5)
        quadro.grid(row=3, column=coluna)
        for c in range(TAMANHO):
            tk.Label(quadro, text=LETRAS[c]).grid(row=0, column=c + 1)

        celulas = {}
        for l in range(TAMANHO):
            tk.Label(quadro, text=str(l + 1)).grid(row=l + 1, column=0)
            for c in range(TAMANHO):
                celula = tk.Label(quadro, width=3, bg="white", relief="ridge", borderwidth=2)
                celula.grid(row=l + 1, column=c + 1)
                if clicavel:
                    celula.bind("<Button-1>", lambda e, casa=(l, c): self.clicar(casa))
                celulas[(l, c)] = celula
        return celulas

    # --- fluxo do jogo ---

    def novo_jogo(self):
        if self.agendado:
            self.janela.after_cancel(self.agendado)
            self.agendado = None
        self.partida = Partida()

        for celula in self.celulas_pc.values():
            celula.config(bg="white", text="")
        for casa, celula in self.celulas_eu.items():
            celula.config(bg="gray" if casa in self.partida.tab_jogador.navios else "white", text="")
        self.msg_eu.config(text="Sua vez! Clique no tabuleiro do computador.")
        self.msg_pc.config(text="")

    def clicar(self, casa):
        resposta = self.partida.jogador_atira(casa)
        if resposta is None:
            return
        resultado, nome = resposta
        self._pintar(self.celulas_pc, self.partida.tab_computador, casa, resultado, nome)
        self.msg_eu.config(text=texto(self.jogador.nickname, casa, resultado, nome))

        if self.partida.terminou:
            self._terminar()
            return
        self.agendado = self.janela.after(800, self._turno_computador)

    def _turno_computador(self):
        self.agendado = None
        casa, resultado, nome = self.partida.computador_atira()
        self._pintar(self.celulas_eu, self.partida.tab_jogador, casa, resultado, nome)
        self.msg_pc.config(text=texto("Computador", casa, resultado, nome))

        if self.partida.terminou:
            self._terminar()

    def _pintar(self, celulas, tabuleiro, casa, resultado, nome):
        if resultado == "agua":
            celulas[casa].config(bg="lightblue", text="o")
            return
        celulas[casa].config(bg="orange", text=nome[0])
        if resultado == "afundou":
            for c, n in tabuleiro.navios.items():
                if n == nome:
                    celulas[c].config(bg="red", text=nome[0])

    def _atualizar_ranking(self):
        linhas = ["RANKING", ""]
        top = self.ranking.top(10)
        if not top:
            linhas.append("Sem partidas ainda.")
        else:
            linhas.append(f"{'#':>2} {'Nickname':<12} {'V':>3} {'D':>3}")
            for posicao, r in enumerate(top, start=1):
                linhas.append(f"{posicao:>2} {r['nickname'][:12]:<12} "
                              f"{r['vitorias']:>3} {r['derrotas']:>3}")
        self.painel_ranking.config(text="\n".join(linhas))

    def _terminar(self):
        venceu = self.partida.vencedor == "jogador"
        mensagem = f"{self.jogador.nickname} venceu!" if venceu else self.partida.mensagem_final
        self.ranking.registrar(self.jogador, venceu)
        self._atualizar_ranking()
        self.msg_eu.config(text=mensagem)
        messagebox.showinfo("Fim de jogo", mensagem)


def pedir_jogador(janela):
    """Pergunta nome, idade e nickname em caixinhas. Devolve None se cancelar."""
    nome = None
    while not nome:
        nome = simpledialog.askstring("Jogador", "Qual é o seu nome?", parent=janela)
        if nome is None:
            return None
        nome = nome.strip()

    idade = simpledialog.askinteger("Jogador", "Qual é a sua idade?",
                                    parent=janela, minvalue=1, maxvalue=120)
    if idade is None:
        return None

    apelido = simpledialog.askstring("Jogador", "Como você gostaria de ser chamado (nickname)?",
                                     parent=janela)
    if apelido is None:
        return None
    apelido = apelido.strip() or nome.split()[0]
    return Jogador(nome, idade, apelido)


def iniciar():
    janela = tk.Tk()
    jogador = pedir_jogador(janela)
    if jogador is None:
        janela.destroy()
        return
    JogoGrafico(janela, jogador)
    janela.mainloop()
