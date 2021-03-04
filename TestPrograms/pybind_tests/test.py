import mod1_binding

a = 5.0
b = 2.0
a = taint(a)
b = taint(b)

ans1 = mod1_binding.msin(a)

ans2 = mod1_binding.mpow(a, b)

print(ans1)
print(ans2)

def taint(x):
    return x
