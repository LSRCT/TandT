""""
A minimal example for using mystic with a custom cost function.
-AN
"""


import numpy as np
import cmath
import mystic
import sys
import matplotlib.pyplot as plt


def opt(real):
    startData = [1E-9, 1E-9]  # start values for the solver. not all need this
    bnds = ((1E-20, 1E2), (1E-20, 1E5))
    sol = mystic.solvers.fmin_powell(minfunc, startData, bounds = bnds, args=(real,))
    return sol


def minfunc(data, real):
    x = range(len(real))
    comps = {"slope": data[0], "yinter": data[1]}  # not necessary but makes it less confusing with many parameters
    simVals = comps["slope"]*x+comps["yinter"]
    ersum = np.sum(np.abs((np.array(real)-np.array(simVals))))
    return ersum


if __name__ == '__main__':
    optV = np.random.normal(size=100)+ np.linspace(0, 10, 100)
    sol = opt(optV)
    x = range(len(optV))
    solVals = sol[0] * x + sol[1]
    plt.plot(optV)
    plt.plot(solVals)
    plt.show()
