import vectorizefunction
import example
import sumandsort

a = 1
b = 3.0
c = 4.0

a = taint(a)
b = taint(b)
c = taint(c)

#vectorizefunction.vectorized_func(a, b, c)

d = 5
d = taint(d)

ans1 = example.square(d)

e = [1, 2, 3, 4, 5]
e = taint(e)

ans2 = sumandsort.sum_vec(e)

ans3 = sumandsort.sort_vector(e)

print(ans1)
print(ans2)
print(ans3)

def taint(x):
    return x
