#include "matMult.cpp"
#include <vector>
namespace py = pybind11;

std::vector<int> taint(std::vector<int> val) {
	return val;
}
std::vector<std::vector<int>> sink(std::vector<std::vector<int>> val) {
	return val;
}
int main() {

	std::vector<int> theVec0 = taint({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12});
	py::list pyList0 = py::cast(theVec0);
	std::vector<std::vector<int>> ans;
	ans = multiply(pyList0);
	sink(ans);
}