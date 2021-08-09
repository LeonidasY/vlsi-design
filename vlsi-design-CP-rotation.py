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

def get_shape(blocks):
    shape = ''
    for n in range(len(blocks)*2):
        if n == len(blocks)*2-1:
            shape += f"{{{n+1}}}"
        else:
            shape += f"{{{n+1}}}, "
    shape = '[' + shape + ']'
    return shape

def get_valid_shapes(blocks):
    valid_shapes = ''
    for n in range(0, len(blocks)*2, 2):
        if n == len(blocks)*2 - 2:
            valid_shapes += f"{{{n+1}, {n+2}}}"
        else:
            valid_shapes += f"{{{n+1}, {n+2}}}, "
    valid_shapes = '[' + valid_shapes + ']'
    return valid_shapes
    
def get_rect_size(block_widths, block_heights):
    rect_size = ''
    dimensions = []
    for n in range(len(block_widths)):
        rect_size += f"{block_widths[n]}, {block_heights[n]}|"
        rect_size += f"{block_heights[n]}, {block_widths[n]}|"
        
        dimensions.append([block_widths[n], block_heights[n]])
        dimensions.append([block_heights[n], block_widths[n]])
    rect_size = '[|' + rect_size + '|]'
    return rect_size, dimensions
    
def get_rect_offset(block_widths, block_heights):
    rect_offset = ''
    for n in range(len(block_widths)):
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

def get_circuits(block_widths, block_heights, max_width, max_height, start_x, start_y):
    circuits = []
    for i in range(len(start_x)):
        circuits.append([block_widths[i], block_heights[i], start_x[i], start_y[i]])
    return circuits            

# # Show a sample solution
# n = 0
# BLOCKS, BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)

# shape = get_shape(BLOCKS)
# valid_shapes = get_valid_shapes(BLOCKS)
# rect_size, dimensions = get_rect_size(BLOCK_WIDTHS, BLOCK_HEIGHTS)
# rect_offset = get_rect_offset(BLOCK_WIDTHS, BLOCK_HEIGHTS)

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

    # constraint forall (obj in OBJECTS)(
        # kind[obj] in valid_shapes[obj]
    # );
    
    # constraint
        # geost_smallest_bb(
            # k,              % the number of dimensions
            # rect_size,      % the size of each box in k dimensions
            # rect_offset,    % the offset of each box from the base position in k dimensions
            # shape,          % the set of rectangles defining the i-th shape
            # x,              % the base position of each object.
                            # % (var) x[i,j] is the position of object i in dimension j
            # kind,           % (var) the shape used by each object
            # l,              % array of lower bounds
            # u               % array of upper bounds
        # );
    
    # solve :: int_search(kind, most_constrained, indomain_min) satisfy;
# """

# trivial = Model()
# trivial.add_string(code)

# timeout = time.time() + 60*5

# instance = Instance(gecode, trivial)

# instance['k'] = 2
# instance['nObjects'] = len(BLOCKS)
# instance['nRectangles'] = len(BLOCKS) * 2
# instance['nShapes'] = len(BLOCKS) * 2
# instance['MAX_WIDTH'] = MAX_WIDTH
# instance['MAX_HEIGHT'] = MAX_HEIGHT

# result = instance.solve(timeout=timedelta(minutes=5), processes=4)

# if time.time() >= timeout:
    # print(f'Instance-{n} Fail: Timeout')
# else:
    # x = result['x']
    # kind = result['kind']
    
    # block_widths, block_heights, start_x, start_y = get_solution(dimensions, x, kind)
    
    # circuits = get_circuits(block_widths, block_heights, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
    # plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits)
    
## Data Output

for n in tqdm(range(len(instances))):
    BLOCKS, BLOCK_WIDTHS, BLOCK_HEIGHTS, MAX_WIDTH, MAX_HEIGHT = get_variables(instances, n)

    shape = get_shape(BLOCKS)
    valid_shapes = get_valid_shapes(BLOCKS)
    rect_size, dimensions = get_rect_size(BLOCK_WIDTHS, BLOCK_HEIGHTS)
    rect_offset = get_rect_offset(BLOCK_WIDTHS, BLOCK_HEIGHTS)
    
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

        constraint forall (obj in OBJECTS)(
            kind[obj] in valid_shapes[obj]
        );
        
        constraint
            geost_smallest_bb(
                k,              % the number of dimensions
                rect_size,      % the size of each box in k dimensions
                rect_offset,    % the offset of each box from the base position in k dimensions
                shape,          % the set of rectangles defining the i-th shape
                x,              % the base position of each object.
                                % (var) x[i,j] is the position of object i in dimension j
                kind,           % (var) the shape used by each object
                l,              % array of lower bounds
                u               % array of upper bounds
            );

        solve :: int_search(kind, most_constrained, indomain_min) satisfy;
    """    
    
    trivial = Model()
    trivial.add_string(code)
    
    timeout = time.time() + 60*5

    instance = Instance(gecode, trivial)

    instance['k'] = 2
    instance['nObjects'] = len(BLOCKS)
    instance['nRectangles'] = len(BLOCKS) * 2
    instance['nShapes'] = len(BLOCKS) * 2
    instance['MAX_WIDTH'] = MAX_WIDTH
    instance['MAX_HEIGHT'] = MAX_HEIGHT

    result = instance.solve(timeout=timedelta(minutes=5), processes=4)
    
    if time.time() >= timeout:
        print(f'Instance-{n+1} Fail: Timeout')
    else:
        x = result['x']
        kind = result['kind']
        
        block_widths, block_heights, start_x, start_y = get_solution(dimensions, x, kind)
        output_solution(MAX_WIDTH, MAX_HEIGHT, block_widths, block_heights, start_x, start_y, f'output/CP (Rotation)/solutions/out-{n+1}.txt')
        
        circuits = get_circuits(block_widths, block_heights, MAX_WIDTH, MAX_HEIGHT, start_x, start_y)
        plot_solution(MAX_WIDTH, MAX_HEIGHT, circuits, f'output/CP (Rotation)/images/out-{n+1}.png')