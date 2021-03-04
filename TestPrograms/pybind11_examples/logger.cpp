#include <iostream>
#include <string>

#include <pybind11/pybind11.h>

// changed from void to string
std::string cpp_print(std::string value)
{   
    //std::cout << value << std::endl;
    return value;
}

PYBIND11_MODULE(logger, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("cpp_print", &cpp_print, "A print function implemented in c++");
}
