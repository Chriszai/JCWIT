import re
import networkx as nx


class WitnessValidation:

    def __init__(self, witness_path):
        self.witness_path = witness_path

    def _read_witness(self):
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

        return witness_file

    def _collate_data(self, file) -> (str, dict, int, list):
        # Collating data from witnesses
        edge_dict = {}
        data_num = 0
        node_arr = []

        entry_node = next(
            node[0]
            for node in file.nodes(data=True)
            if node[1].get("isEntryNode", False)
        )
        for node in file.nodes(data=True):
            node_arr.append(node[0])

        for source, target, data in file.edges(data=True):
            edge_dict[source] = (
                (edge_dict.get(source) + "," + target)
                if edge_dict.get(source)
                else target
            )
            data_num += 1
        return entry_node, edge_dict, node_arr, data_num

    def _check_integrity(
        self, node: str, edge_dict: dict, node_arr: list, num: int, cur: int
    ) -> bool:
        if node in edge_dict and node in node_arr:
            val = edge_dict[node]

            if val == "sink":
                return num == cur + 1
            nodes = val.split(",")
            for n in nodes:
                if not self._check_integrity(n, edge_dict,node_arr, num, cur + len(nodes)):
                    return False
            return True
        return cur == num

    def _check_connectivity(self, graph: dict) -> bool:
        in_degrees = dict((u, 0) for u in graph)
        # Initialise all vertex incidence to 0
        for u in graph:
            for v in graph[u].split(","):
                in_degrees[v] = in_degrees.get(v, 0) + 1

        Q = [u for u, degree in in_degrees.items() if degree == 0]
        # Filter the vertices with an incidence of 0
        Seq = []
        while Q:
            u = Q.pop()
            Seq.append(u)
            for v in graph.get(u, "").split(","):
                if v in in_degrees:
                    in_degrees[v] -= 1
                    if in_degrees[v] == 0:
                        Q.append(v)

        return len(Seq) == len(in_degrees)
