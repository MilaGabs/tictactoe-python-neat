import numpy as np
from random import choice

# PLAYER X = 1
# PLAYER O = -1

class TicTacToeBoard:
    def __init__(self):
        self.EMPTY = 0  # Representa uma célula vazia no tabuleiro
        self.reset()  # Inicializa o tabuleiro

    def make_move(self, row, col):
        if self.winner or self.game_steps == 9:
            return

        if self.game_array[row, col] == self.EMPTY:
            self.game_array[row, col] = self.player
            self.game_steps += 1
            self.check_winner()

            # Todas as 9 jogadas foram feitas e não há vencedor
            if self.game_steps == 9 and not self.winner:
                self.winner = 'Emapate'

    def check_winner(self):
        for line_indices in self.line_indices_array:
            line = self.game_array[np.array([i for i, j in line_indices]), np.array([j for i, j in line_indices])]
            if np.all(line == -1):
                self.winner = 'O'
                self.winning_line = line_indices
            elif np.all(line == 1):
                self.winner = 'X'
                self.winning_line = line_indices

    def reset(self):
        self.game_array = np.full((3, 3), self.EMPTY)  # Cria um tabuleiro 3x3, inicialmente vazio
        self.player =  choice([-1, 1]) # Escolhe aleatoriamente quem será o primeiro jogador
        self.winner = None
        self.game_steps = 0
        self.winning_line = None
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

    def is_opponent_about_to_win(self):
        opponent = -self.player
        return self._is_about_to_win(opponent)

    def is_x_about_to_win(self):
        return self._is_about_to_win(1)

    def moves_block_opponent(self, move):
        # Verificar se a ação realizada bloqueia uma jogada vencedora do oponente
        opponent = -self.player
        row, col = divmod(move, 3)

        # Simular o tabuleiro com o movimento do oponente
        temp_game_array = self.game_array.copy()
        temp_game_array[row, col] = opponent

        # Verificar se o oponente venceria após essa jogada
        return self._player_would_win(opponent, temp_game_array)

    def creates_multiple_threats(self):
        # Verifica se o movimento atual criou multiplas ameaças
        # Simulate the move
        game_array = self.game_array

        # Check for multiple threats
        threat_count = 0
        for i in range(3):
            if np.sum(game_array[i, :] == self.player) == 2 and np.sum(game_array[i, :] == 0) == 1:
                threat_count += 1
            if np.sum(game_array[:, i] == self.player) == 2 and np.sum(game_array[:, i] == 0) == 1:
                threat_count += 1
        if np.sum(np.diag(game_array) == self.player) == 2 and np.sum(np.diag(game_array) == 0) == 1:
            threat_count += 1
        if np.sum(np.diag(np.fliplr(game_array)) == self.player) == 2 and np.sum(np.diag(np.fliplr(game_array)) == 0) == 1:
            threat_count += 1

        return threat_count > 1

    def _is_about_to_win(self, player):
        # Verificar linhas e colunas
        for i in range(3):
            if np.sum(self.game_array[i, :] == player) == 2 and np.sum(self.game_array[i, :] == 0) == 1:
                return True
            if np.sum(self.game_array[:, i] == player) == 2 and np.sum(self.game_array[:, i] == 0) == 1:
                return True

        # Verificar diagonais
        if np.sum(np.diag(self.game_array) == player) == 2 and np.sum(np.diag(self.game_array) == 0) == 1:
            return True
        if np.sum(np.diag(np.fliplr(self.game_array)) == player) == 2 and np.sum(np.diag(np.fliplr(self.game_array)) == 0) == 1:
            return True

        return False

    def _player_would_win(self, player, board):
        if self.winner != 'O' and self.winner != 'X':
            for line_indices in self.line_indices_array:  # Itera sobre todas as possíveis linhas vencedoras
                line = board[np.array([i for i, j in line_indices]), np.array([j for i, j in line_indices])]
                if np.all(line == player):
                    return True
        return False

    def change_player(self):
        self.player = -self.player  # Alterna o jogador (0 vira 1 e vice-versa)

    def _find_threat(self, player):
        # Verifica linhas, colunas e diagonais para ameaças
        for i in range(3):
            # Verificar linhas
            if np.sum(self.game_array[i, :] == player) == 2 and np.sum(self.game_array[i, :] == 0) == 1:
                return (i, np.where(self.game_array[i, :] == 0)[0][0])
            # Verificar colunas
            if np.sum(self.game_array[:, i] == player) == 2 and np.sum(self.game_array[:, i] == 0) == 1:
                return (np.where(self.game_array[:, i] == 0)[0][0], i)

        # Verificar diagonais
        if np.sum(np.diag(self.game_array) == player) == 2 and np.sum(np.diag(self.game_array) == 0) == 1:
            idx = np.where(np.diag(self.game_array) == 0)[0][0]
            return (idx, idx)
        if np.sum(np.diag(np.fliplr(self.game_array)) == player) == 2 and np.sum(np.diag(np.fliplr(self.game_array)) == 0) == 1:
            idx = np.where(np.diag(np.fliplr(self.game_array)) == 0)[0][0]
            return (idx, 2 - idx)

        return None

    def random_opponent(self):
        tabuleiro = self.game_array.flatten()
        return np.random.choice(np.where(tabuleiro == 0)[0])

    def _basic_opponent_1(self):
        for i in range(3):
            if np.sum(self.game_array[i, :] == self.player) == 2 and np.sum(self.game_array[i, :] == 0) == 1:
                return np.where(self.game_array[i, :] == 0)[0][0] + i * 3
            if np.sum(self.game_array[:, i] == self.player) == 2 and np.sum(self.game_array[:, i] == 0) == 1:
                return np.where(self.game_array[:, i] == 0)[0][0] * 3 + i
        return self.random_opponent()

    def _basic_opponent_2(self):
        opportunity_position = self._find_threat(self.player)
        if opportunity_position:
            row, col = opportunity_position
            return row * 3 + col
        return self.random_opponent()

    def _advanced_opponent(self):
        player = self.player
        opponent = -player

        # Verifica se o jogador pode ganhar e faça a jogada
        opportunity_position = self._find_threat(player)
        if opportunity_position:
            row, col = opportunity_position
            return row * 3 + col  # Converte a posição 2D para um índice linear

        # Verifica se o oponente está prestes a ganhar e bloqueie
        threat_position = self._find_threat(opponent)
        if threat_position:
            row, col = threat_position
            return row * 3 + col  # Converte a posição 2D para um índice linear

        # Se não houver ameaças ou oportunidades imediatas, faça uma jogada aleatória
        return self.random_opponent()

    def get_opponent_move(self, difficulty):
        if difficulty == 0:
            return self.random_opponent()
        elif difficulty == 1:
            return self._basic_opponent_1()
        elif difficulty == 2:
            return self._basic_opponent_1()
        else:
            return self._advanced_opponent()