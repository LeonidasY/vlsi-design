import os
import matplotlib.pyplot as plt

# Method to import the instances
# EX: import_instances('input/instances/')
def import_instances(folder):
    instances = []
    files = os.listdir(folder)
    for file in files:
        with open(folder + file) as f:
            content = f.readlines()
            content = [x.strip() for x in content] 
            instances.append(content)
    return instances
    
# Method to output the solution
# EX: output_solution('output/cp/out-0.txt', ['8', '4', '3 3', '3 5', '5 3', '5 5'], [5, 5, 0, 0], [5, 0, 5, 0], 8)
def output_solution(file, instance, start_x, start_y, end_y):
    solution = []
    for i, x in enumerate(instance):
        if i == 0:
            solution.append(x + ' ' + str(end_y))
        elif i == 1:
            solution.append(x)
        else:
            solution.append(x + ' ' + str(start_x[i-2]) + ' ' + str(start_y[i-2]))
    
    print(solution)
    
    with open(file, 'w') as output:
        for item in solution:
            output.write(item)
            output.write('\n')

# Method used to plot the solution
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