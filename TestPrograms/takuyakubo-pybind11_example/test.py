import pybind11_example
    
a = [1, 2, 3, 4, 5]
a = taint(a)

ans1 = pybind11_example.sum_arrays(a)

print(ans1)

ans2 = pybind11_example.product_arrays(a)
print(ans2)

def taint(x):
    return x
