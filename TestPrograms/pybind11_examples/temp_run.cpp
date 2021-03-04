#include "logger.cpp"
#include <vector>
namespace py = pybind11;

std::string taint(std::string val) {
	return val;
}
std::string sink(std::string val) {
	return val;
}
int main() {

	std::string tVal0 = "hi";
	std::string tVal1 = taint(tVal0);
	std::string ans;
	ans = cpp_print(tVal1);
	sink(ans);
}