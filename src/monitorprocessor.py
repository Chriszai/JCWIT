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
        self.condition_dic = {}
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

    def _monitor_counter_initialization(
        self, condition_dic: dict, methods_arr: list
    ) -> None:
        """
        Method Monitor Initialization
        :param condition_dic: predicate that needs to be asserted
        :param method_dir: List of methods
        """
        insert_text = ""
        self.condition_dic = condition_dic
        self.methods_arr = methods_arr
        for counter in methods_arr:
            insert_text = (
                f"    public static int {str(counter['counterName'])} = 0;\n" + insert_text
            )
        for benchmark in self.benchmarks_dir:
            with open(benchmark, "rt") as fin:
                self.__class_import(benchmark)
        self.__generate_monitor_file(insert_text, self.insert_line_number)
        
    def _assertions_selection_insertion(
        self
    ) -> None:
        """
        Inserting assertion selection method into the program

        """
        for key in self.condition_dic:
            for each in self.methods_arr:
                if int(each["row"]) == int(key):
                    with open(each["fileName"], "r") as f:
                        lines = f.readlines()
                    assertion = f'MethodCallMonitor.assertionImplementation(MethodCallMonitor.{each["counterName"]} ++, {self.condition_dic[key]});'
                    lines[int(key) - 1] = (
                        lines[int(key) - 1].rstrip() + " " + assertion + "\n"
                    )
                    with open(each["fileName"], "w") as f:
                        f.writelines(lines)
                        print(
                            f"Invariant {self.condition_dic[key]} in file {each['fileName']} "
                            f"has been inserted as assertion in the program at line {key}. \033[32mSUCCESS\033[0m"
                        )
                    break

    def __class_import(self, benchmark) -> None:
        """
        Import the class of method monitor
        :param benchmark: The current java file being excuted
        """
        index = self.__find_first_code_line_number(benchmark)
        with open(benchmark, "rt") as f:
            lines = f.readlines()
        lines[index] = (
            lines[index].rstrip() + self.IMPORT_NAME + "\n"
            if self.IMPORT_NAME not in lines[index]
            else lines[index]
        )
        with open(benchmark, "w") as f:
            f.writelines(lines)

    def __find_first_code_line_number(self, file_path):
        multi_line_comment = False
        single_line_comment_pattern = re.compile(r"^\s*//")
        multi_line_comment_start_pattern = re.compile(r"^\s*/\*")
        multi_line_comment_end_pattern = re.compile(r"\*/\s*$")

        with open(file_path, "r") as file:
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
                if multi_line_comment and multi_line_comment_end_pattern.search(
                    stripped_line
                ):
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
