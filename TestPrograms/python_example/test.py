import python_example

#assert python_example.__version__ == '0.0.1'

a = 1
b = 2
a = taint(a)
b = taint(b)

python_example.add(a, b)
python_example.subtract(a, b)

def taint(x):
    return x
