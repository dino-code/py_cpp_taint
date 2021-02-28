#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

// ----------------
// Regular C++ code
// ----------------

// multiply all entries by 2.0
// input:  nested std::vector ([[...],[...]]) (read-only)
// output: nested std::vector ([[...],[...]]) (new copy)
std::vector<std::vector<double>> modify(const std::vector<std::vector<double>>& input)
{
    std::vector<std::vector<double>> output(input.size());

    std::vector<double> temp;
    for ( size_t i = 0 ; i < input.size() ; ++i ) {
        for (size_t j = 0; j < input[i].size(); ++j) {
            temp.push_back(2*input[i][j]);
        }
        output[i] = temp;
        temp.clear();
    }

  return output;
}

// ----------------
// Python interface
// ----------------

namespace py = pybind11;

PYBIND11_MODULE(example,m)
{
  m.doc() = "pybind11 example plugin";

  m.def("modify", &modify, "Multiply all entries of a nested list by 2.0");
}
