import mod1_binding

a = 5.0
b = 2.0
a = taint(a)
b = taint(b)

mod1_binding.msin(a)

mod1_binding.mpow(a, b)

def taint(x):
    return x
