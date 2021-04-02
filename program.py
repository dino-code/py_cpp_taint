import subprocess

class Program:
    
    def __init__(self, filename='', runFilename=''):
        self.filename = filename
        self.runFilename =  runFilename  # the file that PyT or Quandary will analyze
        #self.type = filename[filename.find('.')+1:len(filename)]
        self.sourcesAndSinks = []
        self.fileSinks = []
        self.exploredSink = ('example', 'example')
        
        self.analyzed = False
        self.passesForward = False
        self.passesBackward = False
        self.taintPassedTo = "No taint passed" # if true, a tainted variable has been passed to this program
        self.taintPassedFrom = "Received no taint"
        
        self.hasFFCall = False
        self.isVulnerable = False
        #self.files = []      

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
    
    def newFindCalls(self, fileList):
        modNames = [i[:i.find('.')] for i in fileList]
        self.fileSinks = []

        with open(self.filename, 'r') as f:
            for line in f.readlines():
                for mod in modNames:
                    if mod in line and 'import' not in line and '#' not in line and line[line.find(mod):line.find('(')+1] != '':
                        print(line)
                        self.fileSinks.append((mod+'.cpp', line[line.find(mod):line.find('(')+1]))   

class cppProgram(Program):
    
    def __init__(self, filename=None, runFilename=None):
        self.type = 'cpp'

        if filename == None:
            filename = ''
        if runFilename == None:
            runFilename = ''
        super().__init__(filename, runFilename)

    def analyze(self, pyFiles):
        # this function analyzes the program and sets hasFFCall and isVulnerable appropriately
        output = self.getMonolingualOutput()

        if output != "Not a relevant file":
            self.parseOutput(pyFiles, output)
    
    def getMonolingualOutput(self):
        if self.type == "cpp":
            # include code here that differentiates between Boost and Pybind11
            cmd = "infer-run --quandary-only -- g++ -Wall -shared -framework Python -std=c++14 -undefined dynamic_lookup `python3 -m pybind11 --includes` "+self.runFile
            #cmd = "infer-run --quandary-only -- g++ -lm -pthread -O3 -std=c++14 -march=native -Wall -funroll-loops -Wno-unused-result -shared -Wl,-export_dynamic -L/usr/local/Cellar/boost-python3/1.75.0/lib -lboost_python39 -L/usr/local/Cellar/python@3.9/3.9.2/Frameworks/Python.framework/Versions/3.9/lib/ -lpython3.9 "+file.runFile
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

            return str(result.stdout)

        return "Not a relevant file"

    def parseOutput(self, pyFiles, output):
        modFiles = []
        self.isVulnerable = False
        self.hasFFCall = False
        tempList = []
        sourcesAndSinks = []  
        
        for i in output.split('\\n'):
            print(i)              

        # In this part, we need to 
        if "No issues found" in output:

            if self.analyzed is False:
                self.analyzed = True
                with open(self.filename) as f:
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
                    if combo not in self.fileSinks:
                        self.fileSinks.append(combo)
                        self.hasFFCall = True


        if "Taint Error" in output:
            self.isVulnerable = True
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
            
            self.sourcesAndSinks.append(sourcesAndSinks)
            
            if self.analyzed is False:
                with open(self.filename) as f:
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
                    if combo not in self.fileSinks:
                        self.fileSinks.append(combo)
                        self.hasFFCall = True
            
            self.analyzed = True

class pyProgram(Program):

    def __init__(self, filename, runFilename):
        self.type = 'py'

        if filename == None:
            filename = ''
        if runFilename == None:
            runFilename = ''
        super().__init__(filename, runFilename)

    def analyze(self, cppFiles):
        # this function analyzes the program and sets hasFFCall and isVulnerable appropriately
        output = self.getMonolingualOutput()

        if output != "Not a relevant file":
            self.parseOutput(cppFiles, output)
    
    def parseOutput(self, cppFiles, output):
        self.hasFFCall = False
        self.isVulnerable = False
        tempList = []

        if "No vulnerabilities found" in output:        
        # if there are no vulnerabilities, the file targeted for analysis
        # is opened and checked for 

            if self.analyzed is False:
                self.analyzed = True
                with open(self.filename) as f:
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
                    if combo not in self.fileSinks:
                        self.fileSinks.append(combo)
                        self.hasFFCall = True
        
        else:
            self.isVulnerable = True
            output = output.split('\\n') 

            tempSourcesAndSinks = self.SSFinder(output)
            adder = []

            for combo in tempSourcesAndSinks:
                if combo not in adder:
                    adder.append(combo)
            
            self.sourcesAndSinks.append(adder)

            #modNames = findFileCalls(file.sourcesAndSinks, cppFiles)
            if self.analyzed is False:
                self.fileSinks = self.newFindCalls(cppFiles)
            
            self.analyzed = True
            if len(self.fileSinks) > 0:
                self.hasFFCall = True
            else:
                self.hasFFCall = False
    
    def newFindCalls(self, fileList):
        modNames = [i[:i.find('.')] for i in fileList]
        fileSinks = []

        with open(self.filename, 'r') as f:
            for line in f.readlines():
                for mod in modNames:
                    if mod in line and 'import' not in line and '#' not in line and line[line.find(mod):line.find('(')+1] != '':
                        print(line)
                        fileSinks.append((mod+'.cpp', line[line.find(mod):line.find('(')+1]))
        
        return fileSinks

    def SSFinder(self, output):
        tempSourcesAndSinks = []
        tempList = []

        if self.type == "py":  
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
    
    def getMonolingualOutput(self):

        if self.type == "py":
            cmd = ["python3", "-m", "pyt", "-t", "my_trigger_words.pyt", self.runFilename]
            result = subprocess.run(cmd, stdout=subprocess.PIPE)

            return str(result.stdout)
        
        return "Not a relevant file"
