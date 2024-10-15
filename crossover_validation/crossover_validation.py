import numpy as np
import neat
from itertools import product
import pandas as pd
import sys
import os

# Obtém o diretório do script atual
current_dir = os.path.dirname(os.path.abspath(__file__))
# Define o caminho da raiz do projeto baseado no diretório atual
project_root = os.path.abspath(os.path.join(current_dir, '..'))
# Adiciona o caminho da raiz do projeto ao sys.path
sys.path.append(project_root)
# Agora a importação deve funcionar em qualquer máquina
from app.model.board_train import TicTacToeBoard

numero_config = 0  # Inicializa aqui
generation_counter = 0


class Game:
    def __init__(self):
        self.model = TicTacToeBoard()
        self.invalid_moves = 0  # Adiciona o contador de movimentos inválidos aqui
        self.block_moves = 0
        self.multiplas_vitorias = 0

    def run_ai(self, genome, config, opponent_function, difficult):
        net_X = neat.nn.FeedForwardNetwork.create(genome, config)
        invalid_moves_1 = 0
        block_moves_1 = 0
        multiplas_vitorias_1 = 0

        for _ in range(10):  # Joga 10 jogos
            self.model.reset()
            rounds = 0
            x_is_about_to_win = False

            while not self.model.winner and rounds < 9:
                board = self.model.game_array.flatten()

                if self.model.player == 1:

                    # while move_not_valid:
                    output_X = net_X.activate(board)
                    output_with_noise = output_X + np.random.normal(0, 0.1, len(output_X))
                    # Aplicar máscara para garantir ações válidas
                    masked_output = np.array(output_with_noise)
                    masked_output[board != 0] = -float('inf')
                    action = np.argmax(masked_output)

                else:  # Jogada aleatória para o player O
                    action = opponent_function(self.model)

                row, col = divmod(action, 3)
                if self.model.game_array[row, col] == self.model.EMPTY:
                    self.model.make_move(row, col)
                    rounds += 1

                if self.model.player == 1:
                    if self.model.is_opponent_about_to_win():
                        genome.fitness -= 50

                    if self.model.moves_block_opponent(action):
                        genome.fitness += 30
                        block_moves_1 += 1

                    if self.model.creates_multiple_threats():
                        genome.fitness += 20
                        multiplas_vitorias_1 += 1

                    if self.model.winner != "X":
                        # Tinha a oportunidade de ganhar mas não ganhou
                        if x_is_about_to_win:
                            genome.fitness -= 60
                        elif self.model.is_x_about_to_win(): # Jogada atual deixou perto de ganhar
                            x_is_about_to_win = True
                            genome.fitness += 20
                elif self.model.winner != 'O' and x_is_about_to_win:
                    # Verifica se o O não bloqueou a jogada na qual ele estava para ganhar
                    x_is_about_to_win = self.model.is_x_about_to_win()

                self.model.change_player()

            self.calculate_fitness(genome, difficult)

        self.invalid_moves = invalid_moves_1  # Atualiza o total de movimentos inválidos para essa instância de jogo
        self.block_moves = block_moves_1
        self.multiplas_vitorias = multiplas_vitorias_1

    def calculate_fitness(self, genome, difficult):
        winner = self.model.winner
        if winner == 'X':
            genome.fitness += 100 # Recompensa para a vitória
        elif winner == 'O':
            genome.fitness -= 30 # Penalidade por perder
        else: # Verifica a dificuldade do jogo e da a recompensa por empatar
            if difficult == 0:
                genome.fitness += 10
            elif difficult == 1:
                genome.fitness += 20
            elif difficult == 2:
                genome.fitness += 30
            else:
                genome.fitness += 40
