### Import the necessary libraries
from tqdm import tqdm
from utils import *
import time
from datetime import timedelta
from minizinc import Instance, Model, Solver
gecode = Solver.lookup("gecode")


### Data Input
instances = import_instances('../../../input/')

   
### Data Output
for n in tqdm(range(len(instances))):   
    # MiniZinc Code for Model 1
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

        % Constraints to find y-coordinates
        constraint cumulative(start_y, circuit_heights, circuit_widths, max_width);
        constraint forall(c in circuits)(start_y[c] + circuit_heights[c] <= height);

        % Search strategy
        solve :: seq_search([
            int_search([height], dom_w_deg, indomain_min),
            int_search(start_y, dom_w_deg, indomain_min),
        ])
        minimize height;
    """    
  
    circuits, circuit_widths, circuit_heights, max_width, max_height, min_height = get_variables(instances, n)

    shapes, valid_shapes = get_shapes(circuit_widths, circuit_heights)
    rect_size, rect_offset, dimensions = get_rectangles(circuit_widths, circuit_heights)
    
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
    
    try:
        height = instance.solve(timeout=timedelta(minutes=5), processes=4)['height']
        time_diff = timeout - time.time()
    except:
        print(f'Instance-{n+1} Fail: Timeout')
        continue        
    
    
    # MiniZinc Code for Model 2
    code = f"""
        include "globals.mzn";

        % Variables initialisation
        int: k;
        int: nObjects;
        int: nRectangles;
        int: nShapes;
       
        int: max_width;
        int: height;

        set of int: dimensions = 1..k;
        set of int: objects    = 1..nObjects;
        set of int: rectangles = 1..nRectangles;
        set of int: shapes     = 1..nShapes;

        array[dimensions] of int:             l;
        array[dimensions] of int:             u;
        array[rectangles,dimensions] of int:  rect_size = {rect_size};
        array[rectangles,dimensions] of int:  rect_offset = {rect_offset};
        array[shapes] of set of rectangles:   rect_shapes = {shapes};
        array[objects,dimensions] of var int: x;
        array[objects] of var shapes:         kind;

        l = [0, 0];
        u = [max_width, height];
        
        array[objects] of set of shapes: valid_shapes = {valid_shapes};
        
        % Constraint to accept only valid shapes
        constraint forall(obj in objects)(
            kind[obj] in valid_shapes[obj]
        );
        
        % Constraint for packing
        constraint geost_smallest_bb(
            k,
            rect_size,
            rect_offset,
            rect_shapes,
            x,
            kind,
            l,
            u
        );
        
        % Search strategy
        solve :: int_search(kind, dom_w_deg, indomain_min) satisfy;
    """  
    
    trivial = Model()
    trivial.add_string(code)

    instance = Instance(gecode, trivial)

    instance['k'] = 2
    instance['nObjects'] = len(circuits)
    instance['nRectangles'] = len(dimensions)
    instance['nShapes'] = len(dimensions)
    instance['max_width'] = max_width
    instance['height'] = height
    
    try:
        result = instance.solve(timeout=timedelta(seconds=round(time_diff)), processes=4)
        
        if time.time() >= timeout:
            print(f'Instance-{n+1} Fail: Timeout')
        else:
            x = result['x']
            kind = result['kind']
            
            circuit_widths, circuit_heights, start_x, start_y = get_solution(dimensions, x, kind)
            output_solution(max_width, min_height, circuit_widths, circuit_heights, start_x, start_y, f'../out/solutions/out-{n+1}.txt')
            
            circuits = get_circuits(circuit_widths, circuit_heights, max_width, min_height, start_x, start_y)
            plot_solution(max_width, min_height, circuits, f'../out/images/out-{n+1}.png')
    except:
        print(f'Instance-{n+1} Fail: Timeout')
        continue      