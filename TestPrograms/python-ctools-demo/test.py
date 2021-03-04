import py11taylor

a = 5.0
b = 10
a = taint(a)
b = taint(b)

ans1 = py11taylor.ts_sin(a, b)

ans2 = py11taylor.ts_cos(a, b)

print(ans1)
print(ans2)

def taint(x):
    return x
