#!/usr/bin/env python
import argparse
import os
import shutil
import sys

import pandas as pd

DESCRIPTION = """
Purpose is to prepend parameters.txt from other ensembles
(for example in the case of restart runs).
"""


def parse_number(value) -> int | float:
    """
    Extracted from fmu-ensemble library

    Try to parse the string first as an integer, then as float,
    if both fails, return the original string.
    Caveats: Know your Python numbers:
    https://stackoverflow.com/questions/379906/how-do-i-parse-a-string-to-a-float-or-int-in-python
    Beware, this is a minefield.
    Args:
        value (str)
    Returns:
        int, float or string
    """
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        # int(afloat) fails on some, e.g. NaN
        try:
            if int(value) == value:
                return int(value)
            return value
        except ValueError:
            return value  # return float
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def load_txt(fullpath):
    """
    Load parameters.txt if it exist and return a dictionary
    Adapted from fmu-ensemble library
    """
    if not os.path.exists(fullpath):
        print("Warning: Cannot find " + fullpath)
        return {}
    try:
        keyvalues = pd.read_csv(
            fullpath,
            sep=r"\s+",
            index_col=0,
            dtype=str,
            usecols=[0, 1],
            header=None,
        )[1].to_dict()
    except pd.errors.EmptyDataError:
        keyvalues = {}
    new_dict = {}
    for key in keyvalues:
        new_dict[key] = parse_number(keyvalues[key])
    return new_dict


def save_txt(fullpath, parameters):
    """Save parameters dictionary into text file"""
    with open(fullpath, "w") as file_handle:
        file_handle.writelines(f"{key} {parameters[key]}\n" for key in parameters)


def create_parser():
    """Create parser"""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "path_base",
        type=str,
        help="Path to parameters.txt in current ensembles",
    )
    parser.add_argument(
        "path_prepend",
        type=str,
        help="Path to parameters.txt in the other ensembles",
    )
    return parser


def main(args=None):
    """Entry point if called from command line"""
    if args is None:
        args = sys.argv[1:]
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    path_base = parsed_args.path_base
    path_prepend = parsed_args.path_prepend

    dict_base = load_txt(path_base + "/parameters.txt")
    dict_prepend = load_txt(path_prepend + "/parameters.txt")

    for key in dict_base:
        if key in dict_prepend:
            if dict_prepend[key] != dict_base[key]:
                raise ValueError(
                    "One or more parameter(s) are in conflict.\n"
                    f"The first parameter is {key} which is changed from "
                    f"{dict_prepend[key]} to {dict_base[key]}",
                )
            else:
                print(
                    f"Warning: The parameter {key} exists in both parameters.txt\n"
                    "This should preferably be avoided",
                )
        else:
            dict_prepend[key] = dict_base[key]
    if os.path.exists(path_base + "/parameters.txt"):
        shutil.copyfile(
            path_base + "/parameters.txt",
            path_base + "/parameters_original.txt",
        )
    save_txt(path_base + "/parameters.txt", dict_prepend)


if __name__ == "__main__":
    main()
