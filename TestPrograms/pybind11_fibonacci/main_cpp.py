import fibolib


if __name__ == "__main__":

    a = 4
    a = taint(a)
    
    ans1 = fibolib.fib(a)
    print(ans1)

def taint(val):
    return val
