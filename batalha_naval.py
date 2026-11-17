"""Lógica da Batalha Naval.

Este arquivo não imprime nada e não usa tkinter: ele só sabe jogar.
As interfaces (terminal e janela) usam as classes daqui.
"""

import json
import os
import random

TAMANHO = 10
LETRAS = "ABCDEFGHIJ"
FROTA = {
    "Porta-aviões": 5,
    "Encouraçado": 4,
    "Cruzador": 3,
    "Submarino": 3,
    "Destroyer": 2,
}


# ---------------------------------------------------------------
# Tabuleiro
# ---------------------------------------------------------------

class Tabuleiro:
    def __init__(self):
        self.navios = {}      # (linha, coluna) -> nome do navio
        self.restantes = {}   # nome do navio -> casas ainda não atingidas
        self.tiros = set()    # casas onde já se atirou
        self._posicionar_frota()

    def _posicionar_frota(self):
        for nome, tamanho in FROTA.items():
            while True:
                linha = random.randrange(TAMANHO)
                coluna = random.randrange(TAMANHO)
                if random.choice([True, False]):
                    casas = [(linha, coluna + i) for i in range(tamanho)]
                else:
                    casas = [(linha + i, coluna) for i in range(tamanho)]

                cabe = all(
                    0 <= l < TAMANHO and 0 <= c < TAMANHO and (l, c) not in self.navios
                    for l, c in casas
                )
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

    def afundado(self, casa):
        """True se a casa pertence a um navio que já afundou por inteiro."""
        nome = self.navios.get(casa)
        return nome is not None and self.restantes[nome] == 0

    def perdeu(self):
        return all(falta == 0 for falta in self.restantes.values())


# ---------------------------------------------------------------
# Computador
# ---------------------------------------------------------------

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


# ---------------------------------------------------------------
# Partida (controla os turnos; é o que as interfaces usam)
# ---------------------------------------------------------------

class Partida:
    def __init__(self):
        self.tab_jogador = Tabuleiro()
        self.tab_computador = Tabuleiro()
        self.ia = Computador()
        self.vez_do_jogador = True
        self.vencedor = None  # None, "jogador" ou "computador"

    @property
    def terminou(self):
        return self.vencedor is not None

    @property
    def mensagem_final(self):
        if self.vencedor == "jogador":
            return "Você venceu!"
        if self.vencedor == "computador":
            return "O computador venceu!"
        return ""

    def jogador_atira(self, casa):
        """Devolve (resultado, nome), ou None se o tiro não for válido agora."""
        if self.terminou or not self.vez_do_jogador or casa in self.tab_computador.tiros:
            return None
        resposta = self.tab_computador.atirar(casa)
        if self.tab_computador.perdeu():
            self.vencedor = "jogador"
        else:
            self.vez_do_jogador = False
        return resposta

    def computador_atira(self):
        """Devolve (casa, resultado, nome)."""
        casa = self.ia.escolher(self.tab_jogador)
        resultado, nome = self.tab_jogador.atirar(casa)
        if resultado == "acerto":
            self.ia.acertou(casa)
        if self.tab_jogador.perdeu():
            self.vencedor = "computador"
        else:
            self.vez_do_jogador = True
        return casa, resultado, nome


# ---------------------------------------------------------------
# Funções auxiliares usadas pelas duas interfaces
# ---------------------------------------------------------------

def nome_da_casa(casa):
    """(0, 1) -> 'B1'"""
    return f"{LETRAS[casa[1]]}{casa[0] + 1}"


def ler_casa(entrada):
    """'b5' -> (4, 1). Devolve None se a entrada for inválida."""
    entrada = entrada.strip().upper()
    if len(entrada) < 2 or entrada[0] not in LETRAS or not entrada[1:].isdigit():
        return None
    linha = int(entrada[1:]) - 1
    if not 0 <= linha < TAMANHO:
        return None
    return (linha, LETRAS.index(entrada[0]))


def texto(quem, casa, resultado, nome):
    local = nome_da_casa(casa)
    if resultado == "agua":
        return f"{quem} atirou em {local}: água."
    tamanho = FROTA[nome]
    if resultado == "acerto":
        return f"{quem} atirou em {local}: acertou o {nome} (navio de {tamanho} casas)!"
    return f"{quem} atirou em {local}: AFUNDOU o {nome} (navio de {tamanho} casas)!"


# ---------------------------------------------------------------
# Jogador
# ---------------------------------------------------------------

class Jogador:
    """Guarda nome, idade e nickname de quem vai jogar."""

    def __init__(self, nome, idade, nickname):
        self.nome = nome
        self.idade = idade
        self.nickname = nickname

    @classmethod
    def pedir_dados(cls):
        """Pergunta nome, idade e nickname no terminal e devolve um Jogador."""
        nome = cls._pedir_texto("Qual é o seu nome? ")
        idade = cls._pedir_idade()
        apelido = input("Como você gostaria de ser chamado (nickname)? ").strip()
        if not apelido:
            apelido = nome.split()[0]
        return cls(nome, idade, apelido)

    @staticmethod
    def _pedir_texto(pergunta):
        while True:
            resposta = input(pergunta).strip()
            if resposta:
                return resposta
            print("Esse campo não pode ficar vazio.")

    @staticmethod
    def _pedir_idade():
        while True:
            resposta = input("Qual é a sua idade? ").strip()
            if resposta.isdigit() and 1 <= int(resposta) <= 120:
                return int(resposta)
            print("Digite uma idade válida (número de 1 a 120).")

    def __str__(self):
        return f"{self.nickname} ({self.nome}, {self.idade} anos)"


# ---------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------

class Ranking:
    """Guarda vitórias e derrotas de cada jogador em um arquivo ranking.json."""

    def __init__(self, arquivo=None):
        pasta = os.path.dirname(os.path.abspath(__file__))
        self.arquivo = arquivo or os.path.join(pasta, "ranking.json")
        self.dados = {}
        self.carregar()

    def carregar(self):
        try:
            with open(self.arquivo, encoding="utf-8") as f:
                self.dados = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.dados = {}

    def salvar(self):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def registrar(self, jogador, venceu):
        """Soma uma vitória (venceu=True) ou uma derrota ao jogador e salva."""
        registro = self.dados.setdefault(jogador.nickname.lower(), {
            "nickname": jogador.nickname, "nome": jogador.nome,
            "idade": jogador.idade, "vitorias": 0, "derrotas": 0,
        })
        registro["nome"] = jogador.nome
        registro["idade"] = jogador.idade
        registro["vitorias" if venceu else "derrotas"] += 1
        self.salvar()

    def top(self, quantidade=10):
        """Mais vitórias primeiro; em empate, quem tem menos derrotas."""
        ordenados = sorted(
            self.dados.values(),
            key=lambda r: (-r["vitorias"], r["derrotas"], r["nickname"].lower()),
        )
        return ordenados[:quantidade]

    def exibir(self, quantidade=10):
        print("\n=== RANKING ===")
        top = self.top(quantidade)
        if not top:
            print("Ainda não há partidas registradas.")
            return
        print(f"{'#':>2}  {'Nickname':<15} {'Vitórias':>8} {'Derrotas':>8}")
        for posicao, r in enumerate(top, start=1):
            print(f"{posicao:>2}  {r['nickname']:<15} {r['vitorias']:>8} {r['derrotas']:>8}")