import numpy as np
from random import choice

# PLAYER X = 1
# PLAYER O = -1

class TicTacToeBoard:
    def __init__(self):
        self.EMPTY = 0  # Representa uma célula vazia no tabuleiro
        self.reset()  # Inicializa o tabuleiro

    def make_move(self, row, col):
        if self.winner or self.game_steps == 9:  # Impede jogadas após vitória ou empate
            return

        if self.game_array[row, col] == self.EMPTY:  # Verifica se a célula está vazia
            self.game_array[row, col] = self.player  # Marca a célula com o número do jogador
            self.player *= -1  # Alterna o jogador (0 vira 1 e vice-versa)
            self.game_steps += 1  # Incrementa o número de jogadas
            self.check_winner()  # Verifica se houve um vencedor após a jogada

            if self.game_steps == 9 and not self.winner:  # Se todas as 9 jogadas foram feitas e não há vencedor
                self.winner = 'Draw'  # O jogo termina em empate

    def check_winner(self):
        for line_indices in self.line_indices_array:  # Itera sobre todas as possíveis linhas vencedoras
            line = self.game_array[np.array([i for i, j in line_indices]), np.array([j for i, j in line_indices])]
            if np.all(line == -1):  # Se todos os valores na linha são 0
                self.winner = 'O'
                self.winning_line = line_indices
            elif np.all(line == 1):  # Se todos os valores na linha são 1
                self.winner = 'X'
                self.winning_line = line_indices

    def reset(self):
        self.game_array = np.full((3, 3), self.EMPTY)  # Cria um tabuleiro 3x3, inicialmente vazio
        self.player =  choice([-1, 1]) # Escolhe aleatoriamente quem será o primeiro jogador
        self.winner = None  # Inicialmente, não há vencedor
        self.game_steps = 0  # Conta o número de jogadas feitas
        self.winning_line = None  # Armazena a linha vencedora, se houver
        # Definição das combinações de linhas que podem ser vencedoras
        self.line_indices_array = [
            [(0, 0), (0, 1), (0, 2)],  # Linhas horizontais
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],  # Linhas verticais
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],  # Diagonais
            [(0, 2), (1, 1), (2, 0)]
        ]