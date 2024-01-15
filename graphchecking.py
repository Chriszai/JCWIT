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
    for data in file.edges(data=True):
        if edgeDict.get(data[0]) == None:
            edgeDict.update({data[0]: data[1]})
        else:
            str = edgeDict.get(data[0]) + "," + data[1]
            edgeDict.update({data[0]: str})
    print("Data dict creation complete")
    return InspectionCircle(edgeDict)


def InspectionCircle(graph):
    in_degrees = dict((u, 0) for u in graph)
    # Initialise all vertex incidence to 0
    num = len(in_degrees)
    for u in graph:
        values = graph[u].split(",")
        for v in values:
            if v in in_degrees:
                in_degrees[v] += 1
                # Calculate the incidence of each vertex
            else:
                in_degrees.update({v: 1})
                num += 1

    Q = [u for u in in_degrees if in_degrees[u] == 0]
    # Filter the vertices with an incidence of 0
    Seq = []
    while Q:
        u = Q.pop()
        Seq.append(u)
        if u in graph:
            values = graph[u].split(",")
            for v in values:
                in_degrees[v] -= 1
                if in_degrees[v] == 0:
                    Q.append(v)

    if len(Seq) == num:
        return True
        print("The graph of witness is DAG")
    else:
        return False
