import directoryManager
import program

class MultilingualTaintAnalyzer:
    stack = []
    exploredFiles = []
    path = []

    def analyze(self, start_directory, start_filename):
        # This analyze function takes a start_directory and start_filename and traces taint through a program.
        
        # DirectoryManager keeps track of important information necessary for this function
        # it also contains necessary functions to aid in this algorithm's completion.
        dirManager = directoryManager.DirectoryManager(start_directory)
        dirManager.getDirectoryFiles()

        if start_filename in dirManager.pyFiles:
            start_prog = program.pyProgram(start_directory+start_filename, start_directory+start_filename)
        elif start_filename in dirManager.cppFiles:
            start_prog = program.cppProgram(dirManager.rootDirectory+start_filename, dirManager.rootDirectory+start_filename)

        self.stack.append(start_prog)
        self.exploredFiles.append(start_directory+start_filename)

        iter = 0
        while len(self.stack)>0:
            file = self.stack[-1]
            self.path.append(file.filename)
            print()
            iter+=1

            print(str(iter)+')', "Current File:", file.filename)
            print("Has a foreign function call:", file.hasFFCall)
            print("Is vulnerable:", file.isVulnerable)
            print()
            print("Sources and Sinks:", file.sourcesAndSinks)
            print("File sinks:", file.fileSinks)
            print()

            if file.type == 'py':
                file.analyze(dirManager.cppFiles)
            if file.type == 'cpp':
                file.analyze(dirManager.pyFiles)

            if file.hasFFCall:
                # if the file has a foreign function call, then the program can delve deeper.
                mod = file.fileSinks[0]     # grab the next file after the current file.

                # each mod is a foreign module. If a file has one foreign function call, then len(file.fileSinks) == 1
                # mod[0] is the foreign file name, while mod[1] is the function called from the foreign file
                # if the file has not yet been explored, execute this code
                if mod[0][len(mod[0])-3:] == "cpp":
                    # if the file sink is a cpp file
                    tempCppFile = program.cppProgram(start_directory+mod[0])
                    
                    if file.isVulnerable:
                        for i in file.sourcesAndSinks[-1]:
                            if file.type == 'py':
                                if mod[1] == i[1]:
                                    file.passesForward = True
                                    file.taintPassedTo = mod[0]
                                    break
                                else:
                                    file.passesForward = False
                                    file.taintPassedTo = ""
                        
                    tempCppFile.taintPassedFrom = file.filename
                    file.exploredSink = mod

                    tempCppFile.runFilename = dirManager.createCppRunFile(mod, file.passesForward) # send function call as argument because contains mod name
                    self.stack.append(tempCppFile)
                    self.exploredFiles.append(start_directory+mod[0])
                else:
                    # if the file sink is a python file
                    tempPyFile = program.Program(start_directory+mod[0])
                    if file.isVulnerable and start_directory+mod[0]:
                        for i in file.sourcesAndSinks[-1]:
                            print('mod'+str(mod[1]))
                            print('i '+str(i[1]))
                            if mod[1][0] == i[1]:
                                file.passesForward = True
                                file.taintPassedTo = mod[0]
                    else:
                        file.passesForward = False
                        file.taintPassedTo = ""

                    tempPyFile.taintPassedFrom = file.filename
                    file.exploredSink = mod

                    tempPyFile.runFilename = dirManager.createPyRunFile(start_directory, mod, file.passesForward)
                    self.stack.append(tempPyFile)
                    self.exploredFiles.append(start_directory+mod[0]) 

                file.fileSinks.pop(0)
                    
                print('TAINT CARRIED FORWARD:', file.passesForward)
            else:
                prevFile = self.stack[len(self.stack)-2]

                if len(self.stack) > 1 and file.isVulnerable == True and prevFile.type == 'py':
                    dirManager.modifyPyTrigger(prevFile.exploredSink[1])
                if len(self.stack) > 1 and file.isVulnerable == True and prevFile.type == 'cpp':
                    dirManager.modifyCppConfig(prevFile.exploredSink[1][0])

                if len(file.sourcesAndSinks) == 1:
                    if (file.sourcesAndSinks[-1][0][1] == 'sink(') or file.sourcesAndSinks[-1][0][1] == 'sink':
                        file.passesBackward = True
                
                elif len(file.sourcesAndSinks) > 1:
                    count = 0
                    for i in file.sourcesAndSinks[-1]:
                        if (i[0] == 'taint(' or i[0] == 'taint') and (i[1] == 'sink(' or i[1] == 'sink'):
                            count += 1
                        for j in file.sourcesAndSinks[-1]:
                            if (j[1] == 'sink(' or j[1] == 'sink') and (i[1] == j[0]):
                                file.passesBackward = True
                    if count == len(file.sourcesAndSinks[-1]) and len(file.sourcesAndSinks[-1]) > 0:
                        file.passesBackward = True
                
                print('TAINT CARRIED BACKWARD:', file.passesBackward)

                if len(self.stack) == 1:
                    print("END OF ANALYSIS")
                self.stack.pop(-1)
            print('*'*100)

        print()
        print()
        print("PROGRAM PATH")
        for i in self.path:
            print(i)
        print()
        print()

#analyzer = MultilingualTaintAnalyzer()

'''
file = program.pyProgram('TestPrograms/pybind11-examples/03-Constructors/ctor.py', 'TestPrograms/pybind11-examples/03-Constructors/ctor.py')

print("Starting Up\n\n")

file.getMonolingualOutput()
'''

'''

file2 = program.cppProgram('TestPrograms/pybind11-examples/02-ExposingClasses/temp_run.cpp', 'TestPrograms/pybind11-examples/02-ExposingClasses/temp_run.cpp')

file2.getMonolingualOutput()
'''


# TestPrograms/cmake_cpp_pybind11_tutorial/

#file = program.pyProgram('TestPrograms/cmake_cpp_pybind11_tutorial/test.py', 'TestPrograms/cmake_cpp_pybind11_tutorial/test.py')

#file.getMonolingualOutput()

file2 = program.cppProgram('TestPrograms/cmake_cpp_pybind11_tutorial/temp_run.cpp', 'TestPrograms/cmake_cpp_pybind11_tutorial/temp_run.cpp')

file2.getMonolingualOutput()

#analyzer.analyze('/Users/dinobecaj/Documents/ComputerScienceMS/LyonsWork/python_cpp_static_analysis/py_cpp_taint/TestPrograms/pybind11-examples/02-ExposingClasses/', 'classes.py')
