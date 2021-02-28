
import example

A = taint([[1,2,3,4],[5,6]])

B = example.modify(A)

print(B)
