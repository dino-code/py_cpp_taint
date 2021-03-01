#include <cstdint>
#include <pybind11/pybind11.h>

uint64_t fib(uint64_t n) {
    if (n <= 1) {
        return 1;
    }
    return fib(n -1) + fib(n - 2);
}

PYBIND11_MODULE(fibolib, m) {
    m.doc() = "pybind11 fibonacci plugin"; // optional module docstring

    m.def("fib", &fib, "A function that computes the n number of the Fibonacci sequence");
}
