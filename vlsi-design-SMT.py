from itertools import combinations
from utils import import_instances, plot_solution, output_solution
import time
from z3 import *

## Data Input

instances = import_instances('input/instances/')
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
    corner_coordinates = [[Int(f"c_{i}_{coordinates}") for coordinates in range(2)] for i in range(number_of_circuits)]

    # for easier comprension the coordinates of the circuits will be given names
    W = 0   #the x-coordinate (or width)
    H = 1   #the y-coordinate (or height)

    # each circuit's bottom-left corner needs to be in the grid and have all the circuit contained in the plate
    inside = [(And( corner_coordinates[n][W] >= 0,
                    corner_coordinates[n][W] + circuits_width[n] <= plate_width, 
                    corner_coordinates[n][H] >= 0,
                    corner_coordinates[n][H] + circuits_height[n] <= plate_height)) for n in range(number_of_circuits)]

    # each circuit cannot overlap with another circuit
    overlap = []
    for n in range(number_of_circuits):
        for m in range(n + 1, number_of_circuits):
            overlap.append((Or( corner_coordinates[m][W] - corner_coordinates[n][W] >= circuits_width[n],
                                corner_coordinates[n][W] - corner_coordinates[m][W] >= circuits_width[m],
                                corner_coordinates[m][H] - corner_coordinates[n][H] >= circuits_height[n],
                                corner_coordinates[n][H] - corner_coordinates[m][H] >= circuits_height[m])))

    # the sum of the horizontal/vertical sides of the traversed circuits, can be at most the one of the plate
    #implied = []
    #for i in range(plate_width):
    #    implied.append(sum(
    #        [If(And(corner_coordinates[j][W] <= i, corner_coordinates[j][W] + circuits_width[j] > i),
    #            circuits_height[j],
    #            0) for j in range(number_of_circuits)]) 
    #                        <= plate_height)
#
    #for i in range(plate_height):
    #    implied.append(sum(
    #        [If(And(corner_coordinates[j][H] <= i, corner_coordinates[j][H] + circuits_height[j] > i), 
    #            circuits_width[j],
    #            0) for j in range(number_of_circuits)]) 
    #                        <= plate_width)

    vlsi_model = inside + overlap
    s.add(vlsi_model)
    
    if s.check() == sat:
        m = s.model()
        return [[int(m.evaluate(corner_coordinates[i][j]).as_string()) for j in range(2)] for i in range(number_of_circuits)]
    else:
        return 

middle_time = time.time()
for instance_number in range(len(instances)):
    print("Solving instance: ", instance_number + 1)
    number_of_circuits, circuits_width, circuits_height, plate_width = get_variables(instance_number)
    # to solve for model that 
    plate_height = int(math.ceil(sum([circuits_width[i] * circuits_height[i] for i in range(number_of_circuits)]) / plate_width))
    
    s = Solver()

    #5 minutes limit for each instance to be solved
    times = 300 * 1000 # 300 sec
    s.set(timeout = times)

    middle_time = time.time()

    #call of the function that solves the problem
    sol = vlsi(s, plate_height)
        
    if (sol) :
        start_x = []
        start_y = []
        for j in range(len(sol)):
            start_x.append(int(sol[j][0]))
            start_y.append(int(sol[j][1]))
        circuits = [[circuits_width[i], circuits_height[i], start_x[i], start_y[i]] for i in range(number_of_circuits)]
        plot_solution(plate_width, plate_height, circuits, f'output/SMT/images/out-{instance_number + 1}.png')
        output_solution(instances[instance_number], plate_height, start_x, start_y, f'output/SMT/solutions/out-{instance_number + 1}.txt')
        print("Solved instance %i in %.2f seconds" %((instance_number + 1), (time.time() - middle_time)))	
    else:
        print("Failed to solve instance %i" %(instance_number + 1))