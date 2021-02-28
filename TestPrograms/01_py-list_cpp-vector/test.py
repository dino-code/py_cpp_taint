
import example

A = taint([1.,2.,3.,4.])

B = example.modify(A)

print(B)
