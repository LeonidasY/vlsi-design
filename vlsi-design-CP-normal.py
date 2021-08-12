### Import the necessary libraries
from tqdm import tqdm
from utils import import_instances, plot_solution, output_solution
from collections import OrderedDict
import time
from datetime import timedelta
from minizinc import Instance, Model, Solver
gecode = Solver.lookup("gecode")


### Data Input
instances = import_instances('input/instances/')


### Functions
def get_variables(instances, number):
    # Get the number of circuits
    circuits = []
    for n in range(int(instances[number][1])):
        circuits.append(f'Block {n}')
    
    # Get circuit lengths and heights
    width_lst = []
    height_lst = []
    area = {}
    for n, value in enumerate(instances[number][2:]):
        width, height = value.split(' ')
        
        width_lst.append(int(width))
        height_lst.append(int(height))
        area[n] = int(width) * int(height)
    
    sort_area = OrderedDict(sorted(area.items(), key=lambda t: t[1]))
    
    circuit_widths = []
    circuit_heights = []

    for i in sort_area.keys():
        circuit_widths.append(int(width_lst[i]))
        circuit_heights.append(int(height_lst[i]))
    
    # Get the maximum width and height
    max_width = int(instances[number][0])
    
    total_area = 0
    for n in range(int(instances[number][1])):
        total_area += circuit_widths[n] * circuit_heights[n]
    max_height = total_area // max_width
    
    return circuits, circuit_widths, circuit_heights, max_width, max_height

def get_circuits(circuit_widths, circuit_heights, max_width, max_height, start_x, start_y):
    circuits = []
    for i in range(len(start_x)):
        circuits.append([circuit_widths[i], circuit_heights[i], start_x[i], start_y[i]])
    return circuits

# MiniZinc Code
code = """
    include "globals.mzn";

    % Variables initialisation
    enum CIRCUITS;
    array[CIRCUITS] of int: CIRCUIT_WIDTHS;
    array[CIRCUITS] of int: CIRCUIT_HEIGHTS;

    int: MAX_WIDTH;
    int: MAX_HEIGHT;

    array[CIRCUITS] of var 0..MAX_WIDTH: start_x;
    array[CIRCUITS] of var 0..MAX_HEIGHT: start_y;

    % Constraints to find x-coordinates
    constraint cumulative(start_x, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_HEIGHT);
    constraint forall(c in CIRCUITS)(start_x[c] + CIRCUIT_WIDTHS[c] <= MAX_WIDTH);

    % Constraints to find y-coordinates
    constraint cumulative(start_y, CIRCUIT_HEIGHTS, CIRCUIT_WIDTHS, MAX_WIDTH);
    constraint forall(c in CIRCUITS)(start_y[c] + CIRCUIT_HEIGHTS[c] <= MAX_HEIGHT);

    % Constraint to remove overlaps
    constraint diffn(start_x, start_y, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS);

    % Search strategy
    solve :: seq_search([int_search(start_x, most_constrained, indomain_min), 
                         int_search(start_y, most_constrained, indomain_min)])
    satisfy;
"""


# ### Show a sample solution
# n = 0
# CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)

# trivial = Model()
# trivial.add_string(code)

# timeout = time.time() + 60*5

# instance = Instance(gecode, trivial)

# instance['CIRCUITS'] = CIRCUITS
# instance['CIRCUIT_WIDTHS'] = CIRCUIT_WIDTHS
# instance['CIRCUIT_HEIGHTS'] = CIRCUIT_HEIGHTS
# instance['MAX_WIDTH'] = MAX_WIDTH
# instance['MAX_HEIGHT'] = MAX_HEIGHT

# result = instance.solve(timeout=timedelta(minutes=5), processes=4)

# if time.time() >= timeout:
    # print(f'Instance-{n} Fail: Timeout')
# else:
    # start_x = result['start_x']
    # start_y = result['start_y']
    
    # circuits = get_circuits(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
    # plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits)


### Data Output
for n in tqdm(range(len(instances))):
    CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)
    
    trivial = Model()
    trivial.add_string(code)

    timeout = time.time() + 60*5

    instance = Instance(gecode, trivial)

    instance['CIRCUITS'] = CIRCUITS
    instance['CIRCUIT_WIDTHS'] = CIRCUIT_WIDTHS
    instance['CIRCUIT_HEIGHTS'] = CIRCUIT_HEIGHTS
    instance['MAX_WIDTH'] = MAX_WIDTH
    instance['MAX_HEIGHT'] = MAX_HEIGHT
    
    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        start_x = result['start_x']
        start_y = result['start_y']
        
        output_solution(instances[n], MAX_HEIGHT, start_x, start_y, f'output/CP (Normal)/solutions/out-{n+1}.txt')
        
        circuits = get_circuits(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
        plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits, f'output/CP (Normal)/images/out-{n+1}.png')