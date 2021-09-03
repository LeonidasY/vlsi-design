### Import the necessary libraries
from tqdm import tqdm
from itertools import combinations
from utils import import_instances, plot_solution, output_solution
from z3 import *

### Data Input
instances = import_instances('../../input/')

### Functions
def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one(solver, bool_vars):
    solver.add(at_most_one(bool_vars))
    solver.add(at_least_one(bool_vars))

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

### Z3 SAT Code
def vlsi(s, height):
    grid = [[[Bool(f"grid_{i}_{j}_{c}") for c in range(number_of_circuits)] for j in range(height)] for i in range(width)]

    # A place has only one value (only one circuit can be on each place)
    for i in range(width):
        for j in range(height):
            s.add(at_most_one(grid[i][j]))

    # Every piece of a given circuit must be placed together
    for c in range(number_of_circuits):
        positions = []
        for i in range(width - circuits_width[c] + 1):
            for j in range(height - circuits_height[c] + 1):
                positions.append(And([grid[ii][jj][c] for ii in range(i, i + circuits_width[c]) for jj in range(j, j + circuits_height[c])]))
        s.add(at_least_one(positions))
    
    # Return solution if possible
    sol = []
    if s.check() == sat:
        m = s.model()
        for i in range(width):
            sol.append([])
            for j in range(height):
                for c in range(number_of_circuits):
                    if m.evaluate(grid[i][j][c]):
                        sol[i].append(c)
    return sol

for instance_number in tqdm(range(len(instances))):
    number_of_circuits, circuits_width, circuits_height, width, starting_height = get_variables(instance_number)

    s = Solver()

    #5 minutes (300 sec) time limit for each instance to be solved
    times = 300 * 1000
    s.set(timeout=times)

    sol = vlsi(s, starting_height)
    
    # Save solution if present
    if (sol) :
        start_x, flag, start_y= [False]*(number_of_circuits), [False]*(number_of_circuits), [False]*(number_of_circuits)
        for i in range(len(sol)):
            for j in range(len(sol[0])):
                for c in range(number_of_circuits):
                    if sol[i][j] == c and not(flag[c]):
                        flag[c] = True
                        start_x[c] = i
                        start_y[c] = j
        circuits = [[circuits_width[i], circuits_height[i], start_x[i], start_y[i]] for i in range(number_of_circuits)]
        plot_solution(width, starting_height, circuits, f'../out/images/out-{instance_number + 1}.png')
        output_solution(instances[instance_number], starting_height, start_x, start_y, f'../out/solutions/out-{instance_number + 1}.txt')
    else:
        print("\nFailed to solve instance %i" % (instance_number + 1))