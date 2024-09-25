#!/usr/bin/env python
"""
Make 'single_dates.txt' and 'diff_dates.txt' files that can be used with forward models
   ECLRST2ROFF and ECLDIFF2ROFF
The output files are stored directly in runpath folder

Extract dates from global variable yaml file, name of the global variable files is read
from input argument.
Name of the date lists are also read from input arguments

The date lists must be defined under global:dates: level in global variable file,
example of expected structure in global variable file :
global:
  dates:
    SEISMIC_HIST_DATES:
    - 2018-01-01
    - 2020-07-01
    SEISMIC_HIST_DIFFDATES:
    - - 2020-07-01
      - 2018-01-01

Roger Nybo : June 2020 - read dates from yaml file
                         hardcoded globvar filename, date list names, output file names
rnyb, Sep 20 - removing all dashes in datestrings written to file
               (workaround for temporary xtgeo bug)
rnyb, Oct 22 - Rewritten to take global variable file and date list names as user
               input arguments. This makes it easier to reuse for different purposes.
"""

import argparse

import fmu.config.utilities as utils

# -----------------------------------
parser = argparse.ArgumentParser()

parser.add_argument(
    "globvar_file",
    type=str,
    help="name of global variable file, either full path or relative to runpath",
)
parser.add_argument(
    "singledates_list",
    type=str,
    help="Name of single dates list in global variable file",
)
parser.add_argument(
    "diffdates_list", type=str, help="Name of diffdates list in global variable file"
)

args = parser.parse_args()

GLOBVAR_FILE = args.globvar_file  # sys.argv[1]
SINGLE_DATES = args.singledates_list  # sys.argv[2]
DIFF_DATES = args.diffdates_list  # sys.argv[3]

# path is relative to <runpath>
CFG_GLOBAL = utils.yaml_load(GLOBVAR_FILE)["global"]["dates"]

# output files, path is relative to runpath
singledates_output_file = "single_dates.txt"
diffdates_output_file = "diff_dates.txt"


# -----------------------------------
# read from file, extract dates and write to file
# -----------------------------------

print("Create", singledates_output_file)

with open(singledates_output_file, "w") as f_single:
    for date in CFG_GLOBAL[SINGLE_DATES]:
        print(date)
        f_single.write(str(date).replace("-", "") + "\n")


print("Create", diffdates_output_file)

with open(diffdates_output_file, "w") as f_diff:
    for dates in CFG_GLOBAL[DIFF_DATES]:
        print(dates[0], dates[1])
        f_diff.write(
            str(dates[0]).replace("-", "") + " " + str(dates[1]).replace("-", "") + "\n"
        )


print("Done.")
