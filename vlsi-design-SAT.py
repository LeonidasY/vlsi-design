from itertools import combinations
from utils import import_instances, plot_solution, output_solution
import time
from z3 import *

instances = import_instances('input/instances/')

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
    return number_of_circuits, circuits_width, circuits_height, width

# Z3 SAT Code
def vlsi(s, height):
    grid = [[[Bool(f"grid_{i}_{j}_{c}") for c in range(number_of_circuits)] for j in range(width)] for i in range(height)]

    # A place has only one value (only one circuit can be on each place)
    for i in range(height):
        for j in range(width):
            s.add(at_most_one(grid[i][j]))

    # Every piece of a given circuit must be placed together
    for c in range(number_of_circuits):
        circuit_place = []
        for i in range(height - circuits_height[c] + 1):
            for j in range(width - circuits_width[c] + 1):
                circuit_place.append(And([grid[ii][jj][c] for ii in range(i, i + circuits_height[c]) for jj in range(j, j + circuits_width[c])]))
        s.add(at_least_one(circuit_place))
    
    sol = []
    if s.check() == sat:
        m = s.model()
        for i in range(width):
            sol.append([])
            for j in range(height):
                for c in range(number_of_circuits):
                    if m.evaluate(grid[i][j][c]):
                        sol[i].append(c)
    elif s.reason_unknown() == "timeout":
        print("Solver timeout")
    else:
        print("Failed to solve")
    return sol

def vlsiOLD(s, height):
    # Variables
    p = [[[Bool(f"x_{i}_{j}_{n}") for n in range((2*number_of_circuits) + 1)] for j in range(height)] for i in range(width)]

    # A cell has only one value
    for i in range(width):
        for j in range(height):
            exactly_one(s, p[i][j])

    # A circuit appears once in a position inside the plane
    for n in range(number_of_circuits):
        exactly_one(s, [p[i][j][n] for i in range(width - circuits_width[n] + 1) for j in range(height - circuits_height[n] + 1)])
        exactly_one(s, [p[i][j][n] for i in range(width) for j in range(height)])

    for n in range(number_of_circuits):
        for i in range(width - circuits_width[n]+1):
            for j in range(height - circuits_height[n]+1):
                for k in range(i, i + circuits_width[n]):
                    for u in range(j, j + circuits_height[n]):
                        if(k != i or u != j):
                            s.add(Implies(p[i][j][n], p[k][u][n + number_of_circuits]))


    #for i in range(width):
    #    s.add(sum(
    #        [If(And(v[j][W] <= i, v[j][W] + circuits_width[j] > i),
    #            circuits_height[j],
    #            0) for j in range(number_of_circuits)]) 
    #                        <= height)

    sol = []
    if s.check() == sat:
        m = s.model()
        for i in range(width):
            sol.append([])
            for j in range(height):
                for k in range((2*number_of_circuits) + 1):
                    if m.evaluate(p[i][j][k]):
                        sol[i].append(k)
        #print(sol)
    elif s.reason_unknown() == "timeout":
        print("Solver timeout")
    else:
        print("Failed to solve")
    return sol

start = time.time()
middle = start
for instance_number in range(len(instances)):
    print("Solving instance: ", (instance_number + 1))
    number_of_circuits, circuits_width, circuits_height, width = get_variables(instance_number)
    starting_height = int(math.ceil(sum([circuits_width[i] * circuits_height[i] for i in range(number_of_circuits)]) / width))
    height_i = starting_height
    s = Solver()

    times = 300 * 1000 # 300 sec
    s.set(timeout=times)

    middle = time.time()
    sol = vlsi(s, height_i)
        
    if (sol) :
        print("Solved instance %i in %f seconds (%f sec)" %((instance_number  +1), (time.time() - start), (time.time() - middle)))	
        start_x = [False]*(number_of_circuits)
        start_y = [False]*(number_of_circuits)
        flag = [False]*(number_of_circuits)
        for i in range(len(sol)):
            for j in range(len(sol[0])):
                for n in range(number_of_circuits):
                    if sol[i][j] == n and not(flag[n]):
                        flag[n] = True
                        start_x[n] = j
                        start_y[n] = i
        circuits = [[circuits_width[i], circuits_height[i], start_x[i], start_y[i]] for i in range(number_of_circuits)]
        plot_solution(width, height_i, circuits, f'output/SAT/images/out-{instance_number+1}.png')
        output_solution(instances[instance_number], height_i, start_x, start_y, f'output/SAT/solutions/out-{instance_number + 1}.txt')