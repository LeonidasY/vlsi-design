from itertools import combinations
from utils import import_instances, plot_solution, output_solution
import time
from z3 import *

## Data Input

instances = import_instances('input/instances/')

# Functions

def get_variables(instance_number):
    # Get the number of blocks
    number_of_circuits = int(instances[instance_number][1])
    
    # Get block lengths and heights
    circuits_width = []
    circuits_height = []

    for value in instances[instance_number][2:]:
        width, height = value.split(' ')
        circuits_width.append(int(width))
        circuits_height.append(int(height))  

    plate_width = int(instances[instance_number][0])
    return number_of_circuits, circuits_width, circuits_height, plate_width

## Z3 SMT Code

def vlsi(s, plate_height):    
    # matrix of the coordinates of the bottom-left corner of each circuit
    v = [[Int(f"x_{i}_{coordinates}") for coordinates in range(2)] for i in range(number_of_circuits)]

    # for easier comprension the coordinates of the circuits will be given names
    W = 0   #the x-coordinate (or width)
    H = 1   #the y-coordinate (or height)

    # each circuit's bottom-left corner needs to be in the grid and have all the circuit contained in the plate
    inside = []
    inside += [(And(v[n][W] + circuits_width[n] <= plate_width, 
                    v[n][W] >= 0,
                    v[n][H] + circuits_height[n] <= plate_height, 
                    v[n][H] >= 0)) for n in range(number_of_circuits)]

    # each circuit cannot overlap another circuit
    overlap = []
    for n in range(number_of_circuits):
        for m in range(n + 1, number_of_circuits):
            overlap.append((Or (v[n][W] + circuits_width[n] <= v[m][W],
                                v[m][W] + circuits_width[m] <= v[n][W],
                                v[n][H] + circuits_height[n] <= v[m][H],
                                v[m][H] + circuits_height[m] <= v[n][H])))

    # the sum of the horizontal/vertical sides of the traversed circuits, can be at most the one of the plate
    implied = []
    for i in range(plate_width):
        implied.append( Sum(
            [If(And(v[j][W] <= i, 
                    i < v[j][W] + circuits_width[j]),
                circuits_height[j],
                0) for j in range(number_of_circuits)]) <= plate_height)

    for i in range(plate_height):
        implied.append(Sum(
            [If(And(v[j][H] <= i, 
                    i < v[j][H] + circuits_height[j]), 
                circuits_width[j]
                ,0) for j in range(number_of_circuits)]) <= plate_width)

    vlsi_model = inside + overlap + implied

    s.add(vlsi_model)
    
    if s.check() == sat:
        m = s.model()
        return [[int(m.evaluate(v[i][j]).as_string()) for j in range(2)] for i in range(number_of_circuits)]
    else:
        print("Failed to solve")

start = time.time()
middle = start
for instance_number in range(len(instances)):
    print("Solved instance %i in %f seconds (%f sec)" %((instance_number - 1), (time.time() - start), (time.time() - middle)))	
    print("Solving instance: ", instance_number)
    number_of_circuits, circuits_width, circuits_height, plate_width = get_variables(instance_number)
    starting_height = int(math.ceil(sum([circuits_width[i] * circuits_height[i] for i in range(number_of_circuits)]) / plate_width))
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
        circuits = [[circuits_width[i], circuits_height[i], start_x[i], start_y[i]] for i in range(number_of_circuits)]
        plot_solution(plate_width, height_i, circuits, f'output/SMT/images/out-{instance_number + 1}.png')
        output_solution(instances[instance_number], height_i, start_x, start_y, f'output/SMT/solutions/out-{instance_number + 1}.txt')