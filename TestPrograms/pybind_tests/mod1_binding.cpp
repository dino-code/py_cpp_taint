
#include <pybind11/pybind11.h>
#include <cmath>

namespace py = pybind11;

float msin( float x )
{
    //std::cout << "wtf?? sin" << std::endl;
    return sin(x);
}

float mpow( float a, float b )
{
    //::cout << "wtf?? pow" << std::endl;
    return pow( a, b );
}

PYBIND11_MODULE(mod1_binding, m)
{

    m.doc() = R"pbdoc(
        Bindings for sample module 1
    )pbdoc";

    m.def( "msin", &msin );
    m.def( "mpow", &mpow );

    m.attr( "__version__" ) = "dev";

}
