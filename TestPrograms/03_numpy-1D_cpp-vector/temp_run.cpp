#include "example.cpp"
#include <vector>
namespace py = pybind11;

std::vector<double> taint(std::vector<double> val) {
	return val;
}
std::vector<int> sink(std::vector<int> val) {
	return val;
}
int main() {

	const std::vector<double> theVec0 = {1.0, 2.0, 3.0};
	const std::vector<double> theVec1 = taint(theVec0);
	std::vector<int> ans;
	ans = multiply(theVec1);
	sink(ans);
}