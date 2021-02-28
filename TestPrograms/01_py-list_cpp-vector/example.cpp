#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>

// ----------------
// Regular C++ code
// ----------------

// multiply all entries by 2.0
// input:  std::vector ([...]) (read only)
// output: std::vector ([...]) (new copy)
std::vector<double> modify(const std::vector<double>& input)
{
  std::vector<double> output(input.size());
    
  for ( size_t i = 0 ; i < input.size() ; ++i )
     output[i] = 2. * input[i];

  return output;
}

// ----------------
// Python interface
// ----------------

namespace py = pybind11;

PYBIND11_MODULE(example,m)
{
  m.doc() = "pybind11 example plugin";

  m.def("modify", &modify, "Multiply all entries of a list by 2.0");
}


#include <iostream>
#include <string>

class Base
{
public:
    virtual std::string name() const { return "Base"; }
    virtual ~Base() {}
};

class Derived : public Base
{
public:
    virtual std::string name() const { return "Derived"; }
};

void fb(Base *b)
{
    std::cout << b->name() << " called." << std::endl;
}

void fd(Derived *d)
{
    std::cout << "Derived " << d->name() << " called." << std::endl;
}

Base* factory()
{
    return new Derived;
}
