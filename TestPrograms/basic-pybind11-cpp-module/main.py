import numpy as np
import pybind_test

c = 5
c = taint(c)

factorialResult = pybind_test.factorial(c)

a = np.ones((10,3)) * 2
b = np.ones((10,3)) * 3

a = taint(a)
b = taint(b)

addResult = pybind_test.add_arrays(a, b)

print(factorialResult)
print(addResult)

def taint(val):
    return val
