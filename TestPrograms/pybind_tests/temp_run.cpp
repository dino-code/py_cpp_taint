#include "mod1_binding.cpp"
#include <vector>
namespace py = pybind11;

float sink(float val) {
	return val;
}
int main() {

	float tVal0 = 1.0;
	float ans;
	ans = msin(tVal0);
	sink(ans);
}