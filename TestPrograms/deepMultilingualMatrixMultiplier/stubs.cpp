/*
Created by Dino Becaj
Date: 12/5/2020

Summary: This file was created to define stub functions for the C++ to Python API defined by Python.h.
It is necessary because without it, py_cpp_taint is unable to track taint through the existing API calls.
The hope is that through these stub definitions, py_cpp_taint will be able to track taint through
the matMult.cpp.
*/

#include <Python/Python.h>

int myPyList_Append(PyObject *, PyObject *);

int myPyList_Append(PyObject * list, PyObject * val) {
    // pushes the tainted PyObject val into another PyObject called list much like
    // actually happens in the real PyList_Append()

    list = val;

    // when casting, might have to cast to void first (like last time)
    // try pointers to ints
    
    return 1;
}