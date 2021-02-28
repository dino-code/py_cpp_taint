from os import listdir
from os.path import isfile, join
from program import Program
import subprocess
import json

def modifyPyTrigger(function):
    # adds the specified function as a source in the PyT trigger file
    # Standard trigger file included in directory is assumed to be the one used
    trigger = "my_trigger_words.pyt"
    with open(trigger) as f:
        data = json.load(f)
        if function not in data["sources"]:
            data["sources"].append(function)

    with open(trigger, 'w') as t:
        json.dump(data, t, indent='\t')

def modifyCppConfig(function):
    # adds the specified function as a source in the .inferconfig file
    # Standard .inferconfig file included in directory is assumed to be the one used
    config = ".inferconfig"
    with open(config) as c:
        data = json.load(c)
        present = False
        for i in data["quandary-sources"]:
            for j in i:
                if j == 'procedure' and i[j] == function:
                    present = True
        if present == False:
            val = {'procedure': function, 'kind': 'Other'}
            data["quandary-sources"].append(val)
    
    with open(config, 'w') as f:
        json.dump(data, f, indent='\t')

def getCppTypes(directory, modImport):
    modFile = modImport[0]
    func = modImport[1][modImport[1].find('.')+1:]

    # first, find the line where the function in question is declared or defined.
    with open(directory+modFile, 'r') as q:
        for line in q.readlines():
            if func in line:
                theLine = line
                break
    
    # take the line that was found and grab the return type from it.
    returnType = theLine[:theLine.find(' ')]

    # find the parameters passed to the function
    params = theLine[theLine.find('(')+1:theLine.find(')')]
    params = params.split(',')

    # remove spaces
    for i in range(len(params)):
        if params[i][0] == ' ':
            params[i] = params[i][1:]
    
    for i in range(len(params)):
        index = params[i].find(' ')
        if params[i][:index] == 'const':
            params[i] = params[i][:params[i].find(' ', index+1)]
            if '&' in params[i]:
                params[i] = params[i][:len(params[i])-1]
        else:
            params[i] = params[i][:index]
            if '&' in params[i]:
                params[i] = params[i][:len(params[i])-1]

    return returnType, params

