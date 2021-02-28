/*cppimport
<%
setup_pybind11(cfg)
%>
*/
#include <pybind11/pybind11.h>

namespace py = pybind11;

int square(int x) {
    return x * x;
}

PYBIND11_MODULE(example, m) {
    m.def("square", &square);
}
