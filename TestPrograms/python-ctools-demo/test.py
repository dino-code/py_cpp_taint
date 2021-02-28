import py11taylor

a = 5.0
b = 10
a = taint(a)
b = taint(b)

py11taylor.ts_sin(a, b)

py11taylor.ts_cos(a, b)

def taint(x):
    return x