def createCppRunFile(directory, modImport, taintCarried):
    
    # I need to open modImport[0] and find the function definition of modImport[1]

    returnType, paramTypes = getCppTypes(directory, modImport)
        
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if taintCarried:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n',
        'namespace py = pybind11;\n\n']

        # keep track of the taint and sink types written to ensure no duplicates
        writtenTypes = []

        # first, we write the taint functions
        for i in range(len(paramTypes)):
            theType = paramTypes[i]
            if theType in writtenTypes:
                continue
            else:
                writtenTypes.append(theType)
            
                if 'const' in theType:
                    theType = theType[6:]
                if paramTypes[0] == 'py::list':
                    lineList.append('std::vector<int> taint(std::vector<int> val) {\n\treturn val;\n}\n')
                else:
                    lineList.append(theType+' taint('+theType+' val) {\n\treturn val;\n}\n')
        
        # we only need one sink function (for the return type)
        lineList.append(returnType+' sink('+returnType+' val) {\n\treturn val;\n}\n')

        lineList.append('int main() {\n\n')

        # keep track of the variables written so that they can be passed to the function.
        varsWritten = []
        count = 0 # to keep track of duplicate values
        for i in range(len(paramTypes)):
            if paramTypes[i] == 'const std::vector<double>' or paramTypes[i] == 'std::vector<double>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {1.0, 2.0, 3.0};\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = taint(theVec'+str(count-1)+');\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::vector<std::vector<double>>' or paramTypes[i] == 'std::vector<std::vector<double>>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {{1.0, 2.0}, {3.0, 4.0}, {5.0, 6.0}};\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = taint(theVec'+str(count-1)+');\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'py::list':
                lineList.append('\tstd::vector<int> theVec'+str(count)+' = taint({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12});\n')
                lineList.append('\t'+paramTypes[i]+' pyList'+str(count)+' = py::cast(theVec'+str(count)+');\n')
                varsWritten.append('pyList'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'pyList);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::vector<int>' or paramTypes[i] == 'std::vector<int>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = taint(theVec'+str(count-1)+');\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::vector<std::vector<int>>' or paramTypes[i] == 'std::vector<std::vector<int>>' or paramTypes[i] == 'const vector<vector<int>>' or paramTypes[i] == 'vector<svector<int>>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18};\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = taint(theVec'+str(count-1)+');\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const int' or paramTypes[i] == 'int':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = 1;\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = taint(tVal'+str(count-1)+');\n')
                varsWritten.append('tVal'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const float' or paramTypes[i] == 'float':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = 1.0;\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = taint(tVal'+str(count-1)+');\n')
                varsWritten.append('tVal'+str(count))
                count+=1
            elif paramTypes[i] == 'const double' or paramTypes[i] == 'double':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = 1.0;\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = taint(tVal'+str(count-1)+');\n')
                varsWritten.append('tVal'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::string' or paramTypes[i] == 'std::string' or paramTypes[i] == 'const string' or paramTypes[i] == 'string':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = \"hi\";\n')
                count+=1
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = taint(tVal'+str(count-1)+');\n')
                varsWritten.append('tVal'+str(count))
                count+=1
            elif paramTypes[i] == 'Eigen::MatrixXd' or paramTypes[i] == 'const Eigen::MatrixXd':
                lineList.append('\t'+paramTypes[i]+' tMat = taint(MatrixXf a(10,15));\n')
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tMat);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'Matrix<double>' or paramTypes[i] == 'const Matrix<double>':
                if lineList[0] != '#include \"matrix.h\"\n':  
                    lineList.insert(0, '#include \"matrix.h\"\n')

                lineList.append('\tdouble* data'+str(count)+' = new double[3];\n')
                count+=1          
                lineList.append('\t'+paramTypes[i]+' tMat'+str(count)+' = taint(Matrix<double>({1, 3}, data'+str(count-1)+'));\n')
                varsWritten.append('tMat'+str(count))
                count+=1


        # once vars are created for all the params, we write the function and pass the params to them.
        lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:])
        for i in range(len(varsWritten)):
            lineList.append(varsWritten[i])
            if i < len(varsWritten)-1:
                lineList.append(', ')
        
        
        lineList.append(');\n\tsink(ans);\n}')

        '''
        # this code only works with one param
        theType = paramTypes[0]
        if 'const' in theType:
            theType = theType[6:]
        #if theType == 'std::vector<double>':
        if paramTypes[0] == 'py::list':
            lineList.append('std::vector<int> taint(std::vector<int> val) {\n\treturn val;\n}\n')
        else:
            lineList.append(theType+' taint('+theType+' val) {\n\treturn val;\n}\n')
        lineList.append(returnType+' sink('+returnType+' val) {\n\treturn val;\n}\n')
        
        # write the main function and everything in it
        lineList.append('int main() {\n\n')
        if paramTypes[0] == 'const std::vector<double>' or paramTypes[0] == 'std::vector<double>':
            lineList.append('\t'+paramTypes[0]+' theVec = taint({1.0, 2.0, 3.0});\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const std::vector<std::vector<double>>' or paramTypes[0] == 'std::vector<std::vector<double>>':
            lineList.append('\t'+paramTypes[0]+' theVec = taint({{1.0, 2.0}, {3.0, 4.0}, {5.0, 6.0}});\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'py::list':
            lineList.append('\tstd::vector<int> theVec = taint({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12});\n')
            lineList.append('\t'+paramTypes[0]+' pyList = py::cast(theVec);\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'pyList);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const std::vector<int>' or paramTypes[0] == 'std::vector<int>':
            lineList.append('\t'+paramTypes[0]+' theVec = taint({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12});\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const std::vector<std::vector<int>>' or paramTypes[0] == 'std::vector<std::vector<int>>' or paramTypes[0] == 'const vector<vector<int>>' or paramTypes[0] == 'vector<svector<int>>':
            lineList.append('\t'+paramTypes[0]+' theVec = taint({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18});\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const int' or paramTypes[0] == 'int':
            lineList.append('\t'+paramTypes[0]+' tVal = taint(1);\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const double' or paramTypes[0] == 'double':
            lineList.append('\t'+paramTypes[0]+' tVal = taint(1);\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'Eigen::MatrixXd' or paramTypes[0] == 'const Eigen::MatrixXd':
            lineList.append('\t'+paramTypes[0]+' tMat = taint(MatrixXf a(10,15));\n')
            lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tMat);\n\tsink(ans);\n}')
        '''

    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        theType = paramTypes[0]
        if 'const' in theType:
            theType = theType[6:]
            
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\nnamespace py = pybind11;\n\n']

        writtenTypes = []

        # first, we write the taint functions
        for i in range(len(paramTypes)):
            theType = paramTypes[i]

            if theType in writtenTypes:
                continue
            else:
                writtenTypes.append(theType)
            
                if 'const' in theType:
                    theType = theType[6:]
        
        # we only need one sink function (for the return type)
        lineList.append(returnType+' sink('+returnType+' val) {\n\treturn val;\n}\n')

        lineList.append('int main() {\n\n')

        # keep track of the variables written so that they can be passed to the function.
        varsWritten = []
        count = 0 # to keep track of duplicate values
        for i in range(len(paramTypes)):
            if paramTypes[i] == 'const std::vector<double>' or paramTypes[i] == 'std::vector<double>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {1.0, 2.0, 3.0};\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::vector<std::vector<double>>' or paramTypes[i] == 'std::vector<std::vector<double>>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {{1.0, 2.0}, {3.0, 4.0}, {5.0, 6.0}};\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'py::list':
                lineList.append('\tstd::vector<int> theVec'+str(count)+' = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};\n')
                lineList.append('\t'+paramTypes[i]+' pyList'+str(count)+' = py::cast(theVec'+str(count)+');\n')
                varsWritten.append('pyList'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'pyList);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const float' or paramTypes[i] == 'float':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = 1.0;\n')
                varsWritten.append('tVal'+str(count))
                count+=1
            elif paramTypes[i] == 'const std::vector<int>' or paramTypes[i] == 'std::vector<int>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::vector<std::vector<int>>' or paramTypes[i] == 'std::vector<std::vector<int>>' or paramTypes[i] == 'const vector<vector<int>>' or paramTypes[i] == 'vector<svector<int>>':
                lineList.append('\t'+paramTypes[i]+' theVec'+str(count)+' = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18};\n')
                varsWritten.append('theVec'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const int' or paramTypes[i] == 'int':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = 1;\n')
                varsWritten.append('tVal'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const double' or paramTypes[i] == 'double':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = 1.0;\n')
                varsWritten.append('tVal'+str(count))
                count+=1
                #lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
            elif paramTypes[i] == 'const std::string' or paramTypes[i] == 'std::string' or paramTypes[i] == 'const string' or paramTypes[i] == 'string':
                lineList.append('\t'+paramTypes[i]+' tVal'+str(count)+' = \"hi\";\n')
                varsWritten.append('tVal'+str(count))
                count+=1
            elif paramTypes[i] == 'Eigen::MatrixXd' or paramTypes[i] == 'const Eigen::MatrixXd':
                lineList.append('\t'+paramTypes[i]+' tMat = MatrixXf a(10,15));\n')
                lineList.append('\t'+returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tMat);\n\tsink(ans);\n}')

        # once vars are created for all the params, we write the function and pass the params to them.
        theFunc = modImport[1][modImport[1].find('.')+1:]
        if theFunc[-1] != '(':
            theFunc = theFunc + '('
        lineList.append('\t'+returnType+' ans;\n\tans = '+theFunc)
        for i in range(len(varsWritten)):
            lineList.append(varsWritten[i])
            if i < len(varsWritten)-1:
                lineList.append(', ')
        
        
        lineList.append(');\n\tsink(ans);\n}')
        '''
        if paramTypes[0] == 'const std::vector<double>' or paramTypes[0] == 'std::vector<double>':
            lineList.append(paramTypes[0]+' theVec = {1.0, 2.0, 3.0};\n')
            lineList.append(returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const std::vector<int>' or paramTypes[0] == 'std::vector<int>':
            lineList.append(paramTypes[0]+' theVec = {1, 2, 3};\n')
            lineList.append(returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const std::vector<std::vector<int>>' or paramTypes[0] == 'std::vector<std::vector<int>>' or paramTypes[0] == 'const vector<vector<int>>' or paramTypes[0] == 'vector<svector<int>>':
            lineList.append(paramTypes[0]+' theVec = {1, 2, 3};\n')
            lineList.append(returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'theVec);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const int' or paramTypes[0] == 'int':
            lineList.append(paramTypes[0]+' tVal = 1;\n')
            lineList.append(returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
        elif paramTypes[0] == 'const double' or paramTypes[0] == 'double':
            lineList.append(paramTypes[0]+' tVal = 1;\n')
            lineList.append(returnType+' ans;\n\tans = '+modImport[1][modImport[1].find('.')+1:]+'tVal);\n\tsink(ans);\n}')
        '''


        '''
        returnType+' sink ('+returnType+' ans) {\n\treturn ans;\n', '}\n',
        'int main() {\n\n', '\t'+paramTypes[0]+' theVec = {1.0, 2.0, 3.0, 4.0};\n', '\t'+theType+' ans;\n', 
        '\tans = modify(theVec);\n', '\tsink(ans);\n','}'
        ]
        '''

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName

