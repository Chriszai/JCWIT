import sys
import subprocess
import networkx as nx
import numpy as np
import validation as validation


def GetType(argv):
    print('No violation founded')
    if (len(sys.argv) == 3):
        variableType = argv[2].lower()
    else:
        with open(sys.argv[1], "rt") as fin:
            for line in fin:
                index = line.find('verifier.')
                if(index != -1):
                    subStringIndex = line.find('(')
                    variableType = line[index + 15:subStringIndex].lower()
                    print(variableType)
    return variableType


def CollatingData(file):
    edgeDict = {}
    num = 0
    for node in file.nodes(data=True):
        if(node[1].get('isEntryNode') == True):
            entryNode = node[0]

    for data in file.edges(data=True):
        if(edgeDict.get(data[0]) == None):
            edgeDict.update({data[0]: data[1]})
        else:
            str = edgeDict.get(data[0]) + ',' + data[1]
            edgeDict.update({data[0]: str})
        num = num + 1
    return CheckIntegrity(entryNode, edgeDict, num, 0)


def CheckIntegrity(node, edgeDict, num, cur):
    # Check the integrity of this witness file
    if node in edgeDict:
        val = edgeDict.get(node)
    else:
        if(cur == num):
            return True
        return False

    if(val == 'sink'):
        if(num == cur + 1):
            return True
        return False
    nodes = val.split(',')
    for node in nodes:
        ans = CheckIntegrity(node, edgeDict, num, cur + len(nodes))
        if(ans == False):
            return False
    return True


def CreateEdgeDict(file):
    edgeDict = {}
    arr = []
    for node in file.nodes(data=True):
        if(node[1].get('isEntryNode') == True):
            entryNode = node[0]

    for data in file.edges(data=True):
        if(edgeDict.get(data[0]) == None):
            edgeDict.update({data[0]: data[1]})
        else:
            str = edgeDict.get(data[0]) + ',' + data[1]
            edgeDict.update({data[0]: str})

    return InspectionRing(entryNode, edgeDict, arr)


def InspectionRing(node, edgeDict, arr):
    if node in edgeDict:
        arr.append(node)
        val = edgeDict.get(node)
        values = val.split(',')
        for val in values:
            if val in arr:
                return False
            ans = InspectionRing(val, edgeDict, arr)
            if ans == False:
                return False
    return True


classnameArray = sys.argv[1].split('.')
classname = classnameArray[0]
if len(classnameArray) == 2 and classnameArray[1] == 'java':
    subprocess.Popen(['javac', sys.argv[1]]).wait()

variableType =''
if(classnameArray[1] == 'class'):
    variableType = sys.argv[2].lower()

cmd = 'jbmc ' + classname + ' --stop-on-fail --graphml-witness witness'
try:
    result = subprocess.check_output(cmd, shell=True)
except subprocess.CalledProcessError as e:
    result = e.output

witnessFile = nx.read_graphml("witness")
violation = False
for violationKey in witnessFile.nodes(data=True):
    if 'isViolationNode' in violationKey[1]:  
        violation = True

if(violation == False):
    # It is used for get the type of the invariant
    # variableType = GetType(sys.argv)
    # It is used for collate the data
    print('No violation founded')
    isIntegrity = CollatingData(witnessFile)
    if(isIntegrity == True):
        print('This correctness witness is complete.')
    hasRing = CreateEdgeDict(witnessFile)
    if(hasRing == True):
        print('This correctness witness does not have a ring.')
    # It is used for get the type of the invariant
    if not variableType:
        variableType = validation.GetType(sys.argv)
    Invariant = validation.GetInvariant(witnessFile, sys.argv)
    print(Invariant)
    seed = validation.GetSeed(Invariant,variableType)
    if len(variableType) == 0:
        exit(1)
    validation.HarnessRunning(
        variableType, seed, len(variableType), sys.argv[1])

    print('Completed validation, consistent with JBMC result, the reault is true')


else:
    print('Violation founded')
    exit(1)
