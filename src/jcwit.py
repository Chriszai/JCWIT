#!/usr/bin/env python3
import sys
import subprocess
import argparse
from witnessvalidation import WitnessValidation
from propertyvalidation import PropertyValidation
from validationharness import ValidationHarness
from monitorprocessor import MonitorProcessor
from __init__ import __version__

# sys.path.append("/home/tong/.local/lib/python3.8/site-packages")

import networkx as nx


# How to call this script on Linux:
# ./jcwit.py --witness [witness_file] [list of folders/JavaFiles]
# or
# ./jcwit.py --version
def dir_path(path):
    """
    Checks if a path is a valid directory
    :param path: Potential directory
    :return: The original path if valid
    """
    if os.path.isdir(path):
        return path
    raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Creates a parser for the command-line options.
    @return: An argparse.ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="""
                   Validate a given Java program with a witness conforming to the appropriate SV-COMP
                   exchange format.
               """,
    )

    parser.add_argument(
        "benchmark", type=str, nargs="*", help="Path to the benchmark directory"
    )

    parser.add_argument(
        "--packages",
        dest="package_paths",
        type=dir_path,
        nargs="*",
        help="Path to the packages used by the benchmark",
    )

    parser.add_argument(
        "--witness",
        dest="witness_file",
        required=True,
        type=str,
        action="store",
        help="Path to the witness file. Must conform to the exchange format",
    )

    parser.add_argument(
        "--version", action="version", version="%(prog)s " + __version__
    )

    return parser


def main():
    parser = create_argument_parser()
    config = parser.parse_args(sys.argv[1:])
    config = vars(config)
    try:

        wv = WitnessValidation(config["witness_file"])
        pv = PropertyValidation(
            config["witness_file"], config["benchmark"], config["package_paths"]
        )
        mp = MonitorProcessor(config["benchmark"], config["package_paths"])
        mp._monitor_counter_initialization()
        mp._monitor_counter_insertion()

        witness_file = wv._read_witness()
        entry_node, edge_dict, node_arr, data_num = wv._collate_data(witness_file)
        integrity = wv._check_integrity(entry_node, edge_dict, node_arr, data_num, 0)
        print(integrity)
        connectivity = wv._check_connectivity(edge_dict)
        print(connectivity)
        condition_dic, method_dir = pv._assertions_insertion()
        mp._assertions_selection_insertion(condition_dic, method_dir)

        vh = ValidationHarness(config["benchmark"], config["package_paths"])
        benchmark = vh._recompile_programs()
        vh._reverify_modified_program(benchmark)

    except BaseException as err:
        print(f"jcwit: Could not validate witness \n{err}")
        print("Witness validation: Unknown")
    sys.exit()


if __name__ == "__main__":
    main()
