class WitnessChecking:

    def __init__(self, witness_path):
        self.witness_path = witness_path

    def _read_witness(self) -> None:
        with open(self.witness_path, "r", encoding="utf-8") as file:
            data = file.read()
        # Check for malformed XML strings
        cleaned_data = re.sub(r"\(\"(.*)<(.*)>(.*)\"\)", r'("\1&lt;\2&gt;\3")', data)
        if cleaned_data != data:
            with open(self.witness_path, "w", encoding="utf-8") as file:
                file.write(cleaned_data)
        try:
            witness_file = nx.read_graphml(self.witness_path)
        except Exception as exce:
            raise ValueError("Witness file is not formatted correctly.") from exce

    def _collate_data(self, file):
        # Collating data from witnesses
        edge_dict = {}
        num = 0

        entryNode = next(
            node[0]
            for node in file.nodes(data=True)
            if node[1].get("isEntryNode", False)
        )

        for source, target, data in file.edges(data=True):
            edge_dict[source] = (
                (edge_dict.get(source) + "," + target)
                if edge_dict.get(source)
                else target
            )
            num += 1

        print("Data formatting completed")
        result = CheckIntegrity(entryNode, edge_dict, num, 0)

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
        print(edgeDict)
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
            print("The graph of witness is a DAG.")
            return True
        else:
            return False

    def get_assert_dict(self, file):
        dict_line_assert = {}
        with open(file, "rt") as fin:
            for row, line in enumerate(fin, 1):
                index = line.find("assert")
                if index != -1:
                    dict_line_assert[row] = file
        return dict_line_assert

    def AssertStateChecking(dict_line_assert, file):
        dict = {}
        for data_node in file.nodes(data=True):
            if "invariant" in data_node[1] and "Assert" in data_node[1]["invariant"]:
                for data_edge in file.edges(data=True):
                    if data_node[0] == data_edge[0]:
                        dict[data_edge[2]["startline"]] = data_edge[2]["originFileName"]
        return set(dict.items()).issubset(dict_line_assert.items())
