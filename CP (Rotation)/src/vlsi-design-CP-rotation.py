### Import the necessary libraries
from tqdm import tqdm
from utils import *
import time
from datetime import timedelta
from minizinc import Instance, Model, Solver
gecode = Solver.lookup("gecode")


### Data Input
instances = import_instances('../../input/')


# ### Show a sample solution
# n = 0
# CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MIN_HEIGHT = get_variables(instances, n)

# shapes, valid_shapes = get_shapes(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)
# rect_size, rect_offset, dimensions = get_rectangles(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)

# # MiniZinc Code
# code = f"""
    # include "globals.mzn";

    # % Variables initialisation
    # int: k;
    # int: nObjects;
    # int: nRectangles;
    # int: nShapes;
   
    # int: MAX_WIDTH;
    # int: MIN_HEIGHT;

    # set of int: DIMENSIONS = 1..k;
    # set of int: OBJECTS    = 1..nObjects;
    # set of int: RECTANGLES = 1..nRectangles;
    # set of int: SHAPES     = 1..nShapes;

    # array[DIMENSIONS] of int:             l;
    # array[DIMENSIONS] of int:             u;
    # array[RECTANGLES,DIMENSIONS] of int:  rect_size = {rect_size};
    # array[RECTANGLES,DIMENSIONS] of int:  rect_offset = {rect_offset};
    # array[SHAPES] of set of RECTANGLES:   shapes = {shapes};
    # array[OBJECTS,DIMENSIONS] of var int: x;
    # array[OBJECTS] of var SHAPES:         kind;

    # l = [0, 0];
    # u = [MAX_WIDTH, MIN_HEIGHT];
    
    # array[OBJECTS] of set of SHAPES: valid_shapes = {valid_shapes};
    
    # constraint forall(obj in OBJECTS)(
        # kind[obj] in valid_shapes[obj]
    # );
    
    # constraint geost_smallest_bb(
        # k,
        # rect_size,
        # rect_offset,
        # shapes,
        # x,
        # kind,
        # l,
        # u
    # );
    
    # solve :: int_search(kind, most_constrained, indomain_min) satisfy;
# """

# trivial = Model()
# trivial.add_string(code)

# timeout = time.time() + 60*5

# instance = Instance(gecode, trivial)

# instance['k'] = 2
# instance['nObjects'] = len(CIRCUITS)
# instance['nRectangles'] = len(dimensions)
# instance['nShapes'] = len(dimensions)
# instance['MAX_WIDTH'] = MAX_WIDTH
# instance['MIN_HEIGHT'] = MIN_HEIGHT

# result = instance.solve(timeout=timedelta(minutes=5), processes=4)

# if time.time() >= timeout:
    # print(f'Instance-{n} Fail: Timeout')
# else:
    # x = result['x']
    # kind = result['kind']
    
    # circuit_widths, circuit_heights, start_x, start_y = get_solution(dimensions, x, kind)
    
    # circuits = get_circuits(circuit_widths, circuit_heights, MAX_WIDTH, MIN_HEIGHT, start_x, start_y)
    # plot_solution(MAX_WIDTH, MIN_HEIGHT, circuits)

    
### Data Output
for n in tqdm(range(len(instances))):
    CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MIN_HEIGHT = get_variables(instances, n)

    shapes, valid_shapes = get_shapes(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)
    rect_size, rect_offset, dimensions = get_rectangles(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)
    
    # MiniZinc Code
    code = f"""
        include "globals.mzn";

        % Variables initialisation
        int: k;
        int: nObjects;
        int: nRectangles;
        int: nShapes;
       
        int: MAX_WIDTH;
        int: MIN_HEIGHT;

        set of int: DIMENSIONS = 1..k;
        set of int: OBJECTS    = 1..nObjects;
        set of int: RECTANGLES = 1..nRectangles;
        set of int: SHAPES     = 1..nShapes;

        array[DIMENSIONS] of int:             l;
        array[DIMENSIONS] of int:             u;
        array[RECTANGLES,DIMENSIONS] of int:  rect_size = {rect_size};
        array[RECTANGLES,DIMENSIONS] of int:  rect_offset = {rect_offset};
        array[SHAPES] of set of RECTANGLES:   shapes = {shapes};
        array[OBJECTS,DIMENSIONS] of var int: x;
        array[OBJECTS] of var SHAPES:         kind;

        l = [0, 0];
        u = [MAX_WIDTH, MIN_HEIGHT];
        
        array[OBJECTS] of set of SHAPES: valid_shapes = {valid_shapes};
        
        constraint forall(obj in OBJECTS)(
            kind[obj] in valid_shapes[obj]
        );
        
        constraint geost_smallest_bb(
            k,
            rect_size,
            rect_offset,
            shapes,
            x,
            kind,
            l,
            u
        );

        solve :: int_search(kind, most_constrained, indomain_min) satisfy;
    """    
    
    trivial = Model()
    trivial.add_string(code)
    
    timeout = time.time() + 60*5

    instance = Instance(gecode, trivial)

    instance['k'] = 2
    instance['nObjects'] = len(CIRCUITS)
    instance['nRectangles'] = len(dimensions)
    instance['nShapes'] = len(dimensions)
    instance['MAX_WIDTH'] = MAX_WIDTH
    instance['MIN_HEIGHT'] = MIN_HEIGHT
    
    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        x = result['x']
        kind = result['kind']
        
        circuit_widths, circuit_heights, start_x, start_y = get_solution(dimensions, x, kind)
        output_solution(MAX_WIDTH, MIN_HEIGHT, circuit_widths, circuit_heights, start_x, start_y, f'../out/out-{n+1}.txt')
        
        circuits = get_circuits(circuit_widths, circuit_heights, MAX_WIDTH, MIN_HEIGHT, start_x, start_y)
        plot_solution(MAX_WIDTH, MIN_HEIGHT, circuits, f'../out/images/out-{n+1}.png')