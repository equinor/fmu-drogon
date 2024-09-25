"""
 Get last value of wopth, wwpth and wgpth
 Instead of 'last' one can input a date explicitly (make sure it exists in the data set)

 Note: unfortunately explicit date is currently NOT supported with fmu-ensemble
  --> https://github.com/equinor/fmu-ensemble/issues/74

 rnyb, Nov 2019

doc:
https://equinor.github.io/fmu-ensemble/readme.html
https://github.com/equinor/fmu-ensemble/blob/master/src/fmu/ensemble/observations.py



"""


import argparse
import os

# from __future__ import print_function
from fmu import ensemble

#####################
# case settings #####

parser = argparse.ArgumentParser(
    description="Get WOPTH, WWPTH and WGPTH values at given date from"
    "single realisation"
)
parser.add_argument(
    "-s",
    "--scratch",
    required=True,
    help="scratch path to use,including username. Example: /scratch/troll_fmu/rnyb",
)
parser.add_argument("-c", "--casedir", required=True, help="name of casedir to use")
parser.add_argument(
    "-i", "--iterdir", default="iter-0", help="name of iterdir to use (default=iter-0)"
)
parser.add_argument(
    "-r", "--real", default=0, help="realization number to extract data from"
)
parser.add_argument(
    "-d", "--misfitdate", default="last", help="date to use, yyyy-mm-dd (default=last)"
)

args = parser.parse_args()

scratch = args.scratch
casedir = args.casedir
iterdir = args.iterdir
real = args.real
misfitdate = args.misfitdate

############
# MAIN #####

path = scratch + "/" + casedir + "/realization-" + str(real) + "/" + iterdir

print("Working with ensemble: ", path)

ensset = ensemble.EnsembleSet("my_ensemble_set", frompath=path)

ens = ensemble.ScratchEnsemble("single_real", path)

smry = ens.get_smry(column_keys=["W*PTH:*"], time_index=misfitdate)


# output data to file
filepath = scratch + "/" + casedir + "/share/misfit/"
filename = "wopth_wwpth_wgpth_" + misfitdate + ".csv"

if not os.path.exists(filepath):
    os.makedirs(filepath)

fout = os.path.join(filepath, filename)

print("Writing csv file: ", fout)


smry.to_csv(fout, index=False)


print("Done")
