#include "mod1_binding.cpp"
#include <vector>
namespace py = pybind11;

float sink(float val) {
	return val;
}
int main() {

	float ans;
	ans = msin();
	sink(ans);
}