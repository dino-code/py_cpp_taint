class Program:
    
    def __init__(self, filename):
        self.filename = filename
        self.type = filename[filename.find('.')+1:len(filename)]
        self.sourcesAndSinks = []
        self.fileSinks = []
        self.exploredSink = ('example', 'example')
        self.runFile = ''   # the file that PyT or Quandary will analyze
        self.analyzed = False
        self.passesForward = False
        self.passesBackward = False
        self.taintPassedTo = "No taint passed" # if true, a tainted variable has been passed to this program
        self.taintPassedFrom = "Received no taint"
