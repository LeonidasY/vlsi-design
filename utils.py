import matplotlib.pyplot as plt

# method used to plot the solution
# EX: plot_solution(9, 12, 5, [[3, 3, 4, 0],[2, 4, 7, 0],[2, 8, 7, 4],[3, 9, 4, 3],[4, 12, 0, 0 ]])
def plot_solution(width, height, n_circuits, circuits):
    SIZE = 5
    fig, ax = plt.subplots()

    fig.set_size_inches(SIZE, SIZE * height / width)

    colors = ['tab:red','tab:orange', 'yellow', 'tab:green','tab:blue','tab:purple','tab:brown', 'tab:grey']
    for i in range(n_circuits):
        ax.broken_barh([(circuits[i][2], circuits[i][0])], (circuits[i][3], circuits[i][1]), 
                        facecolors=colors[i % len(colors)], 
                        edgecolors=("black"), 
                        linewidths=(2,),)
    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xticks(range(width + 1))
    ax.set_yticks(range(height + 1))
    ax.grid(color='b', linewidth = 1)
    plt.show()