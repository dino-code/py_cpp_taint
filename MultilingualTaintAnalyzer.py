from os import listdir
from os.path import isfile, join
import Program

class MultilingualTaintAnalyzer:
    stack = []
    exploredFiles = []
    path = []

    def multilingualAnalyze(self, start_directory, start_filename):
        cppFiles, pyFiles = getDirectoryFiles(start_directory)

        start_prog = Program.Program(start_directory+start_filename)
        start_prog.runFilename = start_directory+start_filename    # tempFile is the file that Quandary/PyT will be run on

        self.stack.append(start_prog)
        self.exploredFiles.append(start_directory+start_filename)

        print(cppFiles)

        iter = 0
        while len(self.stack)>0:
            file = self.stack[-1]
            self.path.append(file.filename)
            print()
            iter+=1

            hasFFCall, isVulnerable = getCallList(file, cppFiles, pyFiles) # call list is the list of other files called from this program

            print(str(iter)+')', "Current File:", file.filename)
            print("Has a foreign function call:", hasFFCall)
            print("Is vulnerable:", isVulnerable)
            print()
            print("Sources and Sinks:", file.sourcesAndSinks)
            print("File sinks:", file.fileSinks)
            print()

            if hasFFCall:
                # if the file has a foreign function call, then the program can delve deeper.
                mod = file.fileSinks[0]

                # each mod is a foreign module. If a file has one foreign function call, then len(file.fileSinks) == 1
                # mod[0] is the foreign file name, while mod[1] is the function called from the foreign file
                # if the file has not yet been explored, execute this code
                if mod[0][len(mod[0])-3:] == "cpp":
                    # if the file sink is a cpp file
                    tempCppFile = Program(start_directory+mod[0])
                    
                    if isVulnerable:
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

                    tempCppFile.runFile = h.createCppRunFile(start_directory, mod, file.passesForward) # send function call as argument because contains mod name
                    self.stack.append(tempCppFile)
                    self.exploredFiles.append(start_directory+mod[0])
                else:
                    # if the file sink is a python file
                    tempPyFile = Program(start_directory+mod[0])
                    if isVulnerable and start_directory+mod[0]:
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

                    tempPyFile.runFile = h.createPyRunFile(start_directory, mod, file.passesForward)
                    self.stack.append(tempPyFile)
                    self.exploredFiles.append(start_directory+mod[0]) 

                file.fileSinks.pop(0)
                    
                print('TAINT CARRIED FORWARD:', file.passesForward)
            else:
                prevFile = self.stack[len(self.stack)-2]

                if len(self.stack) > 1 and isVulnerable == True and prevFile.type == 'py':
                    h.modifyPyTrigger(prevFile.exploredSink[1])
                if len(self.stack) > 1 and isVulnerable == True and prevFile.type == 'cpp':
                    h.modifyCppConfig(prevFile.exploredSink[1][0])

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
    
    def monolingualAnalyze(self, file):

        output = Program.getMonolingualOutput(file)

        output = output.split('\\n')
        
        for i in output:
            print(i)


def getDirectoryFiles(directory):
    # returns lists of CPP files and Python files
    files = [f for f in listdir(directory) if isfile(join(directory, f)) and (".cpp" in f or ".py" in f)]
    cppFiles = [f for f in files if ".cpp" in f]
    pyFiles = [f for f in files if ".py" in f]

    return cppFiles, pyFiles


analyzer = MultilingualTaintAnalyzer()

file = Program.Program('TestPrograms/01_py-list_cpp-vector/test.py', 'TestPrograms/01_py-list_cpp-vector/test.py')

analyzer.monolingualAnalyze(file)