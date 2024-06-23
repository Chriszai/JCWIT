import os
import re
from fnmatch import fnmatch
import networkx as nx
import javalang
import subprocess


class MonitorProcessor:

    METHODCALLMONITOR_PACKAGE = "./Components/MethodCallMonitor.java"
    insert_line_number = 8
    FORMAT = "MethodCallMonitor.assertionImplementation();"
    CLASS_NAME = "MethodCallMonitor"
    IMPORT_NAME = " import Components.MethodCallMonitor;"
    CONVERSION_DICT = {
        "int": "I",
        "double": "D",
        "float": "F",
        "char": "C",
        "short": "S",
        "long": "J",
        "byte": "B",
        "boolean": "Z",
    }

    def __init__(self, benchmark_path, package_paths):
        self.benchmarks_dir = []
        self.references_arr = []
        self.methods_arr = []
        self.benchmarks_fileName = []
        self.benchmark_path = benchmark_path
        self.package_paths = package_paths
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

    def _monitor_counter_initialization(self) -> None:
        """
        Method Monitor Initialization
        """
        insert_text = ""
        for benchmark in self.benchmarks_dir:
            with open(benchmark, "r") as f:
                java_code = f.read()
            tree = javalang.parse.parse(java_code)
            for path, node in tree.filter(javalang.tree.ClassDeclaration):
                class_name = node.name
                for node in node.body:
                    if node.filter(javalang.tree.MethodDeclaration):
                        method_parameter = ""
                        self.methods_arr.append(
                            {
                                "className": class_name,
                                "methodName": node.name,
                                "length": len(node.parameters),
                            }
                        )
                        for parameter in node.parameters:
                            if isinstance(parameter, javalang.tree.FormalParameter):
                                method_parameter = (
                                    method_parameter
                                    + self.CONVERSION_DICT[parameter.type.name.lower()]
                                    if isinstance(
                                        parameter.type, javalang.tree.BasicType
                                    )
                                    else method_parameter + f"L{parameter.type.name}"
                                )

                        counter_name = (
                            f"{class_name}_{node.name}_{method_parameter}_{self.CONVERSION_DICT[node.return_type.name]}"
                            if node.return_type != None
                            else f"{class_name}_{node.name}_{method_parameter}_V"
                        )
                        insert_text = (
                            f"    public static int {str(counter_name)} = 0;\n"
                            + insert_text
                        )
                        for node in node.body:
                            if isinstance(node, javalang.tree.LocalVariableDeclaration):
                                if isinstance(node.type, javalang.tree.ReferenceType):
                                    self.references_arr.append(
                                        {
                                            "location": counter_name,
                                            "type": node.type.name,
                                            "referenceName": node.declarators[0].name,
                                        }
                                    )
                        self.__counter_to_count(counter_name, benchmark)
        self.__generate_monitor_file(insert_text, self.insert_line_number)

    def _monitor_counter_insertion(self) -> None:
        """
        Inserting a Method Counter in the Method Monitor
        """
        regex = r"(\w*)\.*(.*)\((.*)\)"
        for benchmark in self.benchmarks_dir:
            with open(benchmark, "rt") as fin:
                for row, line in enumerate(fin, 1):
                    search_result = re.search(regex, line)
                    if search_result is not None:
                        matches = [
                            sr for sr in search_result.groups() if sr is not None
                        ]
                        for reference in self.references_arr:
                            for method in self.methods_arr:
                                if (
                                    matches[0] == reference["referenceName"]
                                    and reference["type"] == method["className"]
                                    and matches[1] == method["methodName"]
                                    and len(matches[2].split(",")) == method["length"]
                                ) or (
                                    matches[0] == method["className"]
                                    and matches[1] == method["methodName"]
                                    and len(matches[2].split(",")) == method["length"]
                                ):
                                    statement = f"{self.CLASS_NAME}.{method['className']}{method['methodName']}{method['length']} ++;"
                                    self.__statement_insertion(
                                        benchmark, statement, row
                                    )
                self.__class_import(benchmark)

    def __counter_to_count(self, counter_name: str, benchmark: list):
        """
        Counting with method counters
        :param counter_name: Name of counter
        :param benchmark: The current java file being excuted
        """
        regex = r"(\w*)\.*(.*)\((.*)\)"
        with open(benchmark, "rt") as fin:
            for row, line in enumerate(fin, 1):
                search_result = re.match(regex, line)
                if search_result is not None:
                    counter_name_arr = counter_name.split("_")
                    matches = [
                        sr.strip() for sr in search_result.groups() if sr is not None
                    ]
                    if matches[1] == counter_name_arr[1] and (
                        len(matches[2].split(",")) == len(counter_name_arr[2])
                        or (
                            len(counter_name_arr[2]) == 0
                            and len(matches[2].split(",")) == 1
                        )
                    ):
                        statement = f"MethodCallMonitor.{counter_name} ++;"
                        self.__statement_insertion(benchmark, statement, row)

    def _assertions_selection_insertion(
        self, condition_dic: dict, method_dir: dict
    ) -> None:
        """
        Inserting assertion selection method into the program
        :param condition_dic: predicate that needs to be asserted
        :param method_dir: List of methods
        """
        for key in condition_dic:
            for each in method_dir:
                if int(each["row"]) == int(key):
                    with open(each["fileName"], "r") as f:
                        lines = f.readlines()
                    assertion = f'MethodCallMonitor.assertionImplementation(MethodCallMonitor.{each["counterName"]}, {condition_dic[key]});'
                    lines[int(key) - 1] = (
                        lines[int(key) - 1].rstrip() + " " + assertion + "\n"
                    )
                    with open(each["fileName"], "w") as f:
                        f.writelines(lines)
                        print(
                            f"Invariant {condition_dic[key]} in file {each['fileName']} "
                            f"has been inserted as assertion in the program at line {key}. \033[32mSUCCESS\033[0m"
                        )
                    break

    def __class_import(self, benchmark) -> None:
        """
        Import the class of method monitor
        :param benchmark: The current java file being excuted
        """
        index = self.find_first_code_line_number(benchmark)
        with open(benchmark, "rt") as f:
            lines = f.readlines()
        lines[index] = (
            lines[index].rstrip() + self.IMPORT_NAME + "\n"
            if self.IMPORT_NAME not in lines[index]
            else lines[index]
        )
        with open(benchmark, "w") as f:
            f.writelines(lines)
    
    def find_first_code_line_number(self, file_path):
        multi_line_comment = False
        single_line_comment_pattern = re.compile(r'^\s*//')
        multi_line_comment_start_pattern = re.compile(r'^\s*/\*')
        multi_line_comment_end_pattern = re.compile(r'\*/\s*$')

        with open(file_path, 'r') as file:
            for line_number, line in enumerate(file, start=0):
                stripped_line = line.strip()
                # Check for single-line comment
                if single_line_comment_pattern.match(stripped_line):
                    continue
                # Check for multi-line comment start
                if multi_line_comment_start_pattern.match(stripped_line):
                    multi_line_comment = True
                    continue
                # Check for multi-line comment end
                if multi_line_comment and multi_line_comment_end_pattern.search(stripped_line):
                    multi_line_comment = False
                    continue
                # Skip lines within multi-line comments
                if multi_line_comment:
                    continue
                # Check if the line is not empty and not a comment
                if stripped_line:
                    return line_number
        return 0

    @staticmethod
    def __statement_insertion(benchmark: str, statement: str, row) -> None:
        """
        Insert the statement into the program
        :param benchmark: The current java file being excuted
        :param statement: The statement needs to be inserted
        """
        with open(benchmark, "r") as f:
            lines = f.readlines()
        lines[row - 1] = lines[row - 1].rstrip() + " " + statement + "\n"
        with open(benchmark, "w") as f:
            f.writelines(lines)

    @staticmethod
    def __generate_monitor_file(insert_text: str, insert_line_number: int) -> None:
        """
        Generate method monitor class
        :param insert_text: The text needs to be inserted
        :param insert_line_number: The line number where the text is located
        """
        with open("./Components/MethodCallMonitor.txt", "rt") as file:
            lines = file.readlines()
        lines.insert(insert_line_number, insert_text + "\n")
        with open("./Components/MethodCallMonitor.java", "w") as file:
            file.writelines(lines)
