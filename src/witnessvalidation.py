import re
import networkx as nx
import xml.etree.ElementTree as ET


class WitnessValidation:

    def __init__(self, witness_path):
        self.witness_path = witness_path

    def _read_witness(self):
        """
        Witness reading and formatting of data
        :return: The witness file that has been read.
        """
        self._move_node_to_end(self.witness_path, "sink")
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

    def _collate_data(self, file) -> (str, dict, list, int):
        """
        Collate witness data to meet subsequent checks for completeness and connectivity.
        :param file: The witness file that has been read.
        :return entry_node: Initial nodes in correctness witness
        :return edge_dict: A dict consisting of individual edges in a witness
        :return node_arr: A arr consisting of individual nodes in a witness
        :return data_num: Number of nodes in the correctness witness
        """
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
        """
        Checking the integrity of witnesses
        :param file: The witness file that has been read.
        :param node: Node to be verified
        :param edge_dict: A dict consisting of individual edges in a witness
        :param node_arr: A arr consisting of individual nodes in a witness
        :param num: Number of nodes in the correctness witness
        :param cur: Current node
        :return: outcome of verification of integrity
        """
        if node in edge_dict and node in node_arr:
            val = edge_dict[node]

            if val == "sink":
                return num == cur + 1
            nodes = val.split(",")
            for n in nodes:
                if not self._check_integrity(
                    n, edge_dict, node_arr, num, cur + len(nodes)
                ):
                    return False
            return True
        return cur == num

    def _check_connectivity(self, graph: dict) -> bool:
        """
        Checking the connectivity of witnesses
        :param graph: Graph derived from witnesses
        :return: outcome of verification of connectivity
        """
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

    def _move_node_to_end(self, xml_file, target_id) -> None:
        """
        Move the sink node to the end
        :param xml_file: Witness
        :param target_id: Id of target node
        """
        # Parsing XML files
        tree = ET.parse(xml_file)
        root = tree.getroot()
        # Find target node
        target_node = None
        nodes = root.findall(".//{http://graphml.graphdrawing.org/xmlns}node")
        parent = root.find(".//{http://graphml.graphdrawing.org/xmlns}graph")
        for node in nodes:
            node_id = node.get("id")
            if node_id == target_id:
                target_node = node
                break

        # If the target node is found, move it to the end of the list
        if target_node is not None:
            parent.remove(target_node)
            parent.append(target_node)
            # Save the changed XML file
            tree.write(xml_file)
