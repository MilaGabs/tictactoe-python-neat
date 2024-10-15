import numpy as np
import neat
import pickle
from app.model.board_train import TicTacToeBoard
from app.view.graphics_neat_train import setup_graph, update_graph, save_graph

generation_counter = 0
average_fitness_by_generation = []
max_fitness_maximo_by_generation = []
stagnant_generations = []
x_victories_by_generation = []
o_victories_by_generation = []
draws_by_generation = []
blocks_by_generation = []
victories_multiples_threads = []

class Game:
    def __init__(self):
        self.model = TicTacToeBoard()
        self.moves_blocked = 0
        self.multiple_treads_created = 0

    def run_ai(self, genome, config, difficult):
        net_X = neat.nn.FeedForwardNetwork.create(genome, config)
        self.moves_blocked = 0
        self.multiple_treads_created = 0

        for _ in range(10):
            self.model.reset()
            rounds = 0
            x_is_about_to_win = False

            while not self.model.winner and rounds < 9:
                board = self.model.game_array.flatten()
                # Player 1 == 'X'
                if self.model.player == 1:
                    # while move_not_valid:
                    output_X = net_X.activate(board)
                    output_with_noise = output_X + np.random.normal(0, 0.05, len(output_X))
                    # Aplicar máscara para garantir ações válidas
                    masked_output = np.array(output_with_noise)
                    masked_output[board != 0] = -float('inf')
                    action = np.argmax(masked_output)
                else:
                    action = self.model.get_opponent_move(difficult)

                # Tentar fazer uma jogada em uma célula vazia
                row, col = divmod(action, 3)
                if self.model.game_array[row, col] == self.model.EMPTY:
                    self.model.make_move(row, col)
                    rounds += 1

                if self.model.player == 1:
                    # O oponente esta perto de ganhar
                    if self.model.is_opponent_about_to_win():
                        genome.fitness -= 70

                    # Jogada atual bloqueou o oponente
                    if self.model.moves_block_opponent(action):
                        self.moves_blocked += 1
                        genome.fitness += 40

                    # Jogada atual criou jogadas duplas
                    if self.model.creates_multiple_threats():
                        self.multiple_treads_created += 1
                        genome.fitness += 20

                    if self.model.winner != "X":
                        # Tinha a oportunidade de ganhar mas não ganhou
                        if x_is_about_to_win:
                            genome.fitness -= 90
                        elif self.model.is_x_about_to_win(): # Jogada atual deixou perto de ganhar
                            x_is_about_to_win = True
                            genome.fitness += 30

                elif self.model.winner != 'O' and x_is_about_to_win:
                    # Verifica se o O não bloqueou a jogada na qual ele estava para ganhar
                    x_is_about_to_win = self.model.is_x_about_to_win()

                self.model.change_player()

            self.calculate_fitness(genome, difficult)

    def calculate_fitness(self, genome, difficult):
        winner = self.model.winner
        if winner == 'X':
            genome.fitness += 100 # Recompensa para a vitória
        elif winner == 'O':
            genome.fitness -= 100 # Penalidade por perder
        else: # Verifica a dificuldade do jogo e da a recompensa por empatar
            if difficult == 0:
                genome.fitness += 20
            elif difficult == 1:
                genome.fitness += 30
            elif difficult == 2:
                genome.fitness += 40
            else:
                genome.fitness += 50

def eval_genomes(genomes, config, difficult):
    global generation_counter, average_fitness_by_generation, max_fitness_maximo_by_generation, stagnant_generations
    fitness_values = []
    max_fitness = -float('inf')

    print(f"Running generation {generation_counter}")
    win_X, win_O, draws = 0, 0, 0
    total_blocked_moves = 0
    total_multiple_threads = 0

    for genome_id, genome in genomes:
        if genome.fitness is None:
            genome.fitness = 0

        game = Game()

        game.run_ai(genome, config, difficult)

        fitness_values.append(genome.fitness)

        if genome.fitness > max_fitness:
            max_fitness = genome.fitness

        if game.model.winner == 'X':  # Player X venceu
            win_X += 1
        elif game.model.winner == 'O':  # Player X perdeu
            win_O += 1
        else:  # Empate
            draws += 1

        total_blocked_moves += game.moves_blocked
        total_multiple_threads += game.multiple_treads_created
    x_victories_by_generation.append(win_X)
    o_victories_by_generation.append(win_O)
    draws_by_generation.append(draws)
    blocks_by_generation.append(total_blocked_moves)
    victories_multiples_threads.append(total_multiple_threads)

    # Calcula estagnação de gerações (baseado na diferença de fitness)
    if len(max_fitness_maximo_by_generation) > 0 and max_fitness == max_fitness_maximo_by_generation[-1]:
        stagnant_generations.append(stagnant_generations[-1] + 1 if stagnant_generations else 1)  # Incrementa estagnação
    else:
        stagnant_generations.append(0)  # Reseta se houver mudança no fitness máximo

    # Atualizando os gráficos com a média, máximo do fitness e estagnação
    average_fitness_by_generation.append(np.mean(fitness_values))
    max_fitness_maximo_by_generation.append(max_fitness)

   # Atualiza o gráfico em tempo real
    # update_graph(average_fitness_by_generation, max_fitness_maximo_by_generation, stagnant_generations,
    #              x_victories_by_generation, o_victories_by_generation, draws_by_generation,
    #              blocks_by_generation, victories_multiples_threads)


    # Após o Player X jogar contra os 50 genomas, exibir o resumo
    print(f"Vitórias X: {win_X}, Vitórias O: {win_O}, Empates: {draws}")

    with open('results.csv', 'a') as f:
        f.write(f"Genoma {genome_id}, Vitórias X: {win_X}, Vitórias O: {win_O}, Draws: {draws}\n")

    generation_counter += 1


def run_neat(config):
    population = neat.Population(config)
    generation = 0
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(5, filename_prefix="neat_checkpoint/neat-checkpoint-"))
    population.add_reporter(neat.StatisticsReporter())

    difficult = 0
    fitness_threshold = 1000000
    # setup_graph()
    while generation < 1200:
        if generation < 300:
            difficult = 0
        elif generation < 600:
            difficult = 1
        elif generation < 900:
            difficult = 2
        else:
            difficult = 3

        winner = population.run(lambda genomes, config: eval_genomes(genomes, config, difficult), 1)
        generation += 1

        if winner.fitness >= fitness_threshold:
            print(f"Fitness threshold of {fitness_threshold} reached by genome {winner.key} in generation {generation}.")
            break

    winner = population.best_genome
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    # Salvar o genoma vencedor e a rede neural em um arquivo pickle
    with open("best.pickle", "wb") as f:
        pickle.dump((winner, winner_net), f)
        print("Salvando genoma e rede neural vencedores em 'best.pickle'")

    # save_graph()

if __name__ == '__main__':
    config_path = "config-feedforward.txt"
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    run_neat(config)