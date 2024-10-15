import pygame as pg
import sys
from app.model.board import TicTacToeBoard
from app.view.graphics_game import TicTacToeGraficos
from app.controller.controller import TicTacToeControlador


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode([600] * 2)
        self.clock = pg.time.Clock()
        self.model = TicTacToeBoard()
        self.view = TicTacToeGraficos(self.screen)
        self.controller = TicTacToeControlador(self.model, self.view)

    def new_game(self):
        self.model.reset()

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                self.new_game()
            if event.type == pg.MOUSEBUTTONDOWN:
                self.controller.handle_click(pg.mouse.get_pos())

    def run(self):
        while True:
            self.check_events()
            self.view.draw(self.model)
            pg.display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()