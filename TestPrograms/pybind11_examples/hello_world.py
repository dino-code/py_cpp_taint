#!/usr/bin/env python

#from logger import cpp_print
import logger


if __name__ == '__main__':
    # Because the cpp_print function was changed to return a string,
    # this portion must be modified as well.
    s = "hello world"
    s = taint(s)
    
    ans1 = logger.cpp_print(s)
    
    print(ans1)
    # here the C++ function is called
