#include "pybind_test.cpp"
#include <vector>
namespace py = pybind11;

py::array_t<double> taint(py::array_t<double> val) {
	return val;
}
py::array_t<double> sink(py::array_t<double> val) {
	return val;
}
int main() {

	py::array_t<double> arr0(0, nullptr);
	py::array_t<double> arr1 = taint(arr0);
	py::array_t<double> arr2(0, nullptr);
	py::array_t<double> arr3 = taint(arr2);
	py::array_t<double> ans;
	ans = add_arrays(arr1, arr3);
	sink(ans);
}