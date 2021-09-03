import os
import matplotlib.pyplot as plt
import re
import math


def import_instances(folder):

    # Method to sort a list alphanumerically
    def sorted_alphanumeric(data):
        convert = lambda text: int(text) if text.isdigit() else text.lower()
        alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
        return sorted(data, key=alphanum_key)
        
    instances = []
    files = sorted_alphanumeric(os.listdir(folder))
    print(files)
    for file in files:
        with open(folder + file) as f:
            content = f.readlines()
            content = [x.strip() for x in content] 
            instances.append(content)
    return instances

def get_variables(instances, number):

    # Get the number of circuits
    circuits = []
    for n in range(int(instances[number][1])):
        circuits.append(f'Circuit {n}')
    
    # Get circuit lengths and heights
    circuit_widths = []
    circuit_heights = []

    for value in instances[number][2:]:
        width, height = value.split(' ')
        circuit_widths.append(int(width))
        circuit_heights.append(int(height))
    
    # Get the maximum width, maximum height and minimum height
    max_width = int(instances[number][0])
    
    total_area = 0
    for n in range(int(instances[number][1])):
        total_area += circuit_widths[n] * circuit_heights[n]
    max_height = sum(circuit_heights)
    min_height = math.ceil(total_area / max_width)
    
    return circuits, circuit_widths, circuit_heights, max_width, max_height, min_height

def get_shapes(circuit_widths, circuit_heights):
    shapes = ''
    valid_shapes = ''
    i = 1
    
    for n in range(len(circuit_widths)):
        if circuit_widths[n] == circuit_heights[n]:
            shapes += f"{{{i}}}, "
            valid_shapes += f"{{{i}}}, "
            i += 1        
        else:
            shapes += f"{{{i}}}, {{{i+1}}}, "
            valid_shapes += f"{{{i}, {i+1}}}, "
            i += 2
    
    shapes = '[' + shapes[:-2] + ']'
    valid_shapes = '[' + valid_shapes[:-2] + ']'
    
    return shapes, valid_shapes
    
def get_rectangles(circuit_widths, circuit_heights):
    rect_size = ''
    rect_offset = ''
    dimensions = []
    
    for n in range(len(circuit_widths)):
        if circuit_widths[n] == circuit_heights[n]:
            rect_size += f"{circuit_widths[n]}, {circuit_heights[n]}|"
            rect_offset += f"{0}, {0}|"
            dimensions.append([circuit_widths[n], circuit_heights[n]])
        
        else:
            rect_size += f"{circuit_widths[n]}, {circuit_heights[n]}|"
            rect_size += f"{circuit_heights[n]}, {circuit_widths[n]}|"
            
            rect_offset += f"{0}, {0}|"
            rect_offset += f"{0}, {0}|"
            
            dimensions.append([circuit_widths[n], circuit_heights[n]])
            dimensions.append([circuit_heights[n], circuit_widths[n]])
    
    rect_size = '[|' + rect_size[:-1] + '|]'
    rect_offset = '[|' + rect_offset[:-1] + '|]' 
    
    return rect_size, rect_offset, dimensions
    
def get_solution(dimensions, x, kind):
    widths = []
    heights = []  
    start_x = []
    start_y = []  
    
    for i, n in enumerate(kind):
        widths.append(dimensions[n-1][0])
        heights.append(dimensions[n-1][1])
        start_x.append(x[i][0])
        start_y.append(x[i][1])
    
    return widths, heights, start_x, start_y 

def get_circuits(circuit_widths, circuit_heights, max_width, min_height, start_x, start_y):
    circuits = []
    for i in range(len(start_x)):
        circuits.append([circuit_widths[i], circuit_heights[i], start_x[i], start_y[i]])
    
    return circuits 

def plot_solution(width, height, circuits, file=None):
    SIZE = 5
    fig, ax = plt.subplots()

    fig.set_size_inches(SIZE, SIZE * height / width)

    colors = ['tab:red','tab:orange', 'yellow', 'tab:green','tab:blue','tab:purple','tab:brown', 'tab:grey']
    for i in range(len(circuits)):
        ax.broken_barh([(circuits[i][2], circuits[i][0])], (circuits[i][3], circuits[i][1]), 
                        facecolors=colors[i % len(colors)], 
                        edgecolors=("black"), 
                        linewidths=(2,),)
    ax.set_ylim(0, height)
    ax.set_xlim(0, width)
    ax.set_xticks(range(width + 1))
    ax.set_yticks(range(height + 1))
    ax.grid(color='b', linewidth = 1)
    
    if file is not None:
        plt.savefig(file)
        plt.close()
    else:
        plt.show()
    
def output_solution(max_width, min_height, widths, heights, start_x, start_y, file):
    solution = [str(max_width), str(min_height)]
    for i in range(len(widths)):
        solution.append(str(widths[i]) + ' ' + str(heights[i]) + ' ' + str(start_x[i]) + ' ' + str(start_y[i]))
    
    with open(file, 'w') as output:
        for item in solution:
            output.write(item)
            output.write('\n') 