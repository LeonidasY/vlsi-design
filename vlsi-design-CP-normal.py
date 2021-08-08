# Import the necessary libraries
from tqdm import tqdm
from utils import import_instances, plot_solution, output_solution
import time
from datetime import timedelta
from minizinc import Instance, Model, Solver
gecode = Solver.lookup("gecode")

## Data Input

instances = import_instances('input/instances/')

## Functions

def get_variables(instances, number):
    # Get the number of blocks
    blocks = []
    for n in range(int(instances[number][1])):
        blocks.append(f'Block {n}')
    
    # Get block lengths and heights
    block_widths = []
    block_heights = []

    for value in instances[number][2:]:
        width, height = value.split(' ')
        block_widths.append(int(width))
        block_heights.append(int(height))
    
    # Get the maximum width and height
    max_width = int(instances[number][0])
    
    total_area = 0
    for n in range(int(instances[number][1])):
        total_area += block_widths[n] * block_heights[n]
    max_height = total_area // max_width
    
    return blocks, block_widths, block_heights, max_width, max_height

def get_circuits(block_widths, block_heights, max_width, max_height, start_x, start_y):
    circuits = []
    for i in range(len(start_x)):
        circuits.append([block_widths[i], block_heights[i], start_x[i], start_y[i]])
    return circuits

## MiniZinc Code

code = """
    include "globals.mzn";

    % Variables initialisation
    enum BLOCKS;
    array[BLOCKS] of int: BLOCK_WIDTHS;
    array[BLOCKS] of int: BLOCK_HEIGHTS;

    int: MAX_WIDTH;
    int: MAX_HEIGHT;

    array[BLOCKS] of var 0..MAX_WIDTH: start_x;
    array[BLOCKS] of var 0..MAX_HEIGHT: start_y;

    % Constraints to find x-coordinates
    constraint cumulative(start_x, BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_HEIGHT);
    constraint forall(b in BLOCKS)(start_x[b] + BLOCK_WIDTHS[b] <= MAX_WIDTH);

    % Constraints to find y-coordinates
    constraint cumulative(start_y, BLOCK_HEIGHTS, BLOCK_WIDTHS, MAX_WIDTH);
    constraint forall(b in BLOCKS)(start_y[b] + BLOCK_HEIGHTS[b] <= MAX_HEIGHT);

    % Constraint to remove overlaps
    constraint diffn(start_x, start_y, BLOCK_WIDTHS, BLOCK_HEIGHTS);
    
    % Symmetry breaking
    constraint lex_lesseq(start_y, reverse(start_y));

    % Search strategy
    solve :: seq_search([int_search(start_x, most_constrained, indomain_min), 
                         int_search(start_y, most_constrained, indomain_min)])
    satisfy;
"""

# # Show a sample solution
# n = 0
# BLOCKS, BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)

# trivial = Model()
# trivial.add_string(code)

# timeout = time.time() + 60*5

# instance = Instance(gecode, trivial)

# instance['BLOCKS'] = BLOCKS
# instance['BLOCK_WIDTHS'] = BLOCK_WIDTHS
# instance['BLOCK_HEIGHTS'] = BLOCK_HEIGHTS
# instance['MAX_WIDTH'] = MAX_WIDTH
# instance['MAX_HEIGHT'] = MAX_HEIGHT

# result = instance.solve(timeout=timedelta(minutes=5), processes=4)

# if time.time() >= timeout:
    # print(f'Instance-{n} Fail: Timeout')
# else:
    # start_x = result['start_x']
    # start_y = result['start_y']
    
    # circuits = get_circuits(BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
    # plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits)
   
## Data Output

for n in tqdm(range(len(instances))):
    BLOCKS, BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)
    
    trivial = Model()
    trivial.add_string(code)

    timeout = time.time() + 60*5

    instance = Instance(gecode, trivial)

    instance['BLOCKS'] = BLOCKS
    instance['BLOCK_WIDTHS'] = BLOCK_WIDTHS
    instance['BLOCK_HEIGHTS'] = BLOCK_HEIGHTS
    instance['MAX_WIDTH'] = MAX_WIDTH
    instance['MAX_HEIGHT'] = MAX_HEIGHT
    
    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        start_x = result['start_x']
        start_y = result['start_y']
        
        output_solution(instances[n], MAX_HEIGHT, start_x, start_y, f'output/CP/normal/solutions/out-{n+1}.txt')
        
        circuits = get_circuits(BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
        plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits, f'output/CP/normal/images/out-{n+1}.png')