/*cppimport
<%
setup_pybind11(cfg)
%>
*/

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <algorithm>

namespace py = pybind11;

int sum_vec(const std::vector<int> &v) {
	int sum = 0;
	for (const auto& item : v)
	{
		sum += item;
	}
	return sum;
}

std::vector<int> sort_vector(const std::vector<int> &v) {
	std::vector<int> copy_v = v;
	std::sort(copy_v.begin(), copy_v.end(), [](int a, int b)  { return a > b; });
	return copy_v;
}

PYBIND11_MODULE(sumandsort, m) {
	m.def("sum_vec", &sum_vec);
	m.def("sort_vector", &sort_vector, py::return_value_policy::copy);
}
