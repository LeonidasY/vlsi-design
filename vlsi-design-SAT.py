from itertools import combinations
from utils import import_instances, plot_solution, output_solution
from z3 import *

## Data Input

instances = import_instances('input/instances/')

# Functions

def at_least_one(bool_vars):
    return Or(bool_vars)

def at_most_one(bool_vars):
    return [Not(And(pair[0], pair[1])) for pair in combinations(bool_vars, 2)]

def exactly_one(solver, bool_vars):
    solver.add(at_most_one(bool_vars))
    solver.add(at_least_one(bool_vars))

def get_variables(instance_number):
    # Get the number of blocks
    number_of_blocks = int(instances[instance_number][1])
    
    # Get block lengths and heights
    blocks_width = []
    blocks_height = []

    for value in instances[instance_number][2:]:
        width, height = value.split(' ')
        blocks_width.append(int(width))
        blocks_height.append(int(height))  

    width = int(instances[instance_number][0])
    return number_of_blocks, blocks_width, blocks_height, width

## Z3 SAT Code

def vlsi(s, height):
    # Variables
    p = [[[Bool(f"x_{i}_{j}_{n}") for n in range((2* number_of_blocks) + 1)] for j in range(height)] for i in range(width)]

    # A cell has only one value
    for i in range(width):
        for j in range(height):
            exactly_one(s, p[i][j])

    for n in range(number_of_blocks):
        # A circuit has only one position
        exactly_one(s, [p[i][j][n] for i in range(width) for j in range(height)])

        # A circuit stays inside the plane
        s.add(at_least_one([p[i][j][n] for i in range(width - blocks_width[n] + 1) for j in range(height - blocks_height[n] + 1)]))

    # The circuits can't overlap
    for n in range(number_of_blocks):
        for i in range(width - blocks_width[n]+1):
            for j in range(height - blocks_height[n]+1):
                for k in range(i, i + blocks_width[n]):
                    for u in range(j, j + blocks_height[n]):
                        if(k != i or u != j):
                            s.add(Implies(p[i][j][n], p[k][u][n + number_of_blocks]))

    sol = []
    if s.check() == sat:
        m = s.model()
        for i in range(width):
            sol.append([])
            for j in range(height):
                for k in range(2*(number_of_blocks) + 1):
                    if m.evaluate(p[i][j][k]):
                        sol[i].append(k)
        print(sol)
    elif s.reason_unknown() == "timeout":
        print("Solver timeout")
    else:
        print("Failed to solve")
    return sol

for instance_number in range(len(instances)):
    print("Solving instance: ", instance_number)
    number_of_blocks, blocks_width, blocks_height, width = get_variables(instance_number)
    starting_height = int(sum([blocks_width[i] * blocks_height[i] for i in range(number_of_blocks)]) / width)
    height_i = starting_height
    s = Solver()

    times = 300 * 1000 # 300 sec
    s.set(timeout=times)

    sol = vlsi(s, height_i)
        
    if (sol) :
        start_x = []
        start_y = []
        for n in range(number_of_blocks):
            for i in range(len(sol)):
                for j in range(len(sol[0])):
                    if sol[i][j] == n:
                        start_x.append(i)
                        start_y.append(j)
        circuits = [[blocks_width[i], blocks_height[i], start_x[i], start_y[i]] for i in range(number_of_blocks)]
        plot_solution(width, height_i, circuits, f'output/SAt/images/out-{instance_number+1}.png')
        output_solution(instances[instance_number], height_i, start_x, start_y, f'output/SAT/solutions/out-{instance_number + 1}.txt')