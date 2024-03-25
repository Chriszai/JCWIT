import os
import re
from fnmatch import fnmatch
import networkx as nx
import javalang
import subprocess


class PropertyValidation:

    def __init__(self, witness_path, benchmark_path, package_paths):
        self.benchmarks_dir = []
        self.benchmarks_fileName = []
        self.benchmark_path = benchmark_path
        self.package_paths = package_paths
        self.witness_path = witness_path
        for i in self.benchmark_path:
            if i.endswith("/common") or i.endswith("/common/"):
                continue
            elif i.endswith(".java"):
                self.benchmarks_dir.append(i)
                self.benchmarks_fileName.append(os.path.basename(i))
            else:
                for path, subdirs, files in os.walk(i):
                    for name in files:
                        if fnmatch(name, "*.java"):
                            self.benchmarks_dir.append(os.path.join(path, name))
                            self.benchmarks_fileName.append(name)

    def __read_witness(self):
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

    def _assertions_insertion(self):
        witness_file = self.__read_witness()
        variable_property_arr = []
        class_identifier_dict = []
        variable_regex = r"anonlocal::\d+([a-zA-Z]+)\s*=\s*(-?[\d.]+)[a-zA-Z]*"
        argument_regex = r"arg\d+([a-zA-Z]+)\s*=\s*(-?[\d.]+)[a-zA-Z]*"
        object_regex = (
            r"dynamic_object\$(\d+)\s*=\s*nondet_symbol<struct\s*(\w+)>\(symex::\w+\)"
        )
        object_variable_regex = r"dynamic_object\$(\d+)\.(\w+)\s*=\s*([^;]+)"
        reference_regex = r"anonlocal::\w+\s*=\s*\(void\s*\*\)&?dynamic_object\$(\w+)"

        for local_variable in filter(
            lambda node: ("invariant" in node[1]),
            witness_file.nodes(data=True),
        ):
            for variable_edge in filter(
                lambda edge: (local_variable[0] == edge[1]),
                witness_file.edges(data=True),
            ):
                object_result = re.search(object_regex, local_variable[1]["invariant"])
                reference_result = re.search(
                    reference_regex, local_variable[1]["invariant"]
                )
                if object_result is not None:
                    matches = [sr for sr in object_result.groups() if sr is not None]
                    class_identifier_dict.append(
                        {
                            "startline": variable_edge[2]["startline"],
                            "type": matches[1],
                            "No": matches[0],
                        }
                    )
                    self.__extract_reference_variable_name(
                        {**variable_edge[2], "num": matches[0], "className": matches[1]}
                    )

                if reference_result is not None:
                    matches = [sr for sr in reference_result.groups() if sr is not None]
                    for class_identifier in class_identifier_dict:
                        if (
                            class_identifier["startline"]
                            == variable_edge[2]["startline"]
                        ):
                            self.__extract_reference_variable_name(
                                {
                                    **variable_edge[2],
                                    "num": matches[0],
                                    "classIdentifier": class_identifier["type"],
                                }
                            )
                            break

                object_variable_result = re.search(
                    object_variable_regex, local_variable[1]["invariant"]
                )
                if object_variable_result is not None:
                    matches = [
                        sr for sr in object_variable_result.groups() if sr is not None
                    ]
                    self.__object_variable_matching(
                        {
                            **variable_edge[2],
                            "value": matches[2],
                            "property": matches[1],
                        },
                        class_identifier_dict,
                    )

                value_variable_result = re.search(
                    variable_regex, local_variable[1]["invariant"]
                )
                value_argument_result = re.search(
                    argument_regex, local_variable[1]["invariant"]
                )
                if value_variable_result is not None:
                    variable_property_arr.append(
                        self.__value_variable_array_form(
                            value_variable_result, variable_edge[2]
                        )
                    )
                elif value_argument_result is not None:
                    variable_property_arr.append(
                        self.__value_variable_array_form(
                            value_argument_result, variable_edge[2]
                        )
                    )
        self.__value_type_file_match(variable_property_arr)

    @staticmethod
    def __value_variable_array_form(search_result, variable_edge):
        matches = [sr for sr in search_result.groups() if sr is not None]
        search_result = re.search(r"(\d+\.\d+)", matches[1])
        value = int(matches[1]) if search_result is None else float(matches[1])
        return {**variable_edge, "type": matches[0], "value": value}

    def __read_index_of_program(self, witness_variable_info):
        if witness_variable_info["originFileName"]:
            try:
                index = self.benchmarks_fileName.index(
                    witness_variable_info["originFileName"]
                )
            except Exception as exc:
                raise ValueError(
                    f"{witness_variable_info['originFileName']} is not in the benchmarks."
                ) from exc
        return index if index else -1

    def __value_type_file_match(self, variable_property_arr):
        for witness_variable_info in variable_property_arr:
            if witness_variable_info["originFileName"]:
                try:
                    index = self.benchmarks_fileName.index(
                        witness_variable_info["originFileName"]
                    )
                except Exception as exc:
                    raise ValueError(
                        f"{witness_variable_info['originFileName']} is not in the benchmarks."
                    ) from exc
                self.__extract_value_variable_name(
                    self.benchmarks_dir[index], witness_variable_info
                )

    def __extract_value_variable_name(self, java_file, witness_variable_info):
        regex = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[+\-*/%]?=[+\-*/%]?[^=;]*;"
        with open(java_file, "rt") as fin:
            for row, line in enumerate(fin, 1):
                if (witness_variable_info["startline"]) == row:
                    search_result = re.search(regex, line)
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        self.__value_invariant_insertion(
                            java_file, matches[0], witness_variable_info["value"], row
                        )
                    else:
                        raise ValueError(
                            f"The invariant fails to insert line {row} as an assertion, make sure that the Java file has been formatted."
                        )

    def __extract_reference_variable_name(self, witness_variable_info):
        index = self.__read_index_of_program(witness_variable_info)
        regex1 = r"\w+\s+(\w+)\s*=\s*new\s+([\w.]+)\(\);"
        with open(self.benchmarks_dir[index], "rt") as fin:
            for row, line in enumerate(fin, 1):
                if (witness_variable_info["startline"]) == row:
                    search_result = re.search(regex1, line)
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        self.__reference_invariant_insertion(
                            self.benchmarks_dir[index],
                            matches,
                            witness_variable_info,
                            row,
                        )

    def __object_variable_matching(self, witness_variable_info, class_identifier_arr):
        index = self.__read_index_of_program(witness_variable_info)
        with open(self.benchmarks_dir[index], "rt") as fin:
            for row, line in enumerate(fin, 1):
                if (witness_variable_info["startline"]) == row:
                    search_result = re.search(
                        r"\b(\w+\."
                        + witness_variable_info["property"]
                        + r")\s*[+\-*/%]?=[+\-*/%]?[^=;]*;",
                        line,
                    )
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        search_result = re.match(
                            r"(\b\d+[a-zA-Z]?\b)", witness_variable_info["value"]
                        )
                        if search_result is not None:
                            results = [
                                sr for sr in search_result.groups() if sr is not None
                            ]
                            self.__value_invariant_insertion(
                                self.benchmarks_dir[index],
                                matches[0],
                                witness_variable_info["value"],
                                row,
                            )
                            return
                        search_result = re.search(
                            r"dynamic_object\$(\d+)", witness_variable_info["value"]
                        )
                        if search_result is not None:
                            results = [
                                sr for sr in search_result.groups() if sr is not None
                            ]
                            for class_identifier in class_identifier_arr:
                                if results[0] == class_identifier["No"]:
                                    self.__reference_invariant_insertion(
                                        self.benchmarks_dir[index],
                                        matches,
                                        {"classIdentifier": class_identifier["type"]},
                                        row,
                                    )
                                    return

    @staticmethod
    def __value_invariant_insertion(java_file, variable_name, value, row):
        assertion = "assert " + variable_name + " == " + str(value) + ";"
        with open(java_file, "r") as f:
            lines = f.readlines()
        lines[row - 1] = lines[row - 1].rstrip() + " " + assertion + "\n"
        with open(java_file, "w") as f:
            f.writelines(lines)
            print(
                f"Invariant {variable_name} == {str(value)} "
                f"has been inserted as assertion in the program. \033[32mSUCCESS\033[0m"
            )

    @staticmethod
    def __reference_invariant_insertion(java_file, matches, witness_variable_info, row):
        if len(matches) == 1 and "className" in witness_variable_info:
            assertion = "assert new {0}() instanceof {1};".format(
                matches[0], witness_variable_info["className"]
            )
        elif len(matches) == 2 and "className" in witness_variable_info:
            assertion = "assert new {0}() instanceof {1};".format(
                matches[1], witness_variable_info["className"]
            )
        else:
            assertion = "assert {0} instanceof {1};".format(
                matches[0], witness_variable_info["classIdentifier"]
            )
        with open(java_file, "r") as f:
            lines = f.readlines()
        lines[row - 1] = lines[row - 1].rstrip() + " " + assertion + "\n"
        with open(java_file, "w") as f:
            f.writelines(lines)
            print(
                f"Invariant in the {row} line "
                f"has been inserted as assertion in the program. \033[32mSUCCESS\033[0m"
            )