def find_threat(game_array, player):
    # Verifica linhas, colunas e diagonais para ameaças
    for i in range(3):
        # Verificar linhas
        if np.sum(game_array[i, :] == player) == 2 and np.sum(game_array[i, :] == 0) == 1:
            return (i, np.where(game_array[i, :] == 0)[0][0])
        # Verificar colunas
        if np.sum(game_array[:, i] == player) == 2 and np.sum(game_array[:, i] == 0) == 1:
            return (np.where(game_array[:, i] == 0)[0][0], i)

    # Verificar diagonais
    if np.sum(np.diag(game_array) == player) == 2 and np.sum(np.diag(game_array) == 0) == 1:
        idx = np.where(np.diag(game_array) == 0)[0][0]
        return (idx, idx)
    if np.sum(np.diag(np.fliplr(game_array)) == player) == 2 and np.sum(np.diag(np.fliplr(game_array)) == 0) == 1:
        idx = np.where(np.diag(np.fliplr(game_array)) == 0)[0][0]
        return (idx, 2 - idx)

    return None

def random_opponent(model):
    tabuleiro = model.game_array.flatten()
    return np.random.choice(np.where(tabuleiro == 0)[0])

def basic_opponent_1(model):
    for i in range(3):
        if np.sum(model.game_array[i, :] == model.player) == 2 and np.sum(model.game_array[i, :] == 0) == 1:
            return np.where(model.game_array[i, :] == 0)[0][0] + i * 3
        if np.sum(model.game_array[:, i] == model.player) == 2 and np.sum(model.game_array[:, i] == 0) == 1:
            return np.where(model.game_array[:, i] == 0)[0][0] * 3 + i
    return random_opponent(model)

def basic_opponent_2(model):
    opportunity_position = find_threat(model.game_array, model.player)
    if opportunity_position:
        row, col = opportunity_position
        return row * 3 + col
    return random_opponent(model)

def advanced_opponent(model):
    player = model.player
    opponent = -player

    # Verifica se o jogador pode ganhar e faça a jogada
    opportunity_position = find_threat(model.game_array, player)
    if opportunity_position:
        row, col = opportunity_position
        return row * 3 + col  # Converte a posição 2D para um índice linear

    # Verifica se o oponente está prestes a ganhar e bloqueie
    threat_position = find_threat(model.game_array, opponent)
    if threat_position:
        row, col = threat_position
        return row * 3 + col  # Converte a posição 2D para um índice linear

    # Se não houver ameaças ou oportunidades imediatas, faça uma jogada aleatória
    return random_opponent(model)

def adversarial_opponent(model, genome, config):
    # Joga contra uma versão de si mesma
    net_O = neat.nn.FeedForwardNetwork.create(genome, config)
    tabuleiro = model.game_array.flatten()
    output_O = net_O.activate(tabuleiro)
    action = output_O.index(max(output_O))
    if tabuleiro[action] == 0:
        return action
    else:
        return random_opponent(model)

def eval_genomes(genomes, config,opponent_function, difficult):
    global generation_counter, vitorias_x_por_geracao, vitorias_o_por_geracao, empates_por_geracao
    global movimentos_invalidos_por_geracao, bloqueios_por_geracao, movimento_multiplas_vitorias

    max_fitness = -float('inf')
    win_X, win_O, draws = 0, 0, 0
    invalid_moves_total = 0  # Adiciona contador de movimentos inválidos para a geração
    blocked_moves_total = 0
    multiplas_vitorias_total = 0

    for genome_id, genome in genomes:
        if genome.fitness is None:
            genome.fitness = 0

        game = Game()
        if difficult == 4:
            opponent = lambda model: adversarial_opponent(model, genome, config)
        else:
            opponent = opponent_function

        game.run_ai(genome, config, opponent, difficult)

        if genome.fitness > max_fitness:
            max_fitness = genome.fitness

        generation_counter += 1
        if game.model.winner == 'X':  # Player X venceu
            win_X += 1
        elif game.model.winner == 'O':  # Player X perdeu
            win_O += 1
        else:  # Empate
            draws += 1

        invalid_moves_total += game.invalid_moves  # Soma os movimentos inválidos do jogo atual
        blocked_moves_total += game.block_moves
        multiplas_vitorias_total += game.multiplas_vitorias
    vitorias_x_por_geracao = win_X
    vitorias_o_por_geracao = win_O
    empates_por_geracao = draws
    movimentos_invalidos_por_geracao = invalid_moves_total  # Adiciona ao array global
    bloqueios_por_geracao = blocked_moves_total
    movimento_multiplas_vitorias = multiplas_vitorias_total

