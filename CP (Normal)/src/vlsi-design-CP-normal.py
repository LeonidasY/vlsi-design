### Import the necessary libraries
from tqdm import tqdm
from utils import *
import time
from datetime import timedelta
from minizinc import Instance, Model, Solver
gecode = Solver.lookup("gecode")


### Data Input
instances = import_instances('../../input/')


# MiniZinc Code
code = """
    include "globals.mzn";

    % Variables initialisation
    enum CIRCUITS;
    array[CIRCUITS] of int: CIRCUIT_WIDTHS;
    array[CIRCUITS] of int: CIRCUIT_HEIGHTS;

    int: MAX_WIDTH;
    int: MIN_HEIGHT;

    array[CIRCUITS] of var 0..MAX_WIDTH: start_x;
    array[CIRCUITS] of var 0..MIN_HEIGHT: start_y;

    % Constraints to find x-coordinates
    constraint cumulative(start_x, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MIN_HEIGHT);
    constraint forall(c in CIRCUITS)(start_x[c] + CIRCUIT_WIDTHS[c] <= MAX_WIDTH);

    % Constraints to find y-coordinates
    constraint cumulative(start_y, CIRCUIT_HEIGHTS, CIRCUIT_WIDTHS, MAX_WIDTH);
    constraint forall(c in CIRCUITS)(start_y[c] + CIRCUIT_HEIGHTS[c] <= MIN_HEIGHT);

    % Constraint to remove overlaps
    constraint diffn(start_x, start_y, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS);
    
    % Symmetry breaking
    constraint lex_lesseq(start_y, reverse(start_y));

    % Search strategy
    solve :: seq_search([int_search(start_x, most_constrained, indomain_min), 
                         int_search(start_y, most_constrained, indomain_min)])
    satisfy;
"""


### Data Output
for n in tqdm(range(len(instances))):
    CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MIN_HEIGHT = get_variables(instances, n)
    
    trivial = Model()
    trivial.add_string(code)

    timeout = time.time() + 60*5

    instance = Instance(gecode, trivial)

    instance['CIRCUITS'] = CIRCUITS
    instance['CIRCUIT_WIDTHS'] = CIRCUIT_WIDTHS
    instance['CIRCUIT_HEIGHTS'] = CIRCUIT_HEIGHTS
    instance['MAX_WIDTH'] = MAX_WIDTH
    instance['MIN_HEIGHT'] = MIN_HEIGHT
    
    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        start_x = result['start_x']
        start_y = result['start_y']
        
        output_solution(instances[n], MIN_HEIGHT, start_x, start_y, f'../out/out-{n+1}.txt')
        
        circuits = get_circuits(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MIN_HEIGHT, start_x, start_y)
        plot_solution(MAX_WIDTH, MIN_HEIGHT, circuits, f'../out/images/out-{n+1}.png')