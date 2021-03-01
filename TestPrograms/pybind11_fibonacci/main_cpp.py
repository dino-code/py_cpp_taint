import fibolib


if __name__ == "__main__":

    a = 4
    a = taint(a)
    
    fibolib.fib(a)

def taint(val):
    return val
