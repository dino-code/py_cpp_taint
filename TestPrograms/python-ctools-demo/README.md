[![Build Status](https://travis-ci.org/bast/python-cffi-demo.svg?branch=master)](https://travis-ci.org/bast/python-cffi-demo/builds)
[![License](https://img.shields.io/badge/license-%20MPL--v2.0-blue.svg)](../master/LICENSE)


# python-cython-demo

Inspired by Kurt W. Smith's book on [Cython](http://shop.oreilly.com/product/0636920033431.do)

## Example

This example make use of a simple C++ source code which implements two Taylor
series sinus() and cosinus(). The point is to illustrate how C/C++ functions
can be called from python with the use of Cython.

## Lower-level learning goals

- Show how distutils can be used to build a Python library
- Show how CMake can be used to accomblish the same thing

## Requirements

- Python
- Cython
- [CMake](https://cmake.org/download/)
- C++ compilers


## Installing Python dependencies

In this example using [Virtual Environments](http://python-guide.readthedocs.io/en/latest/dev/virtualenvs/)
but also
[Anaconda](https://www.continuum.io/downloads) or
[Miniconda](https://conda.io/miniconda.html) will do the job:

