#include <pybind11/pybind11.h>
#include <Python/Python.h>
#include <iostream>
#include <vector>
#include "stubs.cpp"

#define STUBS

#ifdef STUBS
#define PyList_Append(x, y) myPyList_Append(x, y)
#endif

namespace py = pybind11;

std::vector<std::vector<int>> populateArray(py::list);
void printVec(std::vector<std::vector<int>>);
std::vector<std::vector<int>> matMult(std::vector<std::vector<int>>, std::vector<std::vector<int>>);
std::vector<int> convList (py::list);
std::vector<std::vector<int>> constr2DVec (std::vector<int>);
std::vector<std::vector<int>> pythonMult (std::vector<std::vector<int>> matOne, std::vector<std::vector<int>> matTwo);
PyObject * convertVecToList (std::vector<std::vector<int>> mat);

// for testing taint being introduced within matMult.cpp
std::vector<int> t(std::vector<int> data) {
    return data;
}

std::vector<std::vector<int>> multiply(py::list pyVec) {
    std::vector<int> data = convList(pyVec);

    for (int i = 0; i < data.size(); i++) fakeData.push_back(i);
    
    std::vector<int> matOneBase;
    for (int i = 0; i < 9; ++i) matOneBase.push_back(data.at(i));
    
    std::vector<int> matTwoBase;
    for (int i = 9; i < data.size(); ++i) matTwoBase.push_back(data.at(i));
    
    std::vector<std::vector<int>> matOne = constr2DVec(matOneBase);
    std::vector<std::vector<int>> matTwo = constr2DVec(matTwoBase);
    
    std::vector<std::vector<int>> matThree = matMult(matOne, matTwo);

    return matThree;
}

PyObject * convertVecToList (std::vector<std::vector<int>> mat) {
        PyObject *lol = PyList_New(0);
        PyObject *temp = PyList_New(0);

        // Here, we convert the two matricies to be multiplied into Python lists
        for (int i = 0; i < mat.size(); i++) {
            for (int j = 0; mat.at(i).size(); j++) {
                PyList_Append(temp, PyLong_FromLong(mat.at(i).at(j)));
            }
            PyList_Append(lol, temp);
            temp = PyList_New(0);
        }

        return lol;
}

std::vector<std::vector<int>> pythonMult (std::vector<std::vector<int>> matOne, std::vector<std::vector<int>> matTwo) {
    std::vector<std::vector<int>> ans;
    PyObject *myModule;

    Py_Initialize();
    
    // These lines are necessary to allow the import of prog.py
    PyRun_SimpleString("import os\n");
    PyRun_SimpleString("import sys\n");
    PyRun_SimpleString("sys.path.append(os.getcwd())");
    
    // This line imports the module Prog.py
    myModule = PyImport_ImportModule("final");

    if (myModule != NULL) {
        PyObject *args; 
        PyObject *myFunction = PyObject_GetAttrString(myModule, "pythFunc");
        PyObject *lol1 = PyList_New(0);
        PyObject *lol2 = PyList_New(0);      // lol stands for list of lists
        PyObject *temp = PyList_New(0);

        // Here, we convert the two matricies to be multiplied into Python lists
        for (int i = 0; i < matOne.size(); i++) {
            for (int j = 0; matOne.at(i).size(); j++) {
                PyList_Append(temp, PyLong_FromLong(matOne.at(i).at(j)));
            }
            PyList_Append(lol1, temp);
            temp = PyList_New(0);
        }

        for (int i = 0; i < matTwo.size(); i++) {
            for (int j = 0; matTwo.at(i).size(); j++) {
                PyList_Append(temp, PyLong_FromLong(matTwo.at(i).at(j)));
            }
            PyList_Append(lol2, temp);
            temp = PyList_New(0);
        }

        // this portion sets up the lol's as args to pass to the python function
        args = PyTuple_New(2);
        PyTuple_SetItem(args, 0, lol1);
        PyTuple_SetItem(args, 1, lol2);

        // here, the python function is called by passing the callable object and the
        // arguments
        // cast matOne to PyObject *
        // (PyObject *)matOne  --> casting example

        PyObject *myResult = PyObject_CallObject(myFunction, args);
        PyObject *outer;
        std::vector<int> tempVec;

        for(Py_ssize_t i = 0; i < Py_SIZE(myResult); i++) {
            outer = PyList_GetItem(myResult, i);
            for (Py_ssize_t j = 0; j < Py_SIZE(outer); j++) {
                tempVec.push_back(PyLong_AsLong(PyList_GetItem(outer, j)));
            }
            ans.push_back(tempVec);
            tempVec.clear();
        }

    }
    else {
        // if the module cannot be loaded, this error is thrown.
        PyErr_Print();
    }

    Py_Finalize(); 

    return ans;
}

std::vector<int> convList (py::list pyVec) {
    std::vector<int> data;
    
    for (auto element : pyVec) {
        data.push_back(element.cast<int>());
    }
    
    return data;
}

std::vector<std::vector<int>> constr2DVec (std::vector<int> vec) {
    std::vector<std::vector<int>> newVec;
    std::vector<int> row;
    
    int counter = 0;
    
    for (int i = 0; i < vec.size(); ++i) {
        
        row.push_back(vec.at(i));
        counter++;
        
        if (counter == 3) {
            newVec.push_back(row);
            row.clear();
            counter = 0;
        }
        
    }
        
    return newVec;
}

std::vector<std::vector<int>> populateArray(py::list pyVec) {
	std::vector<std::vector<int>> vec;
	std::vector<int> vecRow;

	for (auto row : pyVec) {
                for (auto val : row) {
                        vecRow.push_back(val.cast<int>());
                        //std::cout << val.cast<int>() << " ";
                }
                vec.push_back(vecRow);
                vecRow.clear();
        }
	
	return vec;
}

// this function multiplies the 2 matrices given to it and returns the result.
std::vector<std::vector<int>> matMult(std::vector<std::vector<int>> A, std::vector<std::vector<int>> B) {
	std::vector<std::vector<int>> C;
	std::vector<int> row;
	int val = 0;

	for (int i = 0; i < A.size(); ++i) {
		for (int j = 0; j < B.size(); ++j) {
			for (int k = 0; k < A.size(); ++k) {
				val += A[i][k] * B[k][j];
			}
			row.push_back(val);
			val = 0;
		}
		C.push_back(row);
		row.clear();
	}
	return C;
}

// this code allows for the Pybind11 module to be created.
PYBIND11_MODULE(matMult, m) {
    m.doc() = "pybind11 example plugin"; // optional module docstring

    m.def("multiply", &multiply, "A function which multiplies two numbers");
    //m.def("test", &test, "A test for search string")
}
