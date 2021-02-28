#include <pybind11/pybind11.h> // main pybind11 header
#include <pybind11/stl.h> // required for the magical conversion from python list to std::vector

#include <vector>
#include <algorithm>

namespace py = pybind11; //type less

double compute_mean(const std::vector<double>& values){
    double mean = 0;
    const size_t bigN = values.size();
    
    for (auto val : values) mean += val;
    
    mean /= values.size();
    
    /*
    std::for_each(values.begin(), values.end(), [&] (int n){
            mean += n / bigN;
    });*/

    return mean;
}

// define the bindings between the c++ code to the python names here.
// the object m is the representation of the python module in c++
// the name of the module is "example_functions" in python.
// IT IS EXTREMELY IMPORTANT THAT THE MODULE NAME MATCHES HERE AND IN THE CMAKE FILE
PYBIND11_MODULE(example_functions, m){
    //docstring for the module
    m.doc() = "A small example of a pybind11 plugin";
    //define the binding from the c++ function "compute_mean", to the python name "mean"
    m.def("mean", &compute_mean, "A function that computes the mean of a list of numbers");
}
