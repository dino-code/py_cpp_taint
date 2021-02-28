#include "example.cpp"
#include <vector>
namespace py = pybind11;

double taint(double val) {
	return val;
}
double sink(double val) {
	return val;
}
int main() {

	double tVal0 = 1.0;
	double tVal1 = taint(tVal0);
	double tVal2 = 1.0;
	double tVal3 = taint(tVal2);
	double ans;
	ans = mulDouble(tVal1, tVal3);
	sink(ans);
}