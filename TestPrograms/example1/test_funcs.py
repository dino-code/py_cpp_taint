import wrap

if __name__ == '__main__':
    a = 3
    a = taint(a)

    b = 2
    b = taint(b)
    
    wrap.add(a, b)
    
    print(wrap)
