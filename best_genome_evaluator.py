import pickle
import numpy as np
from app.model.board_train import TicTacToeBoard
from app.view.graphics_heuristic import plot_results


class Game:
    def __init__(self, player):
        self.model = TicTacToeBoard()
        self.player = player  # O jogador controlado pela IA
        self.opponent = -player  # O oponente da IA

        # Carregar o melhor genoma salvo em best.pickle
        with open("best.pickle", "rb") as f:
            self.best_genome, self.winner_net = pickle.load(f)

    def run_ai(self):
        num_generations = 100
        num_games_per_generation = 100
        x_wins, o_wins, draws = self.simulate_generations(num_generations, num_games_per_generation)

        plot_results(num_generations, x_wins, o_wins, draws)

    def find_threat(self, game_array, player):
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

    def random_move(self, game):
        # Escolhe uma jogada aleatória entre as posições disponíveis
        available_moves = [i for i in range(9) if game[divmod(i, 3)] == 0]
        return np.random.choice(available_moves)

    def basic_opponent_1(self, game_array):
        for i in range(3):
            if np.sum(game_array[i, :] == 1) == 2 and np.sum(game_array[i, :] == 0) == 1:
                return np.where(game_array[i, :] == 0)[0][0] + i * 3
            if np.sum(game_array[:, i] == 1) == 2 and np.sum(game_array[:, i] == 0) == 1:
                return np.where(game_array[:, i] == 0)[0][0] * 3 + i
        return self.random_move(game_array)

    def basic_opponent_2(self, game_array):
        opportunity_position = self.find_threat(game_array, 1)
        if opportunity_position:
            row, col = opportunity_position
            return row * 3 + col
        return self.random_move(game_array)

    def advanced_opponent(self, game_array):
        # Verifica se o jogador pode ganhar e faça a jogada
        opportunity_position = self.find_threat(game_array, 1)
        if opportunity_position:
            row, col = opportunity_position
            return row * 3 + col  # Converte a posição 2D para um índice linear

        # Verifica se o oponente está prestes a ganhar e bloqueie
        threat_position = self.find_threat(game_array, -1)
        if threat_position:
            row, col = threat_position
            return row * 3 + col  # Converte a posição 2D para um índice linear

        # Se não houver ameaças ou oportunidades imediatas, faça uma jogada aleatória
        return self.random_move(game_array)

    def choose_opponent(self, generation):
        if generation < 20:
            return self.random_move
        elif generation < 40:
            return self.basic_opponent_1
        elif generation < 60:
            return self.basic_opponent_2
        else:
            return self.advanced_opponent

    def evaluate_best_genome(self, gen):
        results = {"vitórias": 0, "derrotas": 0, "empates": 0}
        block_moves_1 = 0
        multiplas_vitorias_1 = 0
        opponent = self.choose_opponent(gen)

        for _ in range(100):  # Joga 100 partidas por geração
            self.model.reset()  # Resetar o tabuleiro para uma nova partida
            rounds = 0

            while not self.model.winner and rounds < 9:  # Limitando a 9 rodadas
                tabuleiro = self.model.game_array.flatten()

                if self.model.player == 1:
                    output = self.winner_net.activate(tabuleiro)
                    masked_output = np.array(output)
                    masked_output[tabuleiro != 0] = -float('inf')
                    action = np.argmax(masked_output)
                else:
                    action = opponent(self.model.game_array)

                # Tentar fazer uma jogada em uma célula vazia
                row, col = divmod(action, 3)
                if self.model.game_array[row, col] == self.model.EMPTY:
                    self.model.make_move(row, col)
                    rounds += 1  # Incrementar o contador de rodadas

                    if self.model.player == 1:
                        if self.model.moves_block_opponent(action):
                            block_moves_1 += 1
                        if self.model.creates_multiple_threats():
                            multiplas_vitorias_1 += 1
                self.model.change_player()

            # Atualizar resultados
            if self.model.winner == 'X':
                results["vitórias"] += 1
            elif self.model.winner == 'O':
                results["derrotas"] += 1
            else:
                results["empates"] += 1

        return results

    def simulate_generations(self, num_generations, num_games_per_generation):
        x_wins = []
        o_wins = []
        draws = []

        for gen in range(num_generations):
            results = self.evaluate_best_genome(gen)
            x_wins.append(results['vitórias'])
            o_wins.append(results['derrotas'])
            draws.append(results['empates'])
            print(f"Boclo de partidas: {gen}")
        return x_wins, o_wins, draws


if __name__ == "__main__":
    player = 1  # Definir o jogador controlado pela IA
    game = Game(player)
    game.run_ai()
