#include "pybind11_example.cpp"
#include <vector>
namespace py = pybind11;

std::vector<int> taint(std::vector<int> val) {
	return val;
}
int sink(int val) {
	return val;
}
int main() {

	std::vector<int> theVec0 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
	std::vector<int> theVec1 = taint(theVec0);
	int ans;
	ans = product_arrays(theVec1);
	sink(ans);
}