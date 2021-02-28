
import numpy as np
import example

A = taint([0,1,2,3,4,5])
B = example.multiply(A)

print('input list = ',A)
print('output     = ',B)

A = taint(np.arange(10))
B = example.multiply(A)

print('input list = ',A)
print('output     = ',B)


