#include "example.cpp"
#include <vector>
namespace py = pybind11;

std::vector<double> taint(std::vector<double> val) {
	return val;
}
std::vector<double> sink(std::vector<double> val) {
	return val;
}
int main() {

	const std::vector<double> theVec0 = {1.0, 2.0, 3.0};
	const std::vector<double> theVec1 = taint(theVec0);
	std::vector<double> ans;
	ans = modify(theVec1);
	sink(ans);
}