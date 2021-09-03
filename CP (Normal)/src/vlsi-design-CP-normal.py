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
    enum circuits;
    array[circuits] of int: circuit_heights;
    array[circuits] of int: circuit_widths;

    int: max_height;
    int: min_height;
    int: max_width;

    var min_height..max_height: height;
    
    array[circuits] of var 0..max_height: start_y;
    array[circuits] of var 0..max_width: start_x;

    % Constraints to find y-coordinates
    constraint cumulative(start_y, circuit_heights, circuit_widths, max_width);
    constraint forall(c in circuits)(start_y[c] + circuit_heights[c] <= height);

    % Constraints to find x-coordinates
    constraint cumulative(start_x, circuit_widths, circuit_heights, height);
    constraint forall(c in circuits)(start_x[c] + circuit_widths[c] <= max_width);
    
    % Constraint to remove overlaps
    constraint diffn(start_x, start_y, circuit_widths, circuit_heights);

    % Search strategy
    solve :: seq_search([
        int_search([height], dom_w_deg, indomain_min),
        int_search(start_y, dom_w_deg, indomain_min), 
        int_search(start_x, dom_w_deg, indomain_min),
    ])
    minimize height;
"""


### Data Output
for n in tqdm(range(len(instances))):
    circuits, circuit_widths, circuit_heights, max_width, max_height, min_height = get_variables(instances, n)
    
    trivial = Model()
    trivial.add_string(code)

    timeout = time.time() + 60*5

    instance = Instance(gecode, trivial)

    instance['circuits'] = circuits
    instance['circuit_widths'] = circuit_widths
    instance['circuit_heights'] = circuit_heights
    instance['max_width'] = max_width
    instance['max_height'] = max_height
    instance['min_height'] = min_height
    
    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        start_x = result['start_x']
        start_y = result['start_y']
        height = result['height']
        
        output_solution(instances[n], min_height, start_x, start_y, f'../out/solutions/out-{n+1}.txt')
        
        circuits = get_circuits(circuit_widths, circuit_heights, max_width, min_height, start_x, start_y)
        plot_solution(max_width, height, circuits, f'../out/images/out-{n+1}.png')