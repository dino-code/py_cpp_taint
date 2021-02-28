import numpy as np
import example

A = taint(10.)
B = taint(20.)
C = taint(10)

ans = example.mulInt(A, C)
print(ans)

ans = example.mulDouble(C, B)
print(ans)

ans = example.mulDouble(B, B)
print(ans)

