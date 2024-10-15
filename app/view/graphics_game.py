import pygame as pg

class TicTacToeGraficos:
    def __init__(self, screen):
        self.screen = screen  # Superfície onde os gráficos serão desenhados (a janela do jogo)
        self.WIN_SIZE = 600  # Tamanho da janela (900x900 pixels)
        self.CELL_SIZE = self.WIN_SIZE // 3  # Tamanho de cada célula (300x300 pixels)
        self.vec2 = pg.math.Vector2  # Vetores 2D para facilitar o cálculo de posições
        self.CELL_CENTER = self.vec2(self.CELL_SIZE / 2)  # Centro de cada célula, usado para alinhamento
        # Carregando e escalando as imagens do campo e dos jogadores (X e O)
        self.field_image = self.get_scaled_image(path='resources/field.png', res=[self.WIN_SIZE] * 2)
        self.O_image = self.get_scaled_image(path='resources/o.png', res=[self.CELL_SIZE] * 2)
        self.X_image = self.get_scaled_image(path='resources/x.png', res=[self.CELL_SIZE] * 2)
        # Fonte usada para exibir textos, como o nome do vencedor
        self.font = pg.font.SysFont('Verdana', self.CELL_SIZE // 4, True)


    def draw(self, model):
        self.screen.blit(self.field_image, (0, 0))  # Desenha o campo de jogo no fundo
        self.draw_objects(model)  # Desenha os Xs e Os no tabuleiro
        self.draw_winning_line(model)  # Se houver, desenha a linha vencedora
        self.draw_winner(model)  # Exibe o vencedor ou empate, se o jogo terminou

    
    def draw_objects(self, model):
        for y, row in enumerate(model.game_array):  # Itera sobre as linhas do tabuleiro
            for x, obj in enumerate(row):  # Itera sobre as colunas do tabuleiro
                if obj != model.EMPTY:  # Verifica se a célula está ocupada (não é vazia)
                    # Desenha X ou O de acordo com o valor da célula (X = 1, O = 0)
                    self.screen.blit(self.X_image if obj == 1 else self.O_image, self.vec2(x, y) * self.CELL_SIZE)


    def draw_winning_line(self, model):
        if model.winning_line:  # Verifica se há uma linha vencedora
            start_pos = self.vec2(model.winning_line[0][1], model.winning_line[0][0]) * self.CELL_SIZE + self.CELL_CENTER
            end_pos = self.vec2(model.winning_line[2][1], model.winning_line[2][0]) * self.CELL_SIZE + self.CELL_CENTER
            pg.draw.line(self.screen, 'red', start_pos, end_pos, 10)  # Desenha uma linha vermelha grossa na posição vencedora


    def draw_winner(self, model):
        if model.winner:  # Verifica se há um vencedor ou empate
            if model.winner == 'Draw':  # Se for empate
                label = self.font.render('Draw!', True, 'white', 'black')  # Texto "Draw!" para empate
            else:  # Se houver um vencedor
                label = self.font.render(f'Player "{model.winner}" wins!', True, 'white', 'black')  # Exibe quem ganhou
            # Centraliza e desenha a mensagem no meio da tela
            self.screen.blit(label, (self.WIN_SIZE // 2 - label.get_width() // 2, self.WIN_SIZE // 4))


    @staticmethod
    def get_scaled_image(path, res):
        img = pg.image.load(path)  # Carrega a imagem de um arquivo
        return pg.transform.smoothscale(img, res)  # Redimensiona a imagem para o tamanho especificado