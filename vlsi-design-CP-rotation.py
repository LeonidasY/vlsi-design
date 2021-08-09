# Import the necessary libraries
from tqdm import tqdm
from utils import import_instances, plot_solution
import time
from datetime import timedelta
from minizinc import Instance, Model, Solver
gecode = Solver.lookup("gecode")

## Data Input

instances = import_instances('input/instances/')

## Functions

def get_variables(instances, number):
    # Get the number of circuits
    circuits = []
    for n in range(int(instances[number][1])):
        circuits.append(f'Block {n}')
    
    # Get circuit lengths and heights
    circuit_widths = []
    circuit_heights = []

    for value in instances[number][2:]:
        width, height = value.split(' ')
        circuit_widths.append(int(width))
        circuit_heights.append(int(height))
    
    # Get the maximum width and height
    max_width = int(instances[number][0])
    
    total_area = 0
    for n in range(int(instances[number][1])):
        total_area += circuit_widths[n] * circuit_heights[n]
    max_height = total_area // max_width
    
    return circuits, circuit_widths, circuit_heights, max_width, max_height

def get_shape(circuits):
    shape = ''
    for n in range(len(circuits)*2):
        if n == len(circuits)*2-1:
            shape += f"{{{n+1}}}"
        else:
            shape += f"{{{n+1}}}, "
    shape = '[' + shape + ']'
    return shape

def get_valid_shapes(circuits):
    valid_shapes = ''
    for n in range(0, len(circuits)*2, 2):
        if n == len(circuits)*2 - 2:
            valid_shapes += f"{{{n+1}, {n+2}}}"
        else:
            valid_shapes += f"{{{n+1}, {n+2}}}, "
    valid_shapes = '[' + valid_shapes + ']'
    return valid_shapes
    
def get_rect_size(circuit_widths, circuit_heights):
    rect_size = ''
    dimensions = []
    for n in range(len(circuit_widths)):
        rect_size += f"{circuit_widths[n]}, {circuit_heights[n]}|"
        rect_size += f"{circuit_heights[n]}, {circuit_widths[n]}|"
        
        dimensions.append([circuit_widths[n], circuit_heights[n]])
        dimensions.append([circuit_heights[n], circuit_widths[n]])
    rect_size = '[|' + rect_size + '|]'
    return rect_size, dimensions
    
def get_rect_offset(circuit_widths, circuit_heights):
    rect_offset = ''
    for n in range(len(circuit_widths)):
        rect_offset += f"{0}, {0}|"
        rect_offset += f"{0}, {0}|"
    rect_offset = '[|' + rect_offset + '|]' 
    return rect_offset
    
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
    
def output_solution(max_width, max_height, widths, heights, start_x, start_y, file):
    solution = [str(max_width), str(max_height)]
    for i in range(len(widths)):
        solution.append(str(widths[i]) + ' ' + str(heights[i]) + ' ' + str(start_x[i]) + ' ' + str(start_y[i]))
    
    with open(file, 'w') as output:
        for item in solution:
            output.write(item)
            output.write('\n')  

def get_circuits(circuit_widths, circuit_heights, max_width, max_height, start_x, start_y):
    circuits = []
    for i in range(len(start_x)):
        circuits.append([circuit_widths[i], circuit_heights[i], start_x[i], start_y[i]])
    return circuits            

# # Show a sample solution
# n = 0
# CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)

# shape = get_shape(CIRCUITS)
# valid_shapes = get_valid_shapes(CIRCUITS)
# rect_size, dimensions = get_rect_size(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)
# rect_offset = get_rect_offset(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)

# ## MiniZinc Code

