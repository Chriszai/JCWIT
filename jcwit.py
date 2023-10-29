import sys
import subprocess
import networkx as nx
import validation as validation
import os

# How to call this script on Linux:
# ./jcwit.py --witness [witness_file] [list of folders/JavaFiles]
# or
# ./jcwit.py --version


def CollatingData(file):
    # Collating data from witnesses
    edgeDict = {}
    num = 0
    for node in file.nodes(data=True):
        if node[1].get("isEntryNode") == True:
            entryNode = node[0]

    for data in file.edges(data=True):
        if edgeDict.get(data[0]) == None:
            edgeDict.update({data[0]: data[1]})
        else:
            str = edgeDict.get(data[0]) + "," + data[1]
            edgeDict.update({data[0]: str})
        num = num + 1
    return CheckIntegrity(entryNode, edgeDict, num, 0)


def CheckIntegrity(node, edgeDict, num, cur):
    # Check the integrity of this witness file
    if node in edgeDict:
        val = edgeDict.get(node)
    else:
        if cur == num:
            return True
        return False

    if val == "sink":
        if num == cur + 1:
            return True
        return False
    nodes = val.split(",")
    for node in nodes:
        ans = CheckIntegrity(node, edgeDict, num, cur + len(nodes))
        if ans == False:
            return False
    return True


def CreateEdgeDict(file):
    edgeDict = {}
    arr = []
    for node in file.nodes(data=True):
        if node[1].get("isEntryNode") == True:
            entryNode = node[0]

    for data in file.edges(data=True):
        if edgeDict.get(data[0]) == None:
            edgeDict.update({data[0]: data[1]})
        else:
            str = edgeDict.get(data[0]) + "," + data[1]
            edgeDict.update({data[0]: str})

    return InspectionRing(entryNode, edgeDict, arr)


def InspectionRing(node, edgeDict, arr):
    # Checking for the presence of ring
    if node in edgeDict:
        arr.append(node)
        val = edgeDict.get(node)
        values = val.split(",")
        for val in values:
            if val in arr:
                return False
            ans = InspectionRing(val, edgeDict, arr)
            if ans == False:
                return False
    return True


def DeleteFiles():
    # File path
    path = "./MockStatement.txt"
    if os.path.exists(path):
        os.remove(path)

    path = "./ValidationHarness.txt"
    if os.path.exists(path):
        os.remove(path)


try:
    if sys.argv[1].lower() == "--version" or sys.argv[1].lower() == "-v":
        if len(sys.argv) <= 2:
            print("Version: 1.0")
            exit(0)
        else:
            print("Usage: ./jcwit.py --witness [witness_file] [list of folders]")
        exit(0)

    print("Version: 1.0")

    benchmarks_dir = []
    for i in sys.argv[3:]:
        if ".java" in i:
            benchmarks_dir.append(i)

        else:
            for path, subdirs, files in os.walk(i):
                for name in files:
                    if fnmatch(name, "*.java"):
                        benchmarks_dir.append(os.path.join(path, name))
    print("benchmark: ", benchmarks_dir)

    witnessFile = nx.read_graphml(sys.argv[2])
    violation = False
    for violationKey in witnessFile.nodes(data=True):
        if "isViolationNode" in violationKey[1]:
            violation = True
except Exception as e:
    print("Witness result: Unknown")

if violation == False:
    # It is used for collate the data
    print("Witness result: True")
    isIntegrity = CollatingData(witnessFile)
    if isIntegrity == True:
        print("This correctness witness is complete.")
    else:
        print("This correctness witness is not complete.")
        print("Witness validation: False")
        exit(0)

    hasRing = CreateEdgeDict(witnessFile)
    if hasRing == True:
        print("This correctness witness does not have a ring.")
    else:
        print("This correctness witness does have a ring.")
        print("Witness validation: False")
        exit(0)

    types = []
    Invariants = []

    # It is used for get the type and row number of all the invariants
    try:
        for javaFile in benchmarks_dir:
            dict_line_type, variableType = validation.GetType(javaFile)
            types = types + variableType
            Invariant = validation.GetInvariant(witnessFile, javaFile, dict_line_type)
            Invariants = Invariants + Invariant

        seed = validation.GetSeed(Invariants, types)
        if len(types) == 0:
            print("Witness validation: Unknown")
            exit(0)
        # Creating harness that used for running
        validation.HarnessRunning(types, seed, len(types), sys.argv[3])
    except Exception as e:
        print(e)
        print("Witness validation: Unknown")
        exit(0)

    # Check the operating system of this machine
    pathWin = ".;./dependencies/byte-buddy-1.14.1.jar;./dependencies/byte-buddy-agent-1.14.1.jar;./dependencies/mockito-core-5.2.0.jar;./dependencies/objenesis-3.3.jar"
    pathLin = ".:./dependencies/byte-buddy-1.14.1.jar:./dependencies/byte-buddy-agent-1.14.1.jar:./dependencies/mockito-core-5.2.0.jar:./dependencies/objenesis-3.3.jar"

    if sys.platform.startswith("linux"):
        cmd1 = "javac -cp " + pathLin + " ValidationHarness.java"
        cmd2 = "java -ea -cp " + pathLin + " ValidationHarness"
    else:
        cmd1 = "javac -cp " + pathWin + " ValidationHarness.java"
        cmd2 = "java -ea -cp " + pathWin + " ValidationHarness"

    # Rerunning the program that has been injected the harness
    try:
        process1 = subprocess.Popen(cmd1, shell=True).wait()
        # Execute validation harness
        process2 = subprocess.Popen(cmd2, shell=True).wait()
    except Exception as e:
        print(e)
        print("Witness validation: Unknown")
        DeleteFiles()
        exit(0)

    if process1 != 0:
        print("Witness validation: Unknown")
    elif process2 != 0:
        print("Witness validation: False")
    else:
        print("Witness validation: True")
    DeleteFiles()

else:
    print("Witness result: False")
    exit(0)
