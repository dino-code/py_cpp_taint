import pybind11_example
    
a = [1, 2, 3, 4, 5]
a = taint(a)

pybind11_example.sum_arrays(a)

pybind11_example.product_arrays(a)


def taint(x):
    return x