# code = f"""
    # include "globals.mzn";

    # % Variables initialisation
    # int: k;
    # int: nObjects;
    # int: nRectangles;
    # int: nShapes;
   
    # int: MAX_WIDTH;
    # int: MAX_HEIGHT;

    # set of int: DIMENSIONS = 1..k;
    # set of int: OBJECTS    = 1..nObjects;
    # set of int: RECTANGLES = 1..nRectangles;
    # set of int: SHAPES     = 1..nShapes;

    # array[DIMENSIONS] of int:             l;
    # array[DIMENSIONS] of int:             u;
    # array[RECTANGLES,DIMENSIONS] of int:  rect_size = {rect_size};
    # array[RECTANGLES,DIMENSIONS] of int:  rect_offset = {rect_offset};
    # array[SHAPES] of set of RECTANGLES:   shape = {shape};
    # array[OBJECTS,DIMENSIONS] of var int: x;
    # array[OBJECTS] of var SHAPES:         kind;

    # l = [0, 0];
    # u = [MAX_WIDTH, MAX_HEIGHT];
    
    # array[OBJECTS] of set of SHAPES: valid_shapes = {valid_shapes};

    # constraint forall(obj in OBJECTS)(
        # kind[obj] in valid_shapes[obj]
    # );
    
    # constraint geost_smallest_bb(
        # k,
        # rect_size,
        # rect_offset,
        # shape,
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
# instance['nRectangles'] = len(CIRCUITS) * 2
# instance['nShapes'] = len(CIRCUITS) * 2
# instance['MAX_WIDTH'] = MAX_WIDTH
# instance['MAX_HEIGHT'] = MAX_HEIGHT

# result = instance.solve(timeout=timedelta(minutes=5), processes=4)

# if time.time() >= timeout:
    # print(f'Instance-{n} Fail: Timeout')
# else:
    # x = result['x']
    # kind = result['kind']
    
    # circuit_widths, circuit_heights, start_x, start_y = get_solution(dimensions, x, kind)
    
    # circuits = get_circuits(circuit_widths, circuit_heights, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
    # plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits)
    
## Data Output

for n in tqdm(range(len(instances))):
    CIRCUITS, CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)

    shape = get_shape(CIRCUITS)
    valid_shapes = get_valid_shapes(CIRCUITS)
    rect_size, dimensions = get_rect_size(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)
    rect_offset = get_rect_offset(CIRCUIT_WIDTHS, CIRCUIT_HEIGHTS)
    
    ## MiniZinc Code

    code = f"""
        include "globals.mzn";

        % Variables initialisation
        int: k;
        int: nObjects;
        int: nRectangles;
        int: nShapes;
       
        int: MAX_WIDTH;
        int: MAX_HEIGHT;

        set of int: DIMENSIONS = 1..k;
        set of int: OBJECTS    = 1..nObjects;
        set of int: RECTANGLES = 1..nRectangles;
        set of int: SHAPES     = 1..nShapes;

        array[DIMENSIONS] of int:             l;
        array[DIMENSIONS] of int:             u;
        array[RECTANGLES,DIMENSIONS] of int:  rect_size = {rect_size};
        array[RECTANGLES,DIMENSIONS] of int:  rect_offset = {rect_offset};
        array[SHAPES] of set of RECTANGLES:   shape = {shape};
        array[OBJECTS,DIMENSIONS] of var int: x;
        array[OBJECTS] of var SHAPES:         kind;

        l = [0, 0];
        u = [MAX_WIDTH, MAX_HEIGHT];
        
        array[OBJECTS] of set of SHAPES: valid_shapes = {valid_shapes};

        constraint forall(obj in OBJECTS)(
            kind[obj] in valid_shapes[obj]
        );
        
        constraint geost_smallest_bb(
            k,
            rect_size,
            rect_offset,
            shape,
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
    instance['nRectangles'] = len(CIRCUITS) * 2
    instance['nShapes'] = len(CIRCUITS) * 2
    instance['MAX_WIDTH'] = MAX_WIDTH
    instance['MAX_HEIGHT'] = MAX_HEIGHT

    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        x = result['x']
        kind = result['kind']
        
        circuit_widths, circuit_heights, start_x, start_y = get_solution(dimensions, x, kind)
        output_solution(MAX_WIDTH, MAX_HEIGHT, circuit_widths, circuit_heights, start_x, start_y, f'output/CP (Rotation)/solutions/out-{n+1}.txt')
        
        circuits = get_circuits(circuit_widths, circuit_heights, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
        plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits, f'output/CP (Rotation)/images/out-{n+1}.png')