def ajustar_configuracoes(config_path, pop_size, mutate_rate, gene_add_prob, gene_delete_prob, node_add_prob,
                          crossover_rate, num_hidden, compatibility_weight_coefficient, compatibility_disjoint_coefficient, response_mutate_rate, bias_mutate_rate, bias_init_mean, aggregation_mutate_rate):
    global numero_config  # Declare que vai usar a variável global

    with open(config_path, 'r') as file:
        config_data = file.readlines()

    for i, line in enumerate(config_data):
        if line.startswith("pop_size"):
            config_data[i] = f"pop_size = {pop_size}\n"
        elif line.startswith("mutate_rate"):
            config_data[i] = f"mutate_rate = {mutate_rate}\n"
        elif line.startswith("gene_add_prob"):
            config_data[i] = f"gene_add_prob = {gene_add_prob}\n"
        elif line.startswith("gene_delete_prob"):
            config_data[i] = f"gene_delete_prob = {gene_delete_prob}\n"
        elif line.startswith("node_add_prob"):
            config_data[i] = f"node_add_prob = {node_add_prob}\n"
        elif line.startswith("crossover_rate"):
            config_data[i] = f"crossover_rate = {crossover_rate}\n"
        elif line.startswith("num_hidden"):
            config_data[i] = f"num_hidden = {num_hidden}\n"
        elif line.startswith("compatibility_weight_coefficient"):
            config_data[i] = f"compatibility_weight_coefficient = {compatibility_weight_coefficient}\n"
        elif line.startswith("compatibility_disjoint_coefficient"):
            config_data[i] = f"compatibility_disjoint_coefficient = {compatibility_disjoint_coefficient}\n"
        elif line.startswith("response_mutate_rate"):
            config_data[i] = f"response_mutate_rate = {response_mutate_rate}\n"
        elif line.startswith("bias_mutate_rate"):
            config_data[i] = f"bias_mutate_rate = {bias_mutate_rate}\n"
        elif line.startswith("bias_init_mean"):
            config_data[i] = f"bias_init_mean = {bias_init_mean}\n"
        elif line.startswith("aggregation_mutate_rate"):
            config_data[i] = f"aggregation_mutate_rate = {aggregation_mutate_rate}\n"

    numero_config += 1
    new_config_path = f"crossover_validation/config_validacao/config-feedforward-{pop_size}-{mutate_rate}-{gene_add_prob}-{gene_delete_prob}-{numero_config}.txt"
    with open(new_config_path, 'w') as file:
        file.writelines(config_data)

    return new_config_path

