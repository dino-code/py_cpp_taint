#include "sumandsort.cpp"
#include <vector>
namespace py = pybind11;

std::vector<int> taint(std::vector<int> val) {
	return val;
}
std::vector<int> sink(std::vector<int> val) {
	return val;
}
int main() {

	const std::vector<int> theVec0 = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
	const std::vector<int> theVec1 = taint(theVec0);
	std::vector<int> ans;
	ans = sort_vector(theVec1);
	sink(ans);
}