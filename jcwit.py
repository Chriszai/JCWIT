#!/usr/bin/env python3
import sys
import subprocess
import validation as validation
import os
from sys import exit
from fnmatch import fnmatch

# sys.path.append("/home/tong/.local/lib/python3.8/site-packages")

import networkx as nx

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
            print("1.0")
            exit(0)
        else:
            print("Usage: ./jcwit.py --witness [witness_file] [list of folders]")
        exit(0)

    print("1.0")

    benchmarks_dir = []
    benchmarks_className = []
    for i in sys.argv[3:]:
        if i.endswith("/common") or i.endswith("/common/"):
            continue
        if ".java" in i:
            benchmarks_dir.append(i)
            benchmarks_className.append(i[0 : i.index("java") - 1])

        else:
            for path, subdirs, files in os.walk(i):
                for name in files:
                    if fnmatch(name, "*.java"):
                        benchmarks_dir.append(os.path.join(path, name))
                        benchmarks_className.append(name[0 : name.index("java") - 1])

    print("benchmark: ", benchmarks_dir)

    witnessFile = nx.read_graphml(sys.argv[2])
    violation = False
    for violationKey in witnessFile.nodes(data=True):
        if "isViolationNode" in violationKey[1]:
            violation = True
except Exception as e:
    print("Witness result: Unknown")
    print(e)
    exit(0)

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
        for index, javaFile in enumerate(benchmarks_dir):
            dict_line_type, variableType = validation.GetType(javaFile)
            types = types + variableType
            Invariant = validation.GetInvariant(
                witnessFile, benchmarks_className[index], dict_line_type
            )
            Invariants = Invariants + Invariant

        if len(types) == 0:
            print("Witness validation: Unknown")
            exit(0)

        while len(types) != len(Invariants) and len(types) > len(Invariants):
            Invariants.append(" ")

        seed = validation.GetSeed(Invariants, types)

        # Creating harness that used for running
        validation.HarnessRunning(types, seed, len(types))
    except Exception as e:
        print(e)
        DeleteFiles()
        print("Witness validation: Unknown")
        exit(0)

    # Check the operating system of this machine
    pathWin = ".;./dependencies/byte-buddy-1.14.1.jar;./dependencies/byte-buddy-agent-1.14.1.jar;./dependencies/mockito-core-5.2.0.jar;./dependencies/objenesis-3.3.jar"
    pathLin = ".:./dependencies/byte-buddy-1.14.1.jar:./dependencies/byte-buddy-agent-1.14.1.jar:./dependencies/mockito-core-5.2.0.jar:./dependencies/objenesis-3.3.jar"

    if len(benchmarks_dir) == 1:
        cmd0 = "javac -d ./ " + benchmarks_dir[0]
    else:
        for benchmark in benchmarks_dir:
            if benchmark.endswith("Main.java"):
                cmd0 = "javac -d ./ " + benchmark

    if sys.platform.startswith("linux"):
        cmd1 = "javac -cp " + pathLin + " ValidationHarness.java"
        cmd2 = "java -ea -cp " + pathLin + " ValidationHarness"
    else:
        cmd1 = "javac -cp " + pathWin + " ValidationHarness.java"
        cmd2 = "java -ea -cp " + pathWin + " ValidationHarness"

    # Rerunning the program that has been injected the harness
    try:
        process0 = subprocess.Popen(cmd0, shell=True).wait()
        process1 = subprocess.Popen(cmd1, shell=True).wait()
        # Execute validation harness
        process2 = subprocess.Popen(cmd2, shell=True).wait()
    except Exception as e:
        print("Witness validation: True")
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
    print("Witness result: Unknown")
    exit(0)

