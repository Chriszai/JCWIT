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
    print("Data formatting completed")
    result = CheckIntegrity(entryNode, edgeDict, num, 0)

    if result == True:
        print("Graph integrity check completed")
    else:
        print("This correctness witness is not complete.")
    return result


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
    print("Data dict creation complete")
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
