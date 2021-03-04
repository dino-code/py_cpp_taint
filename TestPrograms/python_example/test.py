import python_example

#assert python_example.__version__ == '0.0.1'

a = 1
b = 2
a = taint(a)
b = taint(b)

ans1 = python_example.add(a, b)
ans2 = python_example.subtract(a, b)

print(ans1)
print(ans2)

def taint(x):
    return x
