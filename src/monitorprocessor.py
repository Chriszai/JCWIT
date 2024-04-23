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

    def _monitor_counter_initialization(self):
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
                            f"    public static int {str(counter_name)} = -1;\n"
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
        self.__generate_monitor_file(insert_text, self.insert_line_number)

    def _monitor_counter_insertion(self):
        regex = r"(\w+)\.(.*)\((.*)\)"
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

    def _assertions_selection_insertion(self, condition_dic, method_dir):
        for key in condition_dic:
            for each in method_dir:
                if int(each["row"]) == int(key):
                    with open(each["fileName"], "r") as f:
                        lines = f.readlines()
                    assertion = f'MethodCallMonitor.assertionImplementation("{each["counterName"]}", {condition_dic[key]});'
                    lines[int(key) - 1] = lines[int(key) - 1].rstrip() + " " + assertion + "\n"
                    with open(each['fileName'], "w") as f:
                        f.writelines(lines)
                        print(
                            f"Invariant in the {int(key)} line "
                            f"has been inserted as assertion in the program. \033[32mSUCCESS\033[0m"
                        )
                    break

    @staticmethod
    def __class_import(benchmark):
        with open(benchmark, "rt") as f:
            lines = f.readlines()
        lines[0] = lines[0].rstrip() + f" import Components.MethodCallMonitor;" + "\n"
        with open(benchmark, "w") as f:
            f.writelines(lines)

    @staticmethod
    def __statement_insertion(benchmark, statement, row):
        with open(benchmark, "r") as f:
            lines = f.readlines()
        lines[row - 1] = lines[row - 1].rstrip() + " " + statement + "\n"
        with open(benchmark, "w") as f:
            f.writelines(lines)

    @staticmethod
    def __generate_monitor_file(insert_text, insert_line_number):
        with open("./Components/MethodCallMonitor.txt", "rt") as file:
            lines = file.readlines()
        lines.insert(insert_line_number, insert_text + "\n")
        with open("./Components/MethodCallMonitor.java", "w") as file:
            file.writelines(lines)