'''
def createCppRunFile(directory, modImport, isVulnerable):
    # accepts as argument the tuple (file, file.function)
    fileName = 'temp_run.cpp'
    #q = open(directory+modImport[0])

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n', 'namespace py = pybind11;\n\n',
                    'py::list taint (py::list pList) {\n', 
                    '\treturn pList;\n', '}\n', 'std::vector<std::vector<int>> sink (std::vector<std::vector<int>> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tstd::vector<int> theVec;\n', '\tstd::vector<std::vector<int>> ans;\n',
                    '\tfor (int i = 0; i < 9; i++)\n', '\t\ttheVec.push_back(i);\n\n', '\tpy::list pyList = py::cast(theVec);\n', 
                    '\tpyList = taint(pyList);\n', '\tans = multiply(pyList);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n', 'namespace py = pybind11;\n\n',
                    'std::vector<std::vector<int>> sink (std::vector<std::vector<int>> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tstd::vector<int> theVec;\n', '\tstd::vector<std::vector<int>> ans;\n',
                    '\tfor (int i = 0; i < 9; i++)\n', '\t\ttheVec.push_back(i);\n\n', '\tpy::list pyList = py::cast(theVec);\n', 
                    '\tans = multiply(pyList);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
# Pybind11 test file 1.
def createCppRunFile(directory, modImport, isVulnerable):
    # accepts as argument the tuple (file, file.function)
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n', 'namespace py = pybind11;\n\n',
                    'std::vector<double> taint (std::vector<double> vec) {\n', 
                    '\treturn vec;\n', '}\n', 'std::vector<double> sink (std::vector<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tconst std::vector<double> theVec = taint({1.0, 2.0, 3.0, 4.0});\n', '\tstd::vector<double> ans;\n',
                    '\tans = modify(theVec);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n', 'namespace py = pybind11;\n\n',
                    'std::vector<double> sink (std::vector<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tconst std::vector<double> theVec = {1.0, 2.0, 3.0, 4.0};\n', '\tstd::vector<double> ans;\n', 
                    '\tans = modify(theVec);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
# Pybind11 test file 2
def createCppRunFile(directory, modImport, isVulnerable):
    # accepts as argument the tuple (file, file.function)
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n', 'namespace py = pybind11;\n\n',
                    'std::vector<std::vector<double>> taint (std::vector<std::vector<double>> vec) {\n', 
                    '\treturn vec;\n', '}\n', 'std::vector<std::vector<double>> sink (std::vector<std::vector<double>> ans) {\n',
                    '\treturn ans;\n', '}\n','int main() {\n\n', '\tconst std::vector<std::vector<double>> theVec = taint({{1, 2, 3}, {4, 5}});\n', 
                    '\tstd::vector<std::vector<double>> ans;\n','\tans = modify(theVec);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n', 'namespace py = pybind11;\n\n',
                    'std::vector<std::vector<double>> sink (std::vector<std::vector<double>> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tconst std::vector<std::vector<double>> theVec = {{1, 2, 3}, {4, 5}};\n', '\tstd::vector<std::vector<double>> ans;\n',
                    '\tans = modify(theVec);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
# Pybind11 test file 3
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n' 'namespace py = pybind11;\n\n',
                    'std::vector<double> taint (std::vector<double> vec) {\n', 
                    '\treturn vec;\n', '}\n', 'std::vector<int> sink (std::vector<int> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'std::vector<int> ans;\n' '\tconst std::vector<double> theVec = taint({1.0, 2.0, 3.0, 5.0});\n', 
                    '\tans = multiply(theVec);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n' 'namespace py = pybind11;\n\n',
                    'std::vector<int> sink (std::vector<int> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'std::vector<int> ans;\n' '\tconst std::vector<double> theVec = {1.0, 2.0, 3.0, 5.0};\n', 
                    '\tans = multiply(theVec);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
# Pybind11 test file 4
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n' 'namespace py = pybind11;\n\n',
                    'std::vector<double> taint (std::vector<double> vec) {\n', 
                    '\treturn vec;\n', '}\n', 'std::vector<double> sink (std::vector<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'std::vector<double> ans;\n' '\tstd::vector<double> theVec = {1.0, 2.0, 3.0, 5.0};\n', 
                    '\ttheVec = taint(theVec);\n', '\tans = length(theVec);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <vector>\n' 'namespace py = pybind11;\n\n',
                    'std::vector<double> sink (std::vector<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'std::vector<double> ans;\n' '\tstd::vector<double> theVec = {1.0, 2.0, 3.0, 5.0};\n', 
                    '\tans = length(theVec);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
# Pybind11 test file 5
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <Eigen/LU>\n' 'namespace py = pybind11;\n\n',
                    'Eigen::MatrixXd taint (Eigen::MatrixXd mat) {\n', 
                    '\treturn vec;\n', '}\n', 'Eigen::MatrixXd sink (Eigen::MatrixXd ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'Eigen::MatrixXd ans;\n' '\tEigen::MatrixXd mat(3,3);\n', 
                    '\mat = taint(mat);\n', '\tans = '+modImport[1]+'('+'(mat)'+')\n','\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <Eigen/LU>\n' 'namespace py = pybind11;\n\n',
                    'std::vector<double> sink (std::vector<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'std::vector<double> ans;\n' '\tstd::vector<double> theVec = {1.0, 2.0, 3.0, 5.0};\n', 
                    '\tans = length(theVec);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
#Pybind11 test file 6
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <Eigen/LU>\n' 'namespace py = pybind11;\n\n',
                    'Eigen::MatrixXd taint (Eigen::MatrixXd mat) {\n', 
                    '\treturn vec;\n', '}\n', 'Eigen::MatrixXd sink (Eigen::MatrixXd ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'Eigen::MatrixXd ans;\n' '\tEigen::MatrixXd mat(3,3);\n', 
                    '\mat = taint(mat);\n', '\tans = '+modImport[1]+'('+'(mat)'+')\n','\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <Eigen/LU>\n' 'namespace py = pybind11;\n\n',
                    'std::vector<double> sink (std::vector<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'std::vector<double> ans;\n' '\tstd::vector<double> theVec = {1.0, 2.0, 3.0, 5.0};\n', 
                    '\tans = length(theVec);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
# Pybind11 test file 7
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', 'namespace py = pybind11;\n\n',
                    'int taint (int num) {\n', 
                    '\treturn num;\n', '}\n', 'int sink (int ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'int ans;\n' '\tint A = 1;\n', '\tint B = 2;\n', 
                    '\tA = taint(A);\n', '\tB = taint(B);\n', '\tans = mul(A, B);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', 'namespace py = pybind11;\n\n',
                    'int sink (int ans) {\n', '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tint ans;\n', '\tint A = 1;\n', '\tint B = 2;\n', 
                    '\tans = mul(A, B);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
#Pybind11 test file 8
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <Eigen/LU>\n' 'namespace py = pybind11;\n\n',
                    'Eigen::MatrixXd taint (Eigen::MatrixXd mat) {\n', 
                    '\treturn vec;\n', '}\n', 'Eigen::MatrixXd sink (Eigen::MatrixXd ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'Eigen::MatrixXd ans;\n' '\tEigen::MatrixXd mat(3,3);\n', 
                    '\mat = taint(mat);\n', '\tans = '+modImport[1]+'('+'(mat)'+')\n','\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include <Eigen/LU>\n' 'namespace py = pybind11;\n\n',
                    'Eigen::MatrixXd sink (Eigen::MatrixXd ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', 'Eigen::MatrixXd ans;\n' '\tEigen::MatrixXd mat(3,3);\n', 
                    '\tans = '+modImport[1]+'('+'(mat)'+')\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''

'''
#Pybind11 test 9
def createCppRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.cpp'

    f = open(directory+fileName, 'w')

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['#include \"'+modImport[0]+'\"\n', '#include \"matrix.h\"', 'namespace py = pybind11;\n\n',
                    'Matrix<double> taint (Matrix<double> mat) {\n', 
                    '\treturn mat;\n', '}\n', 'Matrix<double> sink (Matrix<double> ans) {\n',
                    '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tMatrix<double> A({1,3}, {1.0, 2.0, 3.0});\n' '\tMatrix<double> B({1,3}, {1.0, 2.0, 3.0});\n', '\tMatrix<double> ans;\n',
                    '\tA = taint(A);\n', '\tB = taint(B);\n', '\tans = '+modImport[1][+'A, B);\n', '\tsink(ans);\n','}'
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['#include \"'+modImport[0]+'\"\n', 'namespace py = pybind11;\n\n',
                    'int sink (int ans) {\n', '\treturn ans;\n', '}\n',
                    'int main() {\n\n', '\tint ans;\n', '\tint A = 1;\n', '\tint B = 2;\n', 
                    '\tans = mul(A, B);\n', '\tsink(ans);\n','}'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName
'''


def createPyRunFile(directory, modImport, isVulnerable):
    fileName = 'temp_run.py'

    f = open(directory+fileName, 'w')

    modName = modImport[0][:modImport[0].find('.')]

    if isVulnerable:
        # if the previous file was vulnerable, then a function called taint() is included to simulate the tainting of the 
        # arguments passed to the foreign function
        lineList = ['import '+modName+'\n\n', 
                    'matOne = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n', 'matTwo = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n\n',
                    'matOne, matTwo = taint(matOne, matTwo)\n\n', 'matThree = final.pythFunc(matOne, matTwo)\n',
                    'sink(matThree)\n', 'def sink(mat):\n', '\treturn mat\n\n','def taint(x, y):\n', '\treturn x, y\n\n',
                    ]
    else:
        # if the previous file was not vulnerable, then a taint() function is not included because that would inaccurately taint
        # the arguments of the foreign function call.
        lineList = ['import '+modName+'\n\n', 
                    'matOne = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n', 'matTwo = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]\n\n',
                    'matThree = final.pythFunc(matOne, matTwo)\n', 'sink(matThree)\n', 'def sink(mat):\n', '\treturn mat\n\n'
                    ]

    for line in lineList:
        f.write(line)

    f.close()
    return directory+fileName

def getDirectoryLists(start_directory):
    # returns lists of CPP files and Python files
    files = [f for f in listdir(start_directory) if isfile(join(start_directory, f)) and (".cpp" in f or ".py" in f)]
    cppFiles = [f for f in files if ".cpp" in f]
    pyFiles = [f for f in files if ".py" in f]

    return cppFiles, pyFiles

def newFindCalls(file, fileList):
    modNames = [i[:i.find('.')] for i in fileList]
    fileSinks = []

    with open(file.filename, 'r') as f:
        for line in f.readlines():
            for mod in modNames:
                if mod in line and 'import' not in line and '#' not in line and line[line.find(mod):line.find('(')+1] != '':
                    print(line)
                    fileSinks.append((mod+'.cpp', line[line.find(mod):line.find('(')+1]))
    
    return fileSinks

def findFileCalls(sourcesAndSinks, fileList):
    # This function searches sources and sinks for module names to find foreign function calls
    # returns (file, 'sink string') tuple list
    filesFound = []

    for ss in sourcesAndSinks:
        for file in fileList:
            modName = file[:file.find('.')]
            if modName in ss[0] and file not in filesFound:
                filesFound.append((file, ss[0]))
            if modName in ss[1] and file not in filesFound:
                filesFound.append((file, ss[1]))
    
    return filesFound

def pySSFinder(type, output):
    tempSourcesAndSinks = []
    tempList = []

    if type == "py":  
        for line in output:
            if "User input" in line:
                sourceName = line[line.find("\"")+1:len(line)-2]
                tempList.append(sourceName)

            if "reaches" in line:
                sinkName = line[line.find("\"")+1:len(line)-2]
                tempList.append(sinkName)

                tempSourcesAndSinks.append((tempList[0], tempList[1]))
                tempList.clear()
    else:
        for i in output:
            if "Other" in i:
                sourceName = i[8:i.find(')')-1]
                sinkName = i[i.find('Other', 15, len(i)-1)+6:i.rfind(')')-2]

                tempSourcesAndSinks.append((sourceName, sinkName))
    
    return tempSourcesAndSinks

def pyParse(file, cppFiles, output):
    hasFFCall = False
    isVulnerable = False
    tempList = []

    if "No vulnerabilities found" in output:        
    # if there are no vulnerabilities, the file targeted for analysis
    # is opened and checked for 

        if file.analyzed is False:
            file.analyzed = True
            with open(file.filename) as f:
                for num, line in enumerate(f, 1):
                    for cppFile in cppFiles:
                        modName = cppFile[:cppFile.find('.')]
                        if modName+"." in line and "#" not in line:
                            start = line.find(modName)+len(modName)+1

                            func = line[start:]
                            func = func[:func.find('(')]

                            # append file name and function name
                            tempList.append((cppFile, func))
            for combo in tempList:
                if combo not in file.fileSinks:
                    file.fileSinks.append(combo)
                    hasFFCall = True

    
    else:
        isVulnerable = True
        output = output.split('\\n') 

        tempSourcesAndSinks = pySSFinder(file.type, output)
        adder = []

        for combo in tempSourcesAndSinks:
            if combo not in adder:
                adder.append(combo)
        
        file.sourcesAndSinks.append(adder)

        #modNames = findFileCalls(file.sourcesAndSinks, cppFiles)
        if file.analyzed is False:
            file.fileSinks = newFindCalls(file, cppFiles)
        
        file.analyzed = True
        if len(file.fileSinks) > 0:
            hasFFCall = True
        else:
            hasFFCall = False
                   
    return hasFFCall, isVulnerable

def cppParse(file, pyFiles, output):
    modFiles = []
    isVulnerable = False
    hasFFCall = False
    tempList = []
    sourcesAndSinks = []                

    # In this part, we need to 
    if "No issues found" in output:

        if file.analyzed is False:
            file.analyzed = True
            with open(file.filename) as f:
                for num, line in enumerate(f, 1):
                    if "PyImport_ImportModule" in line:
                        quotes = line.find('\"')+1
                        importedMod = line[quotes:line.find(')')-1]
                    
                        for pyFile in pyFiles:
                            modName = pyFile[:pyFile.find('.')]

                            if importedMod == modName:
                                modFiles.append(pyFile)
                                fileSink = pyFile
                    if "PyObject_GetAttrString" in line:
                        quotes = line.find('\"')+1
                        functionUsed = line[quotes:line.find(')')-1]
                        tempList.append((fileSink, ("PyObject_CallObject", functionUsed)))
            for combo in tempList:
                if combo not in file.fileSinks:
                    file.fileSinks.append(combo)
                    hasFFCall = True


    if "Taint Error" in output:
        isVulnerable = True
        op = output.split('Taint Error')
        output = output.split('\\n')
    
        for i in op:
            if 'b\'' not in i:
                j = i.split('Other(')
                SS = []
                for q in j:
                    if q != '\\n  ':
                        SS.append(q[:q.find('(')])
                if len(SS) == 2:
                    sourcesAndSinks.append((SS[0], SS[1]))
        
        file.sourcesAndSinks.append(sourcesAndSinks)
        
        if file.analyzed is False:
            with open(file.filename) as f:
                for num, line in enumerate(f, 1):
                    if "PyImport_ImportModule" in line:
                        # grab the name of the module that is imported
                        quotes = line.find('\"')+1
                        importedMod = line[quotes:line.find(')')-1]
                    
                        for pyFile in pyFiles:
                            modName = pyFile[:pyFile.find('.')]

                            if importedMod == modName:
                                modFiles.append(pyFile)
                                fileSink = pyFile
                    if "PyObject_GetAttrString" in line:
                        # grab the name of the function that is imported
                        quotes = line.find('\"')+1
                        functionUsed = line[quotes:line.find(')')-1]
                        tempList.append((fileSink, ("PyObject_CallObject", functionUsed)))
            for combo in tempList:
                if combo not in file.fileSinks:
                    file.fileSinks.append(combo)
                    hasFFCall = True
        
        file.analyzed = True

    return hasFFCall, isVulnerable

def getOutput(file):
    # returns a string of the output from running Quandary or PyT
    if file.type == "py":
        cmd = ["python3", "-m", "pyt", "-t", "my_trigger_words.pyt", file.runFile]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        
        return str(result.stdout)
    
    if file.type == "cpp":
        # include code here that differentiates between Boost and Pybind11
        cmd = "infer-run --quandary-only -- g++ -Wall -shared -framework Python -std=c++14 -undefined dynamic_lookup `python3 -m pybind11 --includes` "+file.runFile
        #cmd = "infer-run --quandary-only -- g++ -lm -pthread -O3 -std=c++14 -march=native -Wall -funroll-loops -Wno-unused-result -shared -Wl,-export_dynamic -L/usr/local/Cellar/boost-python3/1.75.0/lib -lboost_python39 -L/usr/local/Cellar/python@3.9/3.9.2/Frameworks/Python.framework/Versions/3.9/lib/ -lpython3.9 "+file.runFile
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

        return str(result.stdout)


    return "Not a relevant file"

def parseOutput(output, file, cppFiles, pyFiles):
    
    if file.type == "py":
        return pyParse(file, cppFiles, output)
    if file.type == "cpp":
        return cppParse(file, pyFiles, output)

def getCallList(file, cppFiles, pyFiles):
    output = getOutput(file)
    
    return parseOutput(output, file, cppFiles, pyFiles)