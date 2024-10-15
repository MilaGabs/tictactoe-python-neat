import matplotlib.pyplot as plt

def plot_results(num_generations, x_wins, o_wins, draws):
    # Geração de gráficos
    plt.figure(figsize=(10, 6))

    # Gráfico de vitórias
    plt.plot(range(num_generations), x_wins, label='Vitórias da IA (X)', color='blue', marker='o')
    plt.plot(range(num_generations), o_wins, label='Vitórias do Oponente Aleatório (O)', color='red', marker='x')
    plt.plot(range(num_generations), draws, label='Empates', color='green', marker='s')

    # Configurações do gráfico
    plt.title('Resultados das Gerações de Jogos da IA vs Oponente')
    plt.xlabel('Gerações')
    plt.ylabel('Número de Jogos')
    plt.legend()
    plt.grid(True)

    # Exibe o gráfico
    plt.show()
