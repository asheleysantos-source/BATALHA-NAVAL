import random
import tkinter as tk
from tkinter import messagebox

TAMANHO = 10
FROTA = {
    "Porta-aviões": 5,
    "Encouraçado": 4,
    "Cruzador": 3,
    "Submarino": 3,
    "Destroyer": 2,
}
LETRAS = "ABCDEFGHIJ"


# ---------------------------------------------------------------
# LÓGICA
# ---------------------------------------------------------------

class Tabuleiro:
    def __init__(self):
        self.navios = {}      # (linha, coluna) -> nome do navio
        self.restantes = {}   # nome do navio -> quantas casas ainda não foram atingidas
        self.tiros = set()    # casas onde já se atirou
        self.posicionar_frota()

    def posicionar_frota(self):
        for nome, tamanho in FROTA.items():
            while True:
                linha = random.randrange(TAMANHO)
                coluna = random.randrange(TAMANHO)
                if random.choice([True, False]):
                    casas = [(linha, coluna + i) for i in range(tamanho)]
                else:
                    casas = [(linha + i, coluna) for i in range(tamanho)]

                cabe = all(0 <= l < TAMANHO and 0 <= c < TAMANHO and (l, c) not in self.navios
                           for l, c in casas)
                if cabe:
                    for casa in casas:
                        self.navios[casa] = nome
                    self.restantes[nome] = tamanho
                    break

    def atirar(self, casa):
        """Devolve (resultado, nome_do_navio). Resultado: 'agua', 'acerto' ou 'afundou'."""
        self.tiros.add(casa)
        nome = self.navios.get(casa)
        if nome is None:
            return "agua", None
        self.restantes[nome] -= 1
        if self.restantes[nome] == 0:
            return "afundou", nome
        return "acerto", nome

    def perdeu(self):
        return all(falta == 0 for falta in self.restantes.values())


class Computador:
    """Atira aleatoriamente. Depois de acertar, tenta as casas vizinhas."""

    def __init__(self):
        self.alvos = []

    def escolher(self, tabuleiro):
        while self.alvos:
            casa = self.alvos.pop()
            if casa not in tabuleiro.tiros:
                return casa
        livres = [(l, c) for l in range(TAMANHO) for c in range(TAMANHO)
                  if (l, c) not in tabuleiro.tiros]
        return random.choice(livres)

    def acertou(self, casa):
        l, c = casa
        for viz in [(l + 1, c), (l - 1, c), (l, c + 1), (l, c - 1)]:
            if 0 <= viz[0] < TAMANHO and 0 <= viz[1] < TAMANHO:
                self.alvos.append(viz)


def texto(quem, casa, resultado, nome):
    local = f"{LETRAS[casa[1]]}{casa[0] + 1}"
    if resultado == "agua":
        return f"{quem} atirou em {local}: água."
    tamanho = FROTA[nome]
    if resultado == "acerto":
        return f"{quem} atirou em {local}: acertou o {nome} (navio de {tamanho} casas)!"
    return f"{quem} atirou em {local}: AFUNDOU o {nome} (navio de {tamanho} casas)!"


# ---------------------------------------------------------------
# INTERFACE
# ---------------------------------------------------------------

class Jogo:
    def __init__(self, janela):
        self.janela = janela
        self.agendado = None
        janela.title("Batalha Naval")

        self.msg_eu = tk.Label(janela, font=("Arial", 14, "bold"))
        self.msg_eu.grid(row=0, column=0, columnspan=2, pady=(8, 0))
        self.msg_pc = tk.Label(janela, font=("Arial", 11), fg="gray")
        self.msg_pc.grid(row=1, column=0, columnspan=2)

        tk.Label(janela, text="Tabuleiro do computador (clique para atirar)").grid(row=2, column=0)
        tk.Label(janela, text="Seu tabuleiro").grid(row=2, column=1)
        self.celulas_pc = self.criar_grade(0, clicavel=True)
        self.celulas_eu = self.criar_grade(1, clicavel=False)

        legenda = ", ".join(f"{nome[0]} = {nome} ({tam})" for nome, tam in FROTA.items())
        tk.Label(janela, text=legenda).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(janela, text="Novo jogo", command=self.novo_jogo).grid(
            row=5, column=0, columnspan=2, pady=(0, 8))

        self.novo_jogo()

    def criar_grade(self, coluna, clicavel):
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

    def novo_jogo(self):
        if self.agendado:
            self.janela.after_cancel(self.agendado)
            self.agendado = None
        self.pc = Tabuleiro()
        self.eu = Tabuleiro()
        self.ia = Computador()
        self.minha_vez = True
        self.fim = False

        for celula in self.celulas_pc.values():
            celula.config(bg="white", text="")
        for casa, celula in self.celulas_eu.items():
            celula.config(bg="gray" if casa in self.eu.navios else "white", text="")
        self.msg_eu.config(text="Sua vez! Clique no tabuleiro do computador.")
        self.msg_pc.config(text="")

    def clicar(self, casa):
        if self.fim or not self.minha_vez or casa in self.pc.tiros:
            return
        resultado, nome = self.pc.atirar(casa)
        self.pintar(self.celulas_pc, self.pc, casa, resultado, nome)
        self.msg_eu.config(text=texto("Você", casa, resultado, nome))

        if self.pc.perdeu():
            self.terminar("Você venceu!")
            return
        self.minha_vez = False
        self.agendado = self.janela.after(800, self.turno_pc)

    def turno_pc(self):
        self.agendado = None
        casa = self.ia.escolher(self.eu)
        resultado, nome = self.eu.atirar(casa)
        if resultado == "acerto":
            self.ia.acertou(casa)
        self.pintar(self.celulas_eu, self.eu, casa, resultado, nome)
        self.msg_pc.config(text=texto("Computador", casa, resultado, nome))

        if self.eu.perdeu():
            self.terminar("O computador venceu!")
            return
        self.minha_vez = True

    def pintar(self, celulas, tabuleiro, casa, resultado, nome):
        if resultado == "agua":
            celulas[casa].config(bg="lightblue", text="o")
            return
        celulas[casa].config(bg="orange", text=nome[0])
        if resultado == "afundou":
            for c, n in tabuleiro.navios.items():
                if n == nome:
                    celulas[c].config(bg="red", text=nome[0])

    def terminar(self, mensagem):
        self.fim = True
        self.msg_eu.config(text=mensagem)
        messagebox.showinfo("Fim de jogo", mensagem)


if __name__ == "__main__":
    janela = tk.Tk()
    Jogo(janela)
    janela.mainloop()