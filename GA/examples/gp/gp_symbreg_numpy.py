#    This file is part of EAP.
#
#    EAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    EAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with EAP. If not, see <http://www.gnu.org/licenses/>.

import operator
import math
import random

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

# Define new functions
def safeDiv(left, right):
    with numpy.errstate(divide='ignore',invalid='ignore'):
        x = numpy.divide(left, right)
        if isinstance(x, numpy.ndarray):
            x[numpy.isinf(x)] = 0
            x[numpy.isnan(x)] = 0
        elif numpy.isinf(x) or numpy.isnan(x):
            x = 0
    return x

pset = gp.PrimitiveSet("MAIN", 1)
pset.addPrimitive(numpy.add, 2)
pset.addPrimitive(numpy.subtract, 2)
pset.addPrimitive(numpy.multiply, 2)
pset.addPrimitive(safeDiv, 2)
pset.addPrimitive(numpy.negative, 1)
pset.addPrimitive(numpy.cos, 1)
pset.addPrimitive(numpy.sin, 1)
pset.addEphemeralConstant(lambda: random.randint(-1,1))
pset.renameArguments(ARG0='x')

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin, pset=pset)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genRamped, pset=pset, min_=1, max_=2)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("lambdify", gp.lambdify, pset=pset)

samples = numpy.linspace(-1, 1, 10000)
values = samples**4 + samples**3 + samples**2 + samples

def evalSymbReg(individual):
    # Transform the tree expression in a callable function
    func = toolbox.lambdify(expr=individual)
    # Evaluate the sum of squared difference between the expression
    # and the real function values : x**4 + x**3 + x**2 + x 
    diff = numpy.sum((func(samples) - values)**2)
    return diff,

toolbox.register("evaluate", evalSymbReg)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register('mutate', gp.mutUniform, expr=toolbox.expr_mut)

def main():
    random.seed(318)

    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", tools.mean)
    stats.register("std", tools.std)
    stats.register("min", min)
    stats.register("max", max)
    
    algorithms.eaSimple(pop, toolbox, 0.5, 0.1, 40, stats, halloffame=hof)

    return pop, stats, hof

if __name__ == "__main__":
    main()
