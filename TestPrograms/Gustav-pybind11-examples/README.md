# Example of how to get pybind11 to work

Just a simple example of how to get pybind11 [1] to work with C++ and numpy.

This repository includes the pybind11 code as a submodule, it must be initialized after cloning the repository.

```bash
git submodule update --init --recursive
```
This must be done once before compiling.

After compiling move or symlink the resulting .so files into the python package so it can be found
the files should have names like:
example_class.cpython-36m-x86_64-linux-gnu.so
example_functions.cpython-36m-x86_64-linux-gnu.so
If you recompile and move the files you will need to copy them again, so it is usually more convenient to use a symlink.

## Requirements for ubuntu 18.04:
python3-dev
cmake


# Help, it does not work!
* The module name must match in cmake and in the c++ file
* you need to move or symlink the compiled .so files from the build directory to the python directory for python to find them correctly
* you compiled for one python version, (check the filename) but are running a different one

[1] https://github.com/pybind/pybind11
