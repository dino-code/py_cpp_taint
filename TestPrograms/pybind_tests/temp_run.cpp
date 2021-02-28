#include "mod1_binding.cpp"
#include <vector>
namespace py = pybind11;

float taint(float val) {
	return val;
}
float sink(float val) {
	return val;
}
int main() {

	float tVal0 = 1.0;
	float tVal1 = taint(tVal0);
	float tVal2 = 1.0;
	float tVal3 = taint(tVal2);
	float ans;
	ans = mpow(tVal1, tVal3);
	sink(ans);
}