#include <string>

std::string greet(std::string s)
{
   return "hello, world " + s;
}

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(hello, m)
{
//py::module m("hello","Greeting module");
    m.def("greet", &greet);
//return m.ptr();
}
