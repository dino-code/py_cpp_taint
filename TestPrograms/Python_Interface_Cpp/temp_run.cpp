#include "fibonacci.cpp"
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
	int ans;
	ans = compute_fibonacci(tVal1);
	sink(ans);
}