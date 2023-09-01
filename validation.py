import sys
import subprocess
import random


def GetType(argv):
    type = []
    if (len(argv) == 3):
        variableType = argv[2].lower()
        type.append(variableType)
    else:
        with open(sys.argv[1], "rt") as fin:
            for line in fin:
                index = line.find('Verifier.')
                if(index != -1):
                    variableType = line[index + 15 : -4].lower().replace(')','').replace('(','')
                    type.append(variableType)
    print(type)
    return type

def GetInvariant(witnessFile, argv):
    className = argv[1][0:-4]
    arr = []
    for data in witnessFile.nodes(data=True):
        if 'invariant' and 'invariant.scope' in data[1]:
            invariant = data[1]['invariant']
            scope = data[1]['invariant.scope']
            if (invariant.startswith('anonlocal') and className + 'main' in scope):
                Invariant = invariant.split(' = ')[1][: -1]
                arr.append(Invariant)
    return arr

def GetSeed(arr,types):
    for i in range(len(types)):
        if('return_tmp' in arr[i]):
            if types[i] == 'int':
                arr[i] = str(random.randint(-2^31,2^31-1))
            elif types[i] == 'long':
                arr[i] = str(random.randint(-2^63,2^63 - 1)) + 'L'
            elif types[i] == 'short':
                arr[i] = '(short)' + str(random.randint(-2^15,2^15 - 1))
            elif types[i] == 'float':
                arr[i] = str(float(random.randint(-2^128,2^128))) + 'F'
            elif types[i] == 'boolean':
                arr[i] = str(random.getrandbits(1))
            elif types[i] == 'char':
                arr[i] = ''.join(random.sample(string.ascii_letters + string.digits, 1))
    return arr


# def GetSeed(witnessFile):
#     for data in witnessFile.nodes(data=True):
#         if 'invariant' and 'invariant.scope' in data[1]:
#             invariant = data[1]['invariant']
#             scope = data[1]['invariant.scope']
#             if (invariant.startswith('anonlocal') and 'createSeed' in scope):
#                 seed = invariant.split(' = ')[1][: -1]
#                 return seed
#     return '0'


def HarnessRunning(types, Invariants, length, className):
    for i in range(0, length):
        StateCreation(types[i], Invariants[i],  className)
        HarnessCreation(i+8)
    with open("ValidationHarness.txt", "rt") as fin:
        with open("ValidationHarness.java", "wt") as fout:
            for line in fin:
                line = line.replace('ClassName', className[0:-5])
                fout.write(line)
        # subprocess.Popen(['javac', 'ValidationHarness.java']).wait()
        # # Execute validation harness
        # subprocess.Popen(['java','-ea','ValidationHarness']).wait()


def StateCreation(type, Invariant, className):
    print(type)
    print(Invariant)
    with open("MockTemplate.txt", "rt") as file:
        line = file.read()
        # line = line.replace('ClassName', className[0:-5])
        if(type == 'int'):
            line = line.replace('Type', 'nondetInt').replace(
                'Invariant', Invariant)
        if(type == 'short'):
            line = line.replace('Type', 'nondetShort').replace(
                'Invariant', Invariant)
        if(type == 'long'):
            line = line.replace('Type', 'nondetLong').replace(
                'Invariant', Invariant)
        if(type == 'float'):
            line = line.replace('Type', 'nondetFloat').replace(
                'Invariant', Invariant)
        if(type == 'double'):
            line = line.replace('Type', 'nondetDouble').replace(
                'Invariant', Invariant)
        if(type == 'string'):
            try:
                Invariant = int(Invariant)
                line = line.replace('Type', 'nondetString'). replace(
                    'Invariant', 'null')
            except ValueError:
                line = line.replace('Type', 'nondetString'). replace(
                    ' Invariant', '"' + Invariant + '"')
        if(type == 'char'):
                line = line.replace(' Type', 'nondetChar'). replace(
                    ' Invariant', '\'' + chr(int(Invariant)) + '\'')
        if(type == 'boolean'):
            if(Invariant == '1'):
                 line = line.replace(' Type', 'nondetBoolean').replace(
                    'Invariant', 'true')
            if(Invariant == '0'):
                line = line.replace('Type', 'nondetBoolean').replace(
                    'Invariant', 'false')

        with open("MockStatement.txt", "w") as file:
            # 将修改后的内容写入文件
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
