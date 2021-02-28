#include "py11taylor.cpp"
#include <vector>
namespace py = pybind11;

double taint(double val) {
	return val;
}
int taint(int val) {
	return val;
}
double sink(double val) {
	return val;
}
int main() {

	double tVal0 = 1.0;
	double tVal1 = taint(tVal0);
	int tVal2 = 1;
	int tVal3 = taint(tVal2);
	double ans;
	ans = ts_cos(tVal1, tVal3);
	sink(ans);
}