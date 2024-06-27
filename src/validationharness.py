#!/usr/bin/env python3

import os
import re
from fnmatch import fnmatch
import networkx as nx
import javalang
import subprocess
import sys


class ValidationHarness:

    VERIFIER_PACKAGE = [".", "%JAVA_HOME%\lib", "./org/sosy_lab/sv_benchmarks"]
    VERIFIER_PACKAGE_LINUX = [".", "%JAVA_HOME%\lib", "./org/sosy_lab/sv_benchmarks"]

    def __init__(self, benchmark_path, package_paths):
        self.benchmarks_dir = []
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

    @staticmethod
    def __run_command(command: list[str]) -> tuple[str, str]:
        """
        Handles running commands in subprocess
        :param command: List of seperated command to run
        :return: stdout and stderr from command
        """
        with subprocess.Popen(command) as proc:
            proc.wait()
        return proc

    def __extract_before_last_slash(self, input_str) -> str:
        """
        Extracts a string that can be used as a class path
        :param input_str: String that is being manipulated
        :return: Extracted string
        """
        if input_str.endswith(".java"):
            last_forward_slash = input_str.rfind('/')
            last_backward_slash = input_str.rfind('\\')
            if max(last_forward_slash, last_backward_slash) != -1 :
                return input_str[:max(last_forward_slash, last_backward_slash)]
            else:
                return ""
        else:
            return input_str

    def _recompile_programs(self) -> str:
        """
        Recomiles the transformed program
        :return: Name of the transformed program
        """
        self.VERIFIER_PACKAGE = (
            self.VERIFIER_PACKAGE_LINUX
            if sys.platform.startswith("linux")
            else self.VERIFIER_PACKAGE
        )

        for index, benchmark in enumerate(self.benchmark_path):
            if self.__extract_before_last_slash(benchmark) in self.VERIFIER_PACKAGE:
                continue
            else:
                self.VERIFIER_PACKAGE.append(self.__extract_before_last_slash(benchmark))

        symbol = ":" if sys.platform.startswith("linux") else ";"
        self.VERIFIER_PACKAGE = symbol.join(self.VERIFIER_PACKAGE)

        for index, benchmark in enumerate(self.benchmarks_dir):
            if benchmark.endswith("Main.java"):
                cmd = [
                    "javac",
                    "-cp",
                    self.VERIFIER_PACKAGE,
                    "-d",
                    "./",
                    benchmark,
                ]
                class_name = self.benchmarks_fileName[index]
                break
            else:
                cmd = [
                    "javac",
                    "-cp",
                    self.VERIFIER_PACKAGE,
                    "-d",
                    "./",
                    self.benchmarks_dir[0],
                ]
                class_name = self.benchmarks_fileName[0]
        proc = self.__run_command(cmd)
        if class_name.endswith(".java"):
            return class_name.replace(".java", "")
        else:
            raise ValueError("Input file path does not end with '.java'")

    def _reverify_modified_program(self, benchmark) -> None:
        """
        Reverify the transformed program
        """
        cmd = ["jbmc", benchmark]
        proc = self.__run_command(cmd)
