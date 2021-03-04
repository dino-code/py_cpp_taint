#!/usr/bin/env python

import hello

myname = "Joe"
myname = taint(myname)

ans1 = hello.greet(myname)

print(ans1)

def taint(val):
    return val
