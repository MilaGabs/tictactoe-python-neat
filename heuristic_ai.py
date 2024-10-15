import numpy as np
from random import choice
from app.model.board import TicTacToeBoard  # Importando a classe do tabuleiro
from app.view.graphics_heuristic import plot_results

class HeuristicAI:
    def __init__(self, player):
        self.player = player  # O jogador controlado pela IA
        self.opponent = -player  # O oponente da IA

    def choose_move(self, game):
        # Tenta encontrar a melhor jogada para o jogador atual (self.player)
        # 1. Verifica se pode vencer imediatamente
        for move in self.get_available_moves(game):
            if self.is_winning_move(game, move, self.player):
                return move

        # 2. Bloqueia o oponente se ele estiver prestes a vencer
        for move in self.get_available_moves(game):
            if self.is_winning_move(game, move, self.opponent):
                return move

        # 3. Joga no centro se disponível
        if game[1, 1] == 0:
            return 4  # Posição (1, 1) é a posição central em um tabuleiro 3x3

        # 4. Joga em um canto se disponível
        for move in [0, 2, 6, 8]:  # Posições dos cantos
            row, col = divmod(move, 3)
            if game[row, col] == 0:
                return move

        # 5. Se nada disso, joga em qualquer posição disponível
        return choice(self.get_available_moves(game))

    def is_winning_move(self, game, move, player):
        # Verifica se fazer essa jogada levará à vitória para o jogador
        row, col = divmod(move, 3)
        temp_game = game.copy()
        temp_game[row, col] = player

        # Verifica linhas, colunas e diagonais
        for i in range(3):
            if np.all(temp_game[i, :] == player):  # Linha
                return True
            if np.all(temp_game[:, i] == player):  # Coluna
                return True
        if np.all(np.diag(temp_game) == player):  # Diagonal principal
            return True
        if np.all(np.diag(np.fliplr(temp_game)) == player):  # Diagonal secundária
            return True

        return False

    def get_available_moves(self, game):
        # Retorna uma lista de todas as posições disponíveis no tabuleiro
        return [i for i in range(9) if game[divmod(i, 3)] == 0]

def find_threat(game_array, player):
    for i in range(3):
        if np.sum(game_array[i, :] == player) == 2 and np.sum(game_array[i, :] == 0) == 1:
            return (i, np.where(game_array[i, :] == 0)[0][0])
        if np.sum(game_array[:, i] == player) == 2 and np.sum(game_array[:, i] == 0) == 1:
            return (np.where(game_array[:, i] == 0)[0][0], i)

    if np.sum(np.diag(game_array) == player) == 2 and np.sum(np.diag(game_array) == 0) == 1:
        idx = np.where(np.diag(game_array) == 0)[0][0]
        return (idx, idx)
    if np.sum(np.diag(np.fliplr(game_array)) == player) == 2 and np.sum(np.diag(np.fliplr(game_array)) == 0) == 1:
        idx = np.where(np.diag(np.fliplr(game_array)) == 0)[0][0]
        return (idx, 2 - idx)

    return None

def random_move(game):
    # Escolhe uma jogada aleatória entre as posições disponíveis
    available_moves = [i for i in range(9) if game[divmod(i, 3)] == 0]
    return choice(available_moves)

def basic_opponent_1(game_array):
    for i in range(3):
        if np.sum(game_array[i, :] == 1) == 2 and np.sum(game_array[i, :] == 0) == 1:
            return np.where(game_array[i, :] == 0)[0][0] + i * 3
        if np.sum(game_array[:, i] == 1) == 2 and np.sum(game_array[:, i] == 0) == 1:
            return np.where(game_array[:, i] == 0)[0][0] * 3 + i
    return random_move(game_array)

def basic_opponent_2(game_array):
    opportunity_position = find_threat(game_array, 1)
    if opportunity_position:
        row, col = opportunity_position
        return row * 3 + col
    return random_move(game_array)

def advanced_opponent(game_array):
    # Verifica se o jogador pode ganhar e faça a jogada
    opportunity_position = find_threat(game_array, 1)
    if opportunity_position:
        row, col = opportunity_position
        return row * 3 + col  # Converte a posição 2D para um índice linear

    # Verifica se o oponente está prestes a ganhar e bloqueie
    threat_position = find_threat(game_array, -1)
    if threat_position:
        row, col = threat_position
        return row * 3 + col  # Converte a posição 2D para um índice linear

    # Se não houver ameaças ou oportunidades imediatas, faça uma jogada aleatória
    return random_move(game_array)

def choose_opponent(generation):
    if generation < 20:
        return random_move
    elif generation < 40:
        return basic_opponent_1
    elif generation < 60:
        return basic_opponent_2
    else:
        return advanced_opponent

def play_game(generation):
    # Inicializa o tabuleiro e as IAs
    tabuleiro = TicTacToeBoard()
    ai = HeuristicAI(player=1)  # Player 1 (X) é controlado pela IA
    opponent_function = choose_opponent(generation)

    # Loop do jogo até que haja um vencedor ou empate
    while not tabuleiro.winner:
        if tabuleiro.player == 1:  # Vez da IA
            move = ai.choose_move(tabuleiro.game_array)
            row, col = divmod(move, 3)
            tabuleiro.make_move(row, col)

        else:  # Vez do oponente aleatório (player -1)
            move = opponent_function(tabuleiro.game_array)
            row, col = divmod(move, 3)
            tabuleiro.make_move(row, col)

        # Verifica o vencedor
        if tabuleiro.winner:
            return tabuleiro.winner

def simulate_generation(num_games, generation):
    victories = {"X": 0, "O": 0, "Draw": 0}  # Estatísticas de vitórias

    for _ in range(num_games):
        winner = play_game(generation)
        victories[winner] += 1  # Atualiza o contador de vitórias
    return victories

def simulate_generations(num_generations, num_games_per_generation):
    x_wins = []
    o_wins = []
    draws = []

    for gen in range(num_generations):
        results = simulate_generation(num_games_per_generation, gen)
        x_wins.append(results['X'])
        o_wins.append(results['O'])
        draws.append(results['Draw'])
        print (f"Geração:{gen}")
    return x_wins, o_wins, draws

# Simulação de 100 gerações com 100 jogos cada
num_generations = 100
num_games_per_generation = 100
x_wins, o_wins, draws = simulate_generations(num_generations, num_games_per_generation)

plot_results(num_generations, x_wins, o_wins, draws)
