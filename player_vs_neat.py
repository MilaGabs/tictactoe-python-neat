import pygame as pg
import sys
import numpy as np
import pickle
from app.model.board import TicTacToeBoard
from app.view.graphics_game import TicTacToeGraficos
from app.controller.controller import TicTacToeControlador

class Game:
    def __init__(self):
        pg.init()  # Inicializa o Pygame
        self.screen = pg.display.set_mode([600] * 2)  # Define a tela do jogo com tamanho 900x900 pixels
        self.clock = pg.time.Clock()  # Cria um relógio para controlar a taxa de quadros
        self.model = TicTacToeBoard()  # Instancia o "modelo" (a lógica do jogo)
        self.view = TicTacToeGraficos(self.screen)  # Instancia a "visualização" (parte gráfica do jogo)
        self.controller = TicTacToeControlador(self.model, self.view)  # Instancia o "controlador" (controle da lógica e interface)

        # Carregar o genoma e a rede neural
        with open("best.pickle", "rb") as f:
            winner_genome, self.winner_net = pickle.load(f)


    def new_game(self):
        self.model.reset()  # Reseta o estado do jogo para começar uma nova partida

    def check_events(self):
        for event in pg.event.get():  # Itera sobre a lista de eventos (ações do usuário)
            if event.type == pg.QUIT:  # Verifica se o jogador fechou a janela
                pg.quit()  # Fecha o Pygame
                sys.exit()  # Sai do programa
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:  # Verifica se a tecla espaço foi pressionada
                self.new_game()  # Reinicia o jogo
            if event.type == pg.MOUSEBUTTONDOWN:  # Verifica se o jogador clicou em algum lugar
                self.controller.handle_click(pg.mouse.get_pos())  # Envia o evento de clique ao controlador

    def ai_move(self):
        """Função para a IA fazer uma jogada"""
        board = self.model.game_array.flatten()
        output = self.winner_net.activate(board)
        masked_output = np.array(output)
        masked_output[board != 0] = -float('inf')
        action = np.argmax(masked_output)

        row, col = divmod(action, 3)  # Converte a posição linear em coordenadas (linha, coluna)
        if self.model.game_array[row][col] == self.model.EMPTY:  # Verifica se a célula está vazia
            self.model.make_move(row, col)  # A IA faz a jogada
            print(f"IA fez a jogada: ({row}, {col})")
            return

        # Se a IA não conseguiu encontrar uma jogada válida
        print("IA não conseguiu encontrar uma jogada válida.")


    def run(self, play_with_ai=False):
        while True:  # Loop principal do jogo
            self.check_events()  # Verifica e lida com eventos

            if play_with_ai and self.model.player == 1:  # Se for a vez da IA
                if not self.model.winner:  # Verifica se o jogo ainda está em andamento
                    self.ai_move()  # A IA faz sua jogada
                else:
                    print("Jogo já concluído. A IA não pode jogar.")

            self.view.draw(self.model)  # Atualiza a tela com base no estado do jogo
            pg.display.update()  # Atualiza a tela do Pygame
            self.clock.tick(60)  # Limita a execução a 60 quadros por segundo

if __name__ == '__main__':
    game = Game()
    game.run(play_with_ai=True)