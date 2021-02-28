#include "packbind.cpp"
#include <vector>
namespace py = pybind11;

uint64_t taint(uint64_t val) {
	return val;
}
float sink(float val) {
	return val;
}
int main() {

	uint64_t val0 = 1;
	uint64_t val1 = taint(val0);
	float ans;
	ans = unpack(val1);
	sink(ans);
}