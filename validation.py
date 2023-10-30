import sys
import subprocess
import random
import string


def GetType(file):
    dict = {}
    type = []
    with open(file, "rt") as fin:
        for row, line in enumerate(fin, 1):
            index = line.find("Verifier.nondet")
            if index != -1:
                variableType = line[
                    line.rindex("nondet") + 6 : line.rindex("(")
                ].lower()
                dict[row] = variableType
                type.append(variableType)
    print(type)
    return dict, type


def GetInvariant(witnessFile, javaFile, dict_line_type):
    className = javaFile[0 : javaFile.index("java")]
    arr = []
    for data_node in witnessFile.nodes(data=True):
        if "invariant" and "invariant.scope" in data_node[1]:
            invariant = data_node[1]["invariant"]
            scope = data_node[1]["invariant.scope"]
            if invariant.startswith("anonlocal::") and "java::" + className in scope:
                for data_edge in witnessFile.edges(data=True):
                    if data_edge[1] == data_node[0] and dict_line_type.__contains__(
                        data_edge[2]["startline"]
                    ):
                        invariant = invariant.split(" = ")[1][:-1]
                        arr.append(invariant)
    return arr


def GetSeed(arr, types):
    for i in range(len(types)):
        if "return_tmp" in arr[i]:
            if types[i] == "int":
                arr[i] = str(random.randint(-(2 ^ 31), 2 ^ 31 - 1))
            elif types[i] == "long":
                arr[i] = str(random.randint(-(2 ^ 63), 2 ^ 63 - 1)) + "L"
            elif types[i] == "short":
                arr[i] = "(short) " + str(random.randint(-2 ^ 31, 2 ^ 31 - 1))
            elif types[i] == "float":
                tmp = random.uniform(0, 1)
                arr[i] = str(round(tmp, len(str(tmp)) - 10)) + "F"
            elif types[i] == "boolean":
                arr[i] = str(random.getrandbits(1))
            elif types[i] == "char":
                arr[i] = "(char) " + str(random.randint(0, 1114111))
            elif types[i] == "double":
                arr[i] = str(random.uniform(0, 1)) + "D"
            elif types[i] == "byte":
                arr[i] = "(byte) " + str(random.randint(-(2 ^ 31), 2 ^ 31 - 1))
            elif type[i] == "string":
                size = random.randint(0, 2 ^ 31 - 1)
                bytes = [None] * size
                for index in range(size):
                    rnd = random.randint(32, 1114111)
                    bytes[index] = str(chr(rnd))
                string = "".join(bytes)
                arr[i] = string
    return arr


def HarnessRunning(types, Invariants, length, className):
    for i in range(0, length):
        StateCreation(types[i], Invariants[i], className)
        HarnessCreation(i + 8)
    with open("ValidationHarness.txt", "rt") as fin:
        with open("ValidationHarness.java", "wt") as fout:
            for line in fin:
                line = line.replace(
                    "ClassName", className[0 : className.index(".java")]
                )
                fout.write(line)


def StateCreation(type, Invariant, className):
    with open("MockTemplate.txt", "rt") as file:
        line = file.read()
        if type == "int":
            line = line.replace("Type", "nondetInt").replace("Invariant", Invariant)
        if type == "short":
            line = line.replace("Type", "nondetShort").replace("Invariant", Invariant)
        if type == "long":
            line = line.replace("Type", "nondetLong").replace("Invariant", Invariant)
        if type == "float":
            line = line.replace("Type", "nondetFloat").replace("Invariant", Invariant)
        if type == "double":
            line = line.replace("Type", "nondetDouble").replace("Invariant", Invariant)
        if type == "byte":
            line = line.replace("Type", "nondetByte").replace("Invariant", Invariant)
        if type == "string":
            try:
                Invariant = int(Invariant)
                line = line.replace("Type", "nondetString").replace("Invariant", "null")
            except ValueError:
                line = line.replace("Type", "nondetString").replace(
                    "Invariant", '"' + Invariant + '"'
                )
        if type == "char":
            line = line.replace("Type", "nondetChar").replace("Invariant", Invariant)
        if type == "boolean":
            if Invariant == "1":
                line = line.replace("Type", "nondetBoolean").replace(
                    "Invariant", "true"
                )
            if Invariant == "0":
                line = line.replace("Type", "nondetBoolean").replace(
                    "Invariant", "false"
                )

        with open("MockStatement.txt", "w") as file:
            # Write the modified content to a file.
            file.write(line)


def HarnessCreation(insert_line_number):
    with open("MockStatement.txt", "rt") as file:
        insert_text = file.readlines()
    if insert_line_number == 8:
        with open("ValidationHarnessTemplate.txt", "rt") as file:
            lines = file.readlines()
    else:
        with open("ValidationHarness.txt", "rt") as file:
            lines = file.readlines()
    insert_text = str(insert_text)[2:-2]
    lines.insert(insert_line_number, insert_text + "\n")
    with open("ValidationHarness.txt", "w") as file:
        file.writelines(lines)
