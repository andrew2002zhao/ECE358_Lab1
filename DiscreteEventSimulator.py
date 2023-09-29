from math import log,e
from numpy.random import uniform
from numpy import array, vectorize

NUM_SAMPLE = 1000

def simulateExponential(rate):
    # rate must be bigger than 0
    if rate <= 0:
        return []
    # natural logarithm
    def _ln(x):
        return log(x,e)
    
    # generate NUM_SMAPLE points from uniform distribution
    U = array(uniform(low=0.0, high=1.0, size=NUM_SAMPLE))

    # vectorize ln function to apply to numpy array
    _vln = vectorize(_ln)

    # return numpy array of NUM_SAMPLE points using formula outlined in doc
    return array(-(1/rate)*_vln(1-U))
    
    

exp75 = simulateExponential(75)
print(exp75.mean(), exp75.var())
