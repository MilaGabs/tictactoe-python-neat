class TicTacToeControlador:
    def __init__(self, model, view):
        # O controlador recebe o modelo (lógica do tabuleiro) e a visão (gráficos)
        # para poder mediar as interações entre eles.
        self.model = model  # Referência ao modelo do jogo (tabuleiro e regras)
        self.view = view  # Referência à visão do jogo (parte gráfica)

    def handle_click(self, pos):
        # Este método é chamado quando o jogador clica na tela. Ele converte a posição
        # do clique em coordenadas de célula no tabuleiro e faz a jogada correspondente.
        
        # Converte a posição do clique do mouse (em pixels) para a célula correspondente
        # no tabuleiro, dividindo a coordenada do clique pelo tamanho da célula.
        col, row = [int(x // self.view.CELL_SIZE) for x in pos]
        
        # Chama o método `make_move` do modelo para realizar a jogada na célula clicada.
        # `row` e `col` indicam a linha e a coluna da célula onde a jogada será feita.
        self.model.make_move(row, col)

    def reset_game(self):
        # Este método reinicia o jogo, chamando o método `reset` do modelo para
        # limpar o tabuleiro e começar uma nova partida.
        self.model.reset()