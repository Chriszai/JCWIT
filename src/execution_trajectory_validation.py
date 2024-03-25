
def get_assert_dict(self, file):
    dict_line_assert = {}
    with open(file, "rt") as fin:
        for row, line in enumerate(fin, 1):
            index = line.find("assert")
            if index != -1:
                dict_line_assert[row] = file
    return dict_line_assert

def AssertStateChecking(self, dict_line_assert, file):
    dict = {}
    for data_node in file.nodes(data=True):
        if "invariant" in data_node[1] and "Assert" in data_node[1]["invariant"]:
            for data_edge in file.edges(data=True):
                if data_node[0] == data_edge[0]:
                    dict[data_edge[2]["startline"]] = data_edge[2]["originFileName"]
    return set(dict.items()).issubset(dict_line_assert.items())