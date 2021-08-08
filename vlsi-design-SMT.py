from itertools import combinations
from utils import import_instances, plot_solution, output_solution
import time
from z3 import *

## Data Input

instances = import_instances('input/instances/')

# Functions

def get_variables(instance_number):
    # Get the number of blocks
    number_of_blocks = int(instances[instance_number][1])
    
    # Get block lengths and heights
    blocks_width = []
    blocks_height = []

    for value in instances[instance_number][2:]:
        width, height = value.split(' ')
        blocks_width.append(int(width))
        blocks_height.append(int(height))  

    width = int(instances[instance_number][0])
    return number_of_blocks, blocks_width, blocks_height, width

## Z3 SMT Code

def vlsi(s, height):    
    # 9x9 matrix of integer variables
    v = [[Int(f"x_{i}_{dim}") for dim in [0,1]] for i in range(number_of_blocks) ]


    inside = []
    inside += [(And(v[n][0] + blocks_width[n] <= width, v[n][0] >= 0,
                    v[n][1] + blocks_height[n] <= height, v[n][1] >= 0)) for n in range(number_of_blocks)]

    overlap = []
    for n in range(number_of_blocks):
        for m in range(n + 1, number_of_blocks):
            overlap.append((Or (v[n][0] + blocks_width[n] <= v[m][0],
                                v[m][0] + blocks_width[m] <= v[n][0],
                                v[n][1] + blocks_height[n] <= v[m][1],
                                v[m][1] + blocks_height[m] <= v[n][1])))

    vlsi_model = inside + overlap

    s.add(vlsi_model)
    
    if s.check() == sat:
        m = s.model()
        answer = [[int(m.evaluate(v[i][j]).as_string()) for j in range(2)] for i in range(number_of_blocks)]
        return answer
    else:
        print("Failed to solve")

start = time.time()
middle = start
for instance_number in range(20, len(instances)):
    print("Solved instance %i in %f seconds (%f sec)" %((instance_number), (time.time() - start), (time.time() - middle)))	
    print("Solving instance: ", instance_number)
    number_of_blocks, blocks_width, blocks_height, width = get_variables(instance_number)
    starting_height = int(math.ceil(sum([blocks_width[i] * blocks_height[i] for i in range(number_of_blocks)]) / width))
    height_i = starting_height
    s = Solver()

    times = 300 * 1000 # 300 sec
    s.set(timeout=times)

    middle = time.time()
    sol = vlsi(s, height_i)
        
    if (sol) :
        start_x = []
        start_y = []
        for j in range(len(sol)):
            start_x.append(int(sol[j][0]))
            start_y.append(int(sol[j][1]))
        circuits = [[blocks_width[i], blocks_height[i], start_x[i], start_y[i]] for i in range(number_of_blocks)]
        plot_solution(width, height_i, circuits, f'output/SMT/images/out-{instance_number + 1}.png')
        output_solution(instances[instance_number], height_i, start_x, start_y, f'output/SMT/solutions/out-{instance_number + 1}.txt')