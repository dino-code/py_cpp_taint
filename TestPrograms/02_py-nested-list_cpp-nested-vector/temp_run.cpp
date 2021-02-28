#include "example.cpp"
#include <vector>
namespace py = pybind11;

std::vector<std::vector<double>> taint(std::vector<std::vector<double>> val) {
	return val;
}
std::vector<std::vector<double>> sink(std::vector<std::vector<double>> val) {
	return val;
}
int main() {

	const std::vector<std::vector<double>> theVec0 = {{1.0, 2.0}, {3.0, 4.0}, {5.0, 6.0}};
	const std::vector<std::vector<double>> theVec1 = taint(theVec0);
	std::vector<std::vector<double>> ans;
	ans = modify(theVec1);
	sink(ans);
}