#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

int sum_arrays(std::vector<int> lst) {
  int sum = 0;
  for (auto& n: lst) {
    sum += n;
  }
  return sum;
}

int product_arrays(std::vector<int> lst) {
  int sum = 1;
  for (auto& n: lst) {
    sum *= n;
  }
  return sum;
}

PYBIND11_MODULE(pybind11_example, m) {
  m.doc() = "Example pybind11"; // optional module docstring
  m.def("sum_arrays", &sum_arrays);
  m.def("product_arrays", &product_arrays);
}

