#include <pybind11/pybind11.h>

#include "taylor_series.h"

namespace py = pybind11;

PYBIND11_MODULE(taylor,t) {
  t.doc() = "Taylor Series tailored plugin";
  t.def("sin", &ts_sin, "A sine Taylor Series function")
   .def("cos", &ts_cos, "A cosine Taylor Series function");
}
