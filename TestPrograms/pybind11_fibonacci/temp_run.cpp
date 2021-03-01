#include "fibolib.cpp"
#include <vector>
namespace py = pybind11;

uint64_t taint(uint64_t val) {
	return val;
}
uint64_t sink(uint64_t val) {
	return val;
}
int main() {

	uint64_t val0 = 1;
	uint64_t val1 = taint(val0);
	uint64_t ans;
	ans = fib(val1);
	sink(ans);
}