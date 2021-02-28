import sys
from os import listdir
from os.path import isfile, join
import os
from program import Program
import subprocess
import helpers as h
import time
import PySimpleGUI as sg
'''
while True:
    layout = [  [sg.Text("Name your start directory")],     # Part 2 - The Layout
            [sg.Input()],
            [sg.Text("Name your start file")],
            [sg.Input()],
            [sg.Button('Begin'), sg.Button('Quit')] ]

    window = sg.Window('Py_CPP_Taint Program Parameters', layout, size=(500,400))      # Part 3 - Window Defintion

    # Display and interact with the Window
    event, values = window.read()                   # Part 4 - Event loop or Window.read call

    if event == sg.WINDOW_CLOSED or event == 'Quit':
        break

    window.close()

    sg.set_options(debug_win_size=(150,50))
    sg.easy_print(do_not_reroute_stdout=False)
'''
    
    # Get start directory and start file
start_directory = sys.argv[1]+'/'   # "deepMultilingualMatrixMultiplier"
start_file = sys.argv[2]        # "main.py"

'''
start_directory = values[0]+'/'
start_file = values[1]
'''

stack = []
exploredFiles = []
path = [] # track the path of the analysis through sources and sinks

cppFiles, pyFiles = h.getDirectoryLists(start_directory)

start_prog = Program(start_directory+start_file)
start_prog.runFile = start_directory+start_file    # tempFile is the file that Quandary/PyT will be run on

stack.append(start_prog)
exploredFiles.append(start_directory+start_file)

print(cppFiles)

iter = 0
while len(stack)>0:
    file = stack[-1]
    path.append(file.filename)
    print()
    iter+=1

    hasFFCall, isVulnerable = h.getCallList(file, cppFiles, pyFiles) # call list is the list of other files called from this program

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
                #file.passesForward = True
                #file.taintPassedTo = mod[0]
            tempCppFile.taintPassedFrom = file.filename
            file.exploredSink = mod

            tempCppFile.runFile = h.createCppRunFile(start_directory, mod, file.passesForward) # send function call as argument because contains mod name
            stack.append(tempCppFile)
            exploredFiles.append(start_directory+mod[0])
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
            stack.append(tempPyFile)
            exploredFiles.append(start_directory+mod[0]) 

        file.fileSinks.pop(0)
            
        print('TAINT CARRIED FORWARD:', file.passesForward)
    else:
        prevFile = stack[len(stack)-2]

        if len(stack) > 1 and isVulnerable == True and prevFile.type == 'py':
            h.modifyPyTrigger(prevFile.exploredSink[1])
        if len(stack) > 1 and isVulnerable == True and prevFile.type == 'cpp':
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

        if len(stack) == 1:
            print("END OF ANALYSIS")
        stack.pop(-1)
    print('*'*100)

print()
print()
print("PROGRAM PATH")
for i in path:
    print(i)
print()
print()