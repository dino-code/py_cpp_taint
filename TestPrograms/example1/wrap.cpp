#include <pybind11/pybind11.h>

namespace py = pybind11;

using namespace pybind11::literals;

int add(int i, int j) {
    return i + j;
}

PYBIND11_MODULE(wrap, m) {
    //py::module m("wrap", "pybind11 example plugin");
    m.def("add", &add, "A function which adds two numbers");
    //return m.ptr();
}
