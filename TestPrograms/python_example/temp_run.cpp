#include "python_example.cpp"
#include <vector>
namespace py = pybind11;

int taint(int val) {
	return val;
}
int sink(int val) {
	return val;
}
int main() {

	int tVal0 = 1;
	int tVal1 = taint(tVal0);
	int tVal2 = 1;
	int tVal3 = taint(tVal2);
	int ans;
	ans = subtract(tVal1, tVal3);
	sink(ans);
}