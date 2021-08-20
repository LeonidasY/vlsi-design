### Import the necessary libraries
from tqdm import tqdm
from itertools import combinations
from utils import import_instances, plot_solution, output_solution
from z3 import *

### Data Input
instances = import_instances('../../input/')

### Functions
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

    width = int(instances[instance_number][0])
    starting_height = int(math.ceil(sum([circuits_width[c] * circuits_height[c] for c in range(number_of_circuits)]) / width))
    
    return number_of_circuits, circuits_width, circuits_height, width, starting_height

### Z3 SMT Code
def vlsi(s, plate_height):    
    # Matrix of the coordinates of the bottom-left corner of each circuit
    corner_coordinates = [[Int(f"c_{i}_{coordinates}") for coordinates in range(2)] for i in range(number_of_circuits)]

    # For easier comprension the coordinates of the circuits will be given names
    W = 0   #the x-coordinate (or width)
    H = 1   #the y-coordinate (or height)

    # Each circuit's bottom-left corner needs to be in the grid and have all the circuit contained in the plate
    inside = [(And( corner_coordinates[n][W] >= 0,
                    corner_coordinates[n][W] + circuits_width[n] <= plate_width, 
                    corner_coordinates[n][H] >= 0,
                    corner_coordinates[n][H] + circuits_height[n] <= plate_height)) for n in range(number_of_circuits)]

    # Each circuit cannot overlap with another circuit
    overlap = []
    for n in range(number_of_circuits):
        for m in range(n + 1, number_of_circuits):
            overlap.append((Or( corner_coordinates[m][W] - corner_coordinates[n][W] >= circuits_width[n],
                                corner_coordinates[n][W] - corner_coordinates[m][W] >= circuits_width[m],
                                corner_coordinates[m][H] - corner_coordinates[n][H] >= circuits_height[n],
                                corner_coordinates[n][H] - corner_coordinates[m][H] >= circuits_height[m])))

    vlsi_model = inside + overlap
    s.add(vlsi_model)
    
    # Return solution if possible
    if s.check() == sat:
        m = s.model()
        return [[int(m.evaluate(corner_coordinates[i][j]).as_string()) for j in range(2)] for i in range(number_of_circuits)]
    else:
        return 

for instance_number in tqdm(range(len(instances))):
    number_of_circuits, circuits_width, circuits_height, plate_width, starting_height = get_variables(instance_number)
    
    s = Solver()

    #5 minutes (300 sec) time limit for each instance to be solved
    times = 300 * 1000
    s.set(timeout = times)

    sol = vlsi(s, starting_height)
        
    # Save solution if present
    if (sol) :
        start_x = []
        start_y = []
        for j in range(len(sol)):
            start_x.append(int(sol[j][0]))
            start_y.append(int(sol[j][1]))
        circuits = [[circuits_width[i], circuits_height[i], start_x[i], start_y[i]] for i in range(number_of_circuits)]
        plot_solution(plate_width, starting_height, circuits, f'../out/images/out-{instance_number + 1}.png')
        output_solution(instances[instance_number], starting_height, start_x, start_y, f'../out/out-{instance_number + 1}.txt')
    else:
        print("\nFailed to solve instance %i" % (instance_number + 1))