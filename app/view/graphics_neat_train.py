#pip install PyQt5
import matplotlib.pyplot as plt
import numpy as np

# Alterar o backend para Qt5Agg para interatividade no Windows
# plt.switch_backend('Qt5Agg')

# Configurações globais dos gráficos
fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(30, 15))  # 3 linhas e 3 colunas

# Função para configurar os gráficos
def setup_graph():
    ax1.set_title("Fitness por Geração")
    ax1.set_xlabel("Geração")
    ax1.set_ylabel("Fitness")
    
    ax2.set_title("Evolução de Geração Estagnada")
    ax2.set_xlabel("Geração")
    ax2.set_ylabel("Número de Gerações Estagnadas")
    
    ax3.set_title("Frequência de Vitórias por Geração")
    ax3.set_xlabel("Geração")
    ax3.set_ylabel("Quantidade de Vitórias/Empates")
    
    ax4.set_title("Análise de Movimentos Bloqueados")
    ax4.set_xlabel("Geração")
    ax4.set_ylabel("Movimentos Bloqueados")
    
    ax5.set_title("Análise de Multiplas Vitórias")
    ax5.set_xlabel("Geração")
    ax5.set_ylabel("Movimentos Multiplas Vitórias")
  
    plt.subplots_adjust(hspace=0.4, wspace=0.3)  # Ajusta o espaço entre os gráficos

    plt.ion()  # Modo interativo

# Função para atualizar os gráficos
def update_graph(fitness_medio, fitness_maximo, estagnado, vitorias_x, vitorias_o,
                 empates,bloqueios_por_geracao,movimento_multiplas_vitorias):
    ax1.cla()  # Limpar o gráfico 1
    ax1.set_title("Fitness por Geração")
    ax1.set_xlabel("Geração")
    ax1.set_ylabel("Fitness")
    ax1.plot(fitness_medio, label="Fitness Médio")
    ax1.plot(fitness_maximo, label="Fitness Máximo")
    ax1.legend()

    ax2.cla()  # Limpar o gráfico 2
    ax2.set_title("Evolução de Geração Estagnada")
    ax2.set_xlabel("Geração")
    ax2.set_ylabel("Número de Gerações Estagnadas")
    ax2.plot(estagnado, label="Gerações Estagnadas", color='red')
    ax2.legend()

    ax3.cla()  # Limpar o gráfico 3
    ax3.set_title("Frequência de Vitórias por Geração")
    ax3.set_xlabel("Geração")
    ax3.set_ylabel("Quantidade de Vitórias/Empates")
    ax3.plot(vitorias_x, label="Vitórias Player X (IA)", color='blue')
    ax3.plot(vitorias_o, label="Vitórias Player O (Aleatório)", color='orange')
    ax3.plot(empates, label="Empates", color='purple')
    ax3.legend()

    ax4.cla()  # Limpar o gráfico 4
    ax4.set_title("Análise de Movimentos Bloqueados")
    ax4.set_xlabel("Geração")
    ax4.set_ylabel("Movimentos Bloqueados")
    ax4.plot(bloqueios_por_geracao, label="Movimentos Bloqueados", color='green')
    ax4.legend()

    ax5.cla()  # Limpar o gráfico 4
    ax5.set_title("Análise de Multiplas Vitórias")
    ax5.set_xlabel("Geração")
    ax5.set_ylabel("Movimentos de Multiplas Vitórias")
    ax5.plot(movimento_multiplas_vitorias, label="Movimento Com Multiplas Vitórias", color='green')
    ax5.legend()

    plt.pause(0.01)  # Atualiza os gráficos em tempo real

# Função para salvar os gráficos no final
def save_graph():
    plt.ioff()  # Desativa o modo interativo
    plt.savefig("final_graph.png")  # Salva o gráfico final
    plt.show()  # Exibe o gráfico final