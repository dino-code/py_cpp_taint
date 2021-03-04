#!/usr/bin/env python3
#
# pybind11 version of pack.py
# You may compare the result with ieee754 implementation with C and pack.py
#
import packbind

def main():
    f = 3.1415926
    f = taint(f)

    netf = packbind.pack(f)
    f2 = packbind.unpack(netf)

    print("Original: {}".format(f))
    print(" Network: {}".format(hex(netf)))
    print("Unpacked: {}".format(f2))
    
    print(netf)
    print(f2)

if __name__ == '__main__':
    main()

def taint(x):
    return x
