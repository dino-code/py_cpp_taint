from os import listdir
from os.path import isfile, join
import Program

class MultilingualTaintAnalyzer:
    stack = []
    exploredFiles = []
    path = []

    def multilingualAnalyze(self, start_directory, start_file):
        pass
    
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