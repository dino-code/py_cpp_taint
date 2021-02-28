#!/usr/bin/env python

import hello

myname = "Joe"
myname = taint(myname)

hello.greet(myname)

def taint(val):
    return val
