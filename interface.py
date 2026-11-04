import tkinter as tk
from tkinter import messagebox

from batalha_naval import Jogo

TAMANHO = 10
MENSAGENS = {
    "agua": "Água!",
    "acerto": "Acertou um navio!",
    "afundou": "Afundou um navio!",
}


class InterfaceJogo:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Batalha Naval")

        
        self.jogo = Jogo("Você")
        self.jogo.preparar()
        self.vez_humano = True

        self.mensagem = tk.Label(janela, text="Clique no tabuleiro do computador para atirar")
        self.mensagem.grid(row=0, column=0, columnspan=2, pady=5)

        tk.Label(janela, text="Tabuleiro do computador").grid(row=1, column=0)
        tk.Label(janela, text="Seu tabuleiro").grid(row=1, column=1)

        self.celulas_computador = self.criar_grade(coluna=0, clicavel=True)
        self.celulas_jogador = self.criar_grade(coluna=1, clicavel=False)
        self.atualizar()

    def criar_grade(self, coluna, clicavel):
        """Cria uma grade 10x10 de quadradinhos e devolve a matriz deles."""
        quadro = tk.Frame(self.janela, padx=10, pady=5)
        quadro.grid(row=2, column=coluna)

        celulas = []
        for l in range(TAMANHO):
            linha = []
            for c in range(TAMANHO):
                celula = tk.Label(quadro, text="", width=3, height=1,
                                  bg="white", relief="ridge", borderwidth=2)
                celula.grid(row=l, column=c)
                if clicavel:
                    celula.bind("<Button-1>", lambda evento, l=l, c=c: self.clicar(l, c))
                linha.append(celula)
            celulas.append(linha)
        return celulas

    def clicar(self, linha, coluna):
        """Tiro do jogador no tabuleiro do computador."""
        if not self.vez_humano:
            return

        tabuleiro = self.jogo.computador.tabuleiro
        if (linha, coluna) in tabuleiro.tiros:
            self.mensagem.config(text="Você já atirou aí.")
            return

        resultado = tabuleiro.receber_tiro((linha, coluna))
        self.mostrar_tiro("Você", (linha, coluna), resultado)
        self.atualizar()

        if tabuleiro.todos_afundados():
            self.fim_de_jogo("Você venceu!")
            return

        self.vez_humano = False
        self.janela.after(600, self.turno_computador)  

    def turno_computador(self):
        computador = self.jogo.computador
        tabuleiro = self.jogo.humano.tabuleiro

        pos = computador.escolher_tiro(tabuleiro)
        resultado = tabuleiro.receber_tiro(pos)
        computador.registrar_resultado(pos, resultado, tabuleiro)
        self.mostrar_tiro("Computador", pos, resultado)
        self.atualizar()

        if tabuleiro.todos_afundados():
            self.fim_de_jogo("O computador venceu!")
            return

        self.vez_humano = True

    def mostrar_tiro(self, quem, pos, resultado):
        letra = chr(ord("A") + pos[1])
        self.mensagem.config(text=f"{quem} atirou em {letra}{pos[0] + 1}: {MENSAGENS[resultado]}")

    def atualizar(self):
        """Pinta as grades de acordo com o estado dos tabuleiros."""
        comp = self.jogo.computador.tabuleiro
        hum = self.jogo.humano.tabuleiro
        ocupadas = hum._posicoes_ocupadas()

        for l in range(TAMANHO):
            for c in range(TAMANHO):
                self.pintar(self.celulas_computador[l][c], comp.tiros.get((l, c)))

                navio = (l, c) in ocupadas
                self.pintar(self.celulas_jogador[l][c], hum.tiros.get((l, c)), navio)

    @staticmethod
    def pintar(celula, tiro, navio=False):
        """tiro: True = acerto, False = água, None = sem tiro."""
        if tiro is True:
            celula.config(bg="red", text="X")
        elif tiro is False:
            celula.config(bg="lightblue", text="o")
        elif navio:
            celula.config(bg="gray")
        else:
            celula.config(bg="white")

    def fim_de_jogo(self, texto):
        self.vez_humano = False
        self.mensagem.config(text=texto)
        messagebox.showinfo("Fim de jogo", texto)


if __name__ == "__main__":
    janela = tk.Tk()
    InterfaceJogo(janela)
    janela.mainloop()