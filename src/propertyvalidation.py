import os
import re
from fnmatch import fnmatch
import networkx as nx
import javalang
import subprocess

# from monitorprocessor import MonitorProcessor


class PropertyValidation:

    EXCLUDED_FILE_NAME = "org/sosy_lab/sv_benchmarks/Verifier.java"

    def __init__(self, witness_path, benchmark_path, package_paths):
        self.benchmarks_dir = []
        self.benchmarks_fileName = []
        self.method_counter = {}
        self.loops = []
        self.monitor_dir = []
        self.bool_dir = []
        self.benchmark_path = benchmark_path
        self.package_paths = package_paths
        self.witness_path = witness_path
        for i in self.benchmark_path:
            if (
                i.endswith("/common")
                or i.endswith("/common/")
                or i.endswith("Verifier.java")
            ):
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
        """
        Witness reading and formatting of data
        :return: The witness file that has been read.
        """
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

    def __get_boolean_variable(self) -> None:
        """
        Getting variables of type boolean in the Java programs
        """
        for benchmark in self.benchmarks_dir:
            with open(benchmark, "r") as f:
                java_code = f.read()
            tree = javalang.parse.parse(java_code)
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_name = node.name
                for node in node.body:
                    if node.filter(javalang.tree.MethodDeclaration):
                        method_name = node.name
                        for node in node.body:
                            if (
                                isinstance(node, javalang.tree.LocalVariableDeclaration)
                                and node.type.name == "boolean"
                            ):
                                self.bool_dir.append(
                                    {
                                        "className": class_name,
                                        "methodName": method_name,
                                        "name": node.declarators[0].name,
                                    }
                                )

    def __get_loops_positions(self) -> None:
        """
        Getting positions of all loops in the Java programs
        """
        for benchmark in self.benchmarks_dir:
            with open(benchmark, "r") as f:
                java_code = f.read()
            tree = javalang.parse.parse(java_code)
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_name = node.name
                for node in node.body:
                    if node.filter(javalang.tree.MethodDeclaration):
                        method_name = node.name
                        for node in node.body:
                            if isinstance(
                                node,
                                (
                                    javalang.tree.ForStatement,
                                    javalang.tree.WhileStatement,
                                    javalang.tree.DoStatement,
                                ),
                            ):
                                start_pos = node.position
                                end_pos = self.__find_end_position(node, java_code)
                                count = start_pos[0]
                                while count <= end_pos:
                                    self.loops.append(count)
                                    count += 1

    def __find_end_position(self, node, java_code) -> int:
        """
        Getting the end position of all loops in a Java program
        :param java_code: Content of the Java program
        :return: The position of a loop
        """
        # Use the position of the node to determine the range of the code it spans
        code_lines = java_code.splitlines()
        start_line = node.position.line - 1
        current_line = start_line
        open_braces = 0
        close_braces = 0

        if isinstance(node, javalang.tree.DoStatement):
            # For do-while, we need to find the while part
            do_start = current_line
            while do_start < len(code_lines):
                if "while" in code_lines[do_start]:
                    break
                do_start += 1
            return do_start + 1

        # Find the start of the block
        while current_line < len(code_lines):
            line = code_lines[current_line]
            open_braces += line.count("{")
            close_braces += line.count("}")
            if open_braces > 0 and open_braces == close_braces:
                break
            current_line += 1

        return current_line + 1

    def _assertions_insertion(self) -> (list, list):
        """
        Extracting and inserting all of the assertions into the source programs
        :retrun: Two arrays containing the method counters and the monitored methods
        """
        self.__get_boolean_variable()
        self.__get_loops_positions()
        witness_file = self.__read_witness()
        variable_property_arr = []
        class_identifier_dict = []
        variable_regex = r"anonlocal::\d+([a-zA-Z]+)\s*=\s*(-?[\d.]+)[a-zA-Z]*"
        argument_regex = r"arg\d+([a-zA-Z]+)\s*=\s*(-?[\d.]+)[a-zA-Z]*"
        object_regex = r"dynamic_object\$(\d+)\s*=\s*nondet_symbol<(const)?\s*struct\s*(\w.+)>\(symex::\w+\)"
        object_variable_regex = r"dynamic_object\$(\d+)\.(\w+)\s*=\s*([^;]+)"
        reference_regex = r"anonlocal::\w+\s*=\s*\(void\s*\*\)&dynamic_object\$(\w+)"
        string_regex = r"anonlocal::\w+\s*=\s*\(void\s*\*\)&(\w+)"

        for local_variable in filter(
            lambda node: ("invariant" in node[1]),
            witness_file.nodes(data=True),
        ):
            for variable_edge in filter(
                lambda edge: (
                    local_variable[0] == edge[1]
                    and edge[2]["originFileName"] != self.EXCLUDED_FILE_NAME
                    and edge[2]["startline"] not in self.loops
                ),
                witness_file.edges(data=True),
            ):
                object_result = re.match(object_regex, local_variable[1]["invariant"])
                reference_result = re.match(
                    reference_regex, local_variable[1]["invariant"]
                )
                object_variable_result = re.match(
                    object_variable_regex, local_variable[1]["invariant"]
                )
                # String matching
                string_result = re.match(string_regex, local_variable[1]["invariant"])
                # Variable and argument matching
                value_variable_result = re.search(
                    variable_regex, local_variable[1]["invariant"]
                )
                value_argument_result = re.search(
                    argument_regex, local_variable[1]["invariant"]
                )

                if object_result is not None:
                    matches = [sr for sr in object_result.groups() if sr is not None]
                    class_identifier_dict.append(
                        {
                            "startline": variable_edge[2]["startline"],
                            "type": matches[1] if len(matches) == 2 else matches[2],
                            "No": matches[0],
                        }
                    )
                    self.__extract_reference_variable_name(
                        {
                            **variable_edge[2],
                            "num": matches[0],
                            "className": (
                                matches[1] if len(matches) == 2 else matches[2]
                            ),
                            "scope": local_variable[1]["invariant.scope"],
                        }
                    )

                elif reference_result is not None:
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
                                    "scope": local_variable[1]["invariant.scope"],
                                }
                            )
                            break

                elif object_variable_result is not None:
                    matches = [
                        sr for sr in object_variable_result.groups() if sr is not None
                    ]
                    self.__object_variable_matching(
                        {
                            **variable_edge[2],
                            "value": matches[2],
                            "property": matches[1],
                            "scope": local_variable[1]["invariant.scope"],
                        },
                        class_identifier_dict,
                    )

                elif string_result is not None:
                    matches = [sr for sr in string_result.groups() if sr is not None]
                    self.__extract_string_variable_name(
                        {
                            **variable_edge[2],
                            "value": matches[0],
                            "scope": local_variable[1]["invariant.scope"],
                        }
                    )

                elif value_variable_result is not None:
                    # print(value_variable_result)
                    variable_property_arr.append(
                        self.__value_variable_array_form(
                            value_variable_result,
                            variable_edge[2],
                            local_variable[1]["invariant.scope"],
                        )
                    )
                elif value_argument_result is not None:
                    variable_property_arr.append(
                        self.__value_variable_array_form(
                            value_argument_result,
                            variable_edge[2],
                            local_variable[1]["invariant.scope"],
                        )
                    )
        self.__value_type_file_match(variable_property_arr)
        return self.method_counter, self.monitor_dir

    @staticmethod
    def __value_variable_array_form(search_result, variable_edge, scope) -> dict:
        """
        Constructs arrays that include all value variable types
        :param search_result: Result after regular expression matching
        :param variable_edge: Information on the edge of the corresponding variable in the witness
        :param scope: Scope of the variable
        :retrun: A dictionary contains all the information about the invariant to be asserted
        """
        matches = [sr for sr in search_result.groups() if sr is not None]
        search_result = re.search(r"(\d+\.\d+)", matches[1])
        value = int(matches[1]) if search_result is None else float(matches[1])
        return {**variable_edge, "type": matches[0], "value": value, "scope": scope}

    def __read_index_of_program(self, witness_variable_info) -> int:
        """
        Retrieve the index of the file being processed in the file array
        :param witness_variable_info: Information on invariant being processed in the witness
        :retrun: The index of the program
        """
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

    def __extract_string_variable_name(self, witness_variable_info: dict) -> None:
        """
        Extracts the name of a variable of type string
        :param witness_variable_info: Information on invariant being processed in the witness
        """
        index = self.__read_index_of_program(witness_variable_info)
        regex = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[+\-*/%]?=[+\-*/%]?[^=;]*;"
        with open(self.benchmarks_dir[index], "rt") as fin:
            for row, line in enumerate(fin, 1):
                if (witness_variable_info["startline"]) == row:
                    search_result = re.search(regex, line)
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        self.__value_invariant_insertion(
                            self.benchmarks_dir[index],
                            matches[0],
                            f'"{witness_variable_info["value"]}"',
                            row,
                            witness_variable_info["scope"],
                        )

    def __value_type_file_match(self, variable_property_arr: list) -> None:
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

    def __extract_value_variable_name(self, java_file, witness_variable_info) -> None:
        """
        Extracts the name of a variable of value-type
        :param java_file: The java file to which the variable belongs
        :param witness_variable_info: Information on invariant being processed in the witness
        """
        regex = r"\b([A-Za-z_][A-Za-z0-9_]*)\s*[+\-*/%]?=[+\-*/%]?[^=;]*;"
        method_regex = r"(\w*)\.*(.*)\((.*)\)"
        with open(java_file, "rt") as fin:
            for row, line in enumerate(fin, 1):
                if (witness_variable_info["startline"]) == row:
                    search_result = re.search(regex, line)
                    search_result2 = re.search(
                        r"\+\+([a-zA-Z_][a-zA-Z0-9_]*)|([a-zA-Z_][a-zA-Z0-9_]*)\+\+|--([a-zA-Z_][a-zA-Z0-9_]*)|([a-zA-Z_][a-zA-Z0-9_]*)--",
                        line,
                    )
                    search_result = (
                        search_result if search_result is not None else search_result2
                    )
                    method_search_result = re.search(method_regex, line)
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        self.__value_invariant_insertion(
                            java_file,
                            matches[0],
                            witness_variable_info["value"],
                            row,
                            witness_variable_info["scope"],
                        )
                    elif method_search_result is not None:
                        continue
                    else:
                        raise ValueError(
                            f"The invariant fails to insert line {row} as an assertion, make sure that the Java file has been formatted."
                        )

    def __extract_reference_variable_name(self, witness_variable_info) -> None:
        """
        Extracts the name of a variable of reference-type
        :param witness_variable_info: Information on invariant being processed in the witness
        """
        index = self.__read_index_of_program(witness_variable_info)
        regex1 = r"\w+\s+(\w+)\s*=\s*new\s+([\w.]+)\((.*)\);"
        regex2 = r"\s*new\s+([\w.]+)\((.*)\);"
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
                            matches if len(matches) >= 3 else [None, *matches],
                            witness_variable_info,
                            row,
                        )
                        return
                    search_result = re.search(regex2, line)
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        self.__reference_invariant_insertion(
                            self.benchmarks_dir[index],
                            matches if len(matches) >= 3 else [None, *matches],
                            witness_variable_info,
                            row,
                        )

    def __object_variable_matching(self, witness_variable_info, class_identifier_arr):
        """
        Match the reference to which the object refers
        :param witness_variable_info: Information on invariant being processed in the witness
        :param class_identifier_arr: Array of class identifiers in the Java programs
        """
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
                                witness_variable_info["scope"],
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
                                        (
                                            matches
                                            if len(matches) >= 2
                                            else [None, *matches]
                                        ),
                                        {"classIdentifier": class_identifier["type"]},
                                        row,
                                    )
                                    return

    def __condition_judgement(self, regex, scope, condition, row, java_file):
        """
        Determines if the current invariant is in the main method, if so returns true, otherwise returns false
        :param regex: The regular expression applied to the scope of the current invariant
        :param scope: The predicate formed by the current invariant
        :param condition: The scope of the current invariant
        :param row: The line number of the current invariant
        :param java_file: The java file to which the current invariant belongs
        :return: Result of conditional judgment
        """
        if "Main.java" in self.benchmarks_fileName:
            file_name = "Main"
        else:
            file_name = self.benchmarks_fileName[0][
                0 : self.benchmarks_fileName[0].index(".java")
            ]
        search_result = re.search(regex, scope)
        if search_result is not None:
            matches = [sr for sr in search_result.groups() if sr is not None]
            if (
                matches[1] == "main"
                and matches[2] == "[Ljava/lang/String;"
                and matches[3] == "V"
            ):
                return True
            else:
                counter_name = f"{matches[0]}_{matches[1]}_{matches[2].replace('[','').replace('java/lang/String','String').replace(';','')}_{matches[3].replace('[','').replace('java/lang/String','String').replace(';','')}"
                self.method_counter[row] = (
                    (self.method_counter.get(row) + ", " + condition)
                    if self.method_counter.get(row)
                    else condition
                )
                self.monitor_dir.append(
                    {
                        "row": row,
                        "scope": scope,
                        "counterName": counter_name,
                        "fileName": java_file,
                    }
                )
                return False

    def __replace_boolean_value(self, scope, variable_name, value):
        """
        Replaces the value of the boolean type in the assertion, where 1 is replaced with true and 0 is replaced with false.
        :param scope: The predicate formed by the current invariant
        :param variable_name: The name of the variable of type boolean in the assertion being replaced,
        :param value: The value in the current invariant
        :return: true or false
        """
        regex = r"\w+::(\w+)\.(\w+):\((.*)\)(.*)"
        result = re.search(regex, scope)
        if result is not None:
            matches = [sr for sr in result.groups() if sr is not None]
            for each in self.bool_dir:
                if (
                    each["className"] == matches[0]
                    and variable_name == each["name"]
                    and each["methodName"] == matches[1]
                ):
                    return "false" if value == 0 else "true"
        return value

    def __value_invariant_insertion(
        self, java_file, variable_name, value, row, scope
    ) -> None:
        """
        Insertion the value-type invariant in the form of assertion into the program to be validated
        :param java_file: The java file to which the current invariant belongs
        :param variable_name: The name of the variable of type boolean in the assertion being replaced,
        :param value: The value in the current invariant
        :param row: The line number of the current invariant in the java program
        :param scope: The predicate formed by the current invariant
        """
        regex = r"\w+::(\w+)\.(\w+):\((.*)\)(.*)"
        value = self.__replace_boolean_value(scope, variable_name, value)
        condition = f"{variable_name} == {str(value)}"
        assertion = "assert " + variable_name + " == " + str(value) + ";"
        result = self.__condition_judgement(regex, scope, condition, row, java_file)
        if result:
            with open(java_file, "r") as f:
                lines = f.readlines()
            lines[row - 1] = lines[row - 1].rstrip() + " " + assertion + "\n"
            with open(java_file, "w") as f:
                f.writelines(lines)
                print(
                    f"Invariant {variable_name} == {str(value)} in file {java_file}"
                    f"has been inserted as assertion in the program at line {row}. \033[32mSUCCESS\033[0m"
                )

    def __reference_invariant_insertion(
        self, java_file, matches, witness_variable_info, row
    ) -> None:
        """
        Insertion the reference-type invariant in the form of assertion into the program to be validated
        :param java_file: The java file to which the current invariant belongs
        :param matches: An array containing information about the current variable
        :param witness_variable_info: Information on invariant being processed in the witness
        :param row: The line number of the current invariant in the java program
        """
        regex = r"\w+::(\w+)\.(\w+):\((.*)\)(.*)"
        if "className" in witness_variable_info:
            condition = "new {0}({1}) instanceof {2}".format(
                matches[1], matches[2], witness_variable_info["className"]
            )
        else:
            condition = "{0} instanceof {1}".format(
                matches[0], witness_variable_info["classIdentifier"]
            )

        result = self.__condition_judgement(
            regex, witness_variable_info["scope"], condition, row, java_file
        )
        if result:
            assertion = f"assert {condition};"

            with open(java_file, "r") as f:
                lines = f.readlines()
            lines[row - 1] = lines[row - 1].rstrip() + " " + assertion + "\n"
            with open(java_file, "w") as f:
                f.writelines(lines)
                print(
                    f"Invariant in the {row} line "
                    f"has been inserted as assertion in the program. \033[32mSUCCESS\033[0m"
                )
