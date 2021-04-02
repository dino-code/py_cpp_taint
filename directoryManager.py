from os import listdir
from os.path import isfile, join
import json

class DirectoryManager:
    # This class is responsible for:
    # - keeping track of the root directory
    # - creating cppRunfile and pyRunfile
    # - keeping track of py and cpp files
    # - knowing and modifying pyTrigger and .inferconfig files
    def __init__(self, rootDirectory=''):
        self.rootDirectory = rootDirectory

    def getDirectoryFiles(self):
        # returns lists of CPP files and Python files
        files = [f for f in listdir(self.rootDirectory) if isfile(join(self.rootDirectory, f)) and (".cpp" in f or ".py" in f)]
        self.cppFiles = [f for f in files if ".cpp" in f]
        self.pyFiles = [f for f in files if ".py" in f]

    def createCppRunFile(self, modImport, taintCarried):
        # I need to open modImport[0] and find the function definition of modImport[1]

        returnType, paramTypes = getCppTypes(self.rootDirectory, modImport)
            
        fileName = 'temp_run.cpp'

        f = open(self.rootDirectory+fileName, 'w')

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
                elif paramTypes[i] == 'py::array_t<double>' or paramTypes[i] == 'const py::array_t<double>':
                    lineList.append('\t'+paramTypes[i]+' arr'+str(count)+'(0, nullptr);\n')
                    count+=1
                    lineList.append('\t'+paramTypes[i]+' arr'+str(count)+' = taint(arr'+str(count-1)+');\n')
                    varsWritten.append('arr'+str(count))
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
                elif paramTypes[i] == 'uint64_t' or paramTypes[i] == 'const uint64_t':
                    lineList.append('\t'+paramTypes[i]+' val'+str(count)+' = 1;\n')
                    count+=1
                    lineList.append('\t'+paramTypes[i]+' val'+str(count)+' = taint(val'+str(count-1)+');\n')
                    varsWritten.append('val'+str(count))
                    count+=1
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
                elif paramTypes[i] == 'py::array_t<double>' or paramTypes[i] == 'const py::array_t<double>':
                    lineList.append('\t'+paramTypes[i]+' arr'+str(count)+'(0, nullptr);\n')
                    varsWritten.append('arr'+str(count))
                    count+=1
                elif paramTypes[i] == 'uint64_t' or paramTypes[i] == 'const uint64_t':
                    lineList.append('\t'+paramTypes[i]+' val'+str(count)+' = 1;\n')
                    varsWritten.append('val'+str(count))
                    count+=1
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
            
        for line in lineList:
            f.write(line)

        f.close()
        return self.rootDirectory+fileName

    def modifyPyTrigger(self, function):
        # adds the specified function as a source in the PyT trigger file
        # Standard trigger file included in directory is assumed to be the one used
        trigger = "my_trigger_words.pyt"
        with open(trigger) as f:
            data = json.load(f)
            if function not in data["sources"]:
                data["sources"].append(function)

        with open(trigger, 'w') as t:
            json.dump(data, t, indent='\t')

    def modifyCppConfig(self, function):
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
            # checks to make sure the string search is not tripped up by includes or in similarly named functions

            if func[-1] == '(':
                dist = len(func)-1
            else:
                dist = len(func)
            if func in line and '#' not in line and line[line.find(func)+dist] == '(':
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