def validacao_cruzada(config_path_base, parametros, nome_arquivo):
    combinacoes = list(product(*parametros.values()))

    for (pop_size, mutate_rate, gene_add_prob, gene_delete_prob, node_add_prob, num_generations,
         crossover_rate, num_hidden, compatibility_weight_coefficient, compatibility_disjoint_coefficient, response_mutate_rate, bias_mutate_rate, bias_init_mean, aggregation_mutate_rate) in combinacoes:
        print(f"Treinando com pop_size={pop_size}, mutate_rate={mutate_rate}, gene_add_prob={gene_add_prob}, "
              f"gene_delete_prob={gene_delete_prob}, node_add_prob={node_add_prob}, num_generations={num_generations}, "
              f"crossover_rate={crossover_rate}, num_hidden={num_hidden}, compatibility_weight_coefficient={compatibility_weight_coefficient}, compatibility_disjoint_coefficient={compatibility_disjoint_coefficient}, "
              f"response_mutate_rate={response_mutate_rate}, bias_mutate_rate={bias_mutate_rate}, bias_init_mean={bias_init_mean},aggregation_mutate_rate={aggregation_mutate_rate} ")
        generation = 0

        config_path = ajustar_configuracoes(config_path_base, pop_size, mutate_rate, gene_add_prob, gene_delete_prob, node_add_prob,
                                            crossover_rate, num_hidden, compatibility_weight_coefficient, compatibility_disjoint_coefficient, response_mutate_rate, bias_mutate_rate, bias_init_mean, aggregation_mutate_rate)
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.StatisticsReporter())

        difficult = 0

        if generation < 120:
            difficult = 0
            opponent_function = random_opponent
        elif generation < 20:
            difficult = 1
            opponent_function = basic_opponent_1
        elif generation < 40:
            difficult = 2
            opponent_function = basic_opponent_2
        elif generation < 60:
            difficult = 3
            opponent_function = advanced_opponent
        else:
            difficult = 4
            opponent_function = adversarial_opponent

        winner = population.run(lambda genomes, config: eval_genomes(genomes, config, opponent_function, difficult), num_generations)

        generation += 1

        resultado = {
                'numero': numero_config,
                'Pop Size': pop_size,
                'Mutate Rate': mutate_rate,
                'gene_add_prob': gene_add_prob,
                'gene_delete_prob': gene_delete_prob,
                'node_add_prob': node_add_prob,
                'Generations': num_generations,
                'crossover_rate': crossover_rate,
                'num_hidden': num_hidden,
                'compatibility_weight_coefficient': compatibility_weight_coefficient,
                'compatibility_disjoint_coefficient': compatibility_disjoint_coefficient,
                'response_mutate_rate': response_mutate_rate,
                'bias_mutate_rate': bias_mutate_rate,
                'bias_init_mean': bias_init_mean,
                'aggregation_mutate_rate': aggregation_mutate_rate,
                'Vitórias X': vitorias_x_por_geracao,  # Certifique-se de que essas variáveis estão definidas corretamente
                'Vitórias O': vitorias_o_por_geracao,
                'Empates': empates_por_geracao,
                'Movimentos Inválidos': movimentos_invalidos_por_geracao,
                'Bloqueios': bloqueios_por_geracao,
                'Múltiplas Vitórias': movimento_multiplas_vitorias,
                'Winner Fitness': winner.fitness
            }
        df_resultado = pd.DataFrame([resultado])
        df_resultado.to_csv(nome_arquivo, index=False, mode='a', header=False)  # Modo append ('a')

    # Após todas as iterações, ordenar o CSV pelo 'Winner Fitness' (do maior para o menor)
    df_final = pd.read_csv(nome_arquivo)
    df_final_ordenado = df_final.sort_values(by='Winner Fitness', ascending=False)

    # Salvar o arquivo ordenado
    df_final_ordenado.to_csv(nome_arquivo, index=False)


if __name__ == '__main__':
    config_path_base = "config-feedforward.txt"

    parametros = {
        'pop_size': [100],
        'mutate_rate': [0.1, 0.2],
        'gene_add_prob': [0.2, 0.3],
        'gene_delete_prob': [0.1, 0.2],
        'node_add_prob': [0.2, 0.3],
        'num_generations': [121],
        'crossover_rate': [0.7],
        'num_hidden': [6, 8],
        'compatibility_weight_coefficient': [0.5, 0.9],
        'compatibility_disjoint_coefficient': [0.5, 0.9],
        'response_mutate_rate': [0.3],
        'bias_mutate_rate': [0.5],
        'bias_init_mean': [0.1],
        'aggregation_mutate_rate': [ 0.05]
    }

    nome_arquivo = 'crossover_validation/list_config_feedforwards.csv'

    # Criar o arquivo CSV e adicionar o cabeçalho (somente na primeira vez)
    colunas = [
        'numero', 'Pop Size', 'Mutate Rate', 'gene_add_prob', 'gene_delete_prob', 'node_add_prob',
        'Generations', 'crossover_rate', 'num_hidden',
        'compatibility_weight_coefficient', 'compatibility_disjoint_coefficient',
        'response_mutate_rate', 'bias_mutate_rate', 'bias_init_mean', 'aggregation_mutate_rate',
        'Vitórias X', 'Vitórias O', 'Empates', 'Movimentos Inválidos', 'Bloqueios',
        'Múltiplas Vitórias', 'Winner Fitness'
    ]

    # Escrever o cabeçalho no CSV apenas uma vez, antes do loop
    df_vazio = pd.DataFrame(columns=colunas)
    df_vazio.to_csv(nome_arquivo, index=False, mode='w')

    validacao_cruzada(config_path_base, parametros, nome_arquivo)