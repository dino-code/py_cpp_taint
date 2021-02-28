# pybind11
is a lightweight header-only library that exposes C++ types in Python and vice versa.

# Installation
first clone https://github.com/pybind/pybind11
### Building with [cppimport](https://github.com/tbenthompson/cppimport)
 cppimport is a small Python import hook that determines whether there is a C++ source file whose name matches the requested module. If there is, the file is compiled as a Python extension using pybind11 and placed in the same folder as the C++ source file. Python is then able to find the module and load it.
 
If you are using windows with MSVS then you need an environment with python 3.6 or above. (please note I tested cppimport with python 3.5 and it didn't work. this is mentioned also in one of the issues)
- conda create -n envpybind python=3.6
- conda activate envpybind
- pip install cppimport
Examples of using cppimport with pybind11 exists in: https://github.com/tbenthompson/cppimport

### Building with CMake - c++ to python
For C++ codebases that have an existing CMake-based build system, a Python extension module can be created with just a few lines of code:

```python
cmake_minimum_required(VERSION 3.0)
project(example)

add_subdirectory(pybind11)
pybind11_add_module(example example.cpp)
```
This assumes that the pybind11 repository is located in a subdirectory named pybind11 and that the code is located in a file named example.cpp. The CMake command add_subdirectory will import the pybind11 project which provides the pybind11_add_module function. It will take care of all the details needed to build a Python extension module on any platform.
** After configuring by cmake, building in MSVS you will get .pyd file like 'example.cp36-win_amd64.pyd' as output from the build. you just need to put this .pyd file next to .py file or the jupyter notebook and import it like 'import example'**

### Building with CMake - python to c++
```python
cmake_minimum_required(VERSION 3.0)
project(callpythonfromcplusplustest)

add_subdirectory(pybind11)

add_executable(pythoncallfromcplusplustest pythoncallfromcplusplustest.cpp)
target_link_libraries(pythoncallfromcplusplustest PRIVATE pybind11::embed)
```

of course there are also other options like setuptools. you can check all building approaches in:
https://pybind11.readthedocs.io/en/stable/compiling.html

# Examples in this repo:
- c++ to python examples:
    - example.cpp and example.ipynb shows the simplest example for square function of input number
   - sumandsort.cpp and sum_and_sort_std_vector.ipynb shows one function to accumulate a vector and another function to sort
   - classtest.cpp and class_set_get.ipynb shows how to call c++ class from python with constructor/set/get
   - vectorizefunction.cpp and vectorize_numpy_array.ipynb shows how to multiply two numpy matrices x,y with scalar z
   
- python to c++ example:
    - pythoncalltest.cpp shows how to call python types from c++, casting of types, import python modules from c++, and how to execute python script in c++.

# Documentation
for more examples and details:
https://pybind11.readthedocs.io/en/stable/basics.html
there is ability to use numpy and Eigen

# Examples
https://github.com/pybind/pybind11/tree/master/tests

# pybind11 Supported compilers
- Clang/LLVM 3.3 or newer (for Apple Xcode's clang, this is 5.0.0 or newer)
- GCC 4.8 or newer
- Microsoft Visual Studio 2015 Update 3 or newer
- Intel C++ compiler 17 or newer (16 with pybind11 v2.0 and 15 with pybind11 v2.0 and a workaround)
- Cygwin/GCC (tested on 2.5.1)