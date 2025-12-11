#!/usr/bin/env python
"""
Compute statistics of N realisations to produce average value pr cell.

jriv, Jan 19 - author
rnyb, Feb 19 - adapted to ert workflow
               facies is transformed to facies probability and hence output parameter
               is renamed to facprob
rnyb, Mar 19 - exclude iterdir in outputname as foldername holds that info already
               (simplifies RMS covisualization)
rnyb, Jul 19 - also added fac 2, 3 and 10

rnyb, Sep 22 - adjusted to field xxx
               eclipsegrid_pem, airatio

"""

import os.path
import sys

import xtgeo

# read arguments
outfolder = sys.argv[1]
casedir = sys.argv[2]
iterdir = sys.argv[3]
firstreal = int(sys.argv[4])
lastreal = int(sys.argv[5]) + 1


FULLPATH = casedir + "/realization-#/" + iterdir + "/share/results/grids"

GRID_NAME = "eclipsegrid_pem"  # grid file name without extension
FEXT = ".roff"

PROPS = [
    "airatio--20180701_20180101",
    "airatio--20190701_20180101",
    "airatio--20190701_20180701",
    "airatio--20200701_20180101",
    "airatio--20200701_20190701",
]

GFILEROOT = os.path.join(FULLPATH, GRID_NAME)

# -------- main ----------------


def sum_running_stats():
    """Find avg per realisation and do a cumulative rolling mean."""

    for propname in PROPS:
        nnum = 0.0
        for real in range(firstreal, lastreal):
            pfile = GFILEROOT.replace("#", str(real)) + "--" + propname + FEXT

            if not os.path.isfile(pfile):
                print(
                    f"Real {real}: {pfile} does not exist, "
                    "skipping to next realization...",
                )
                continue

            print(f"Realization {real}")
            print(f"Loading {pfile}")

            param = xtgeo.gridproperty_from_file(pfile, name=None)
            val1d = param.values1d

            nnum += 1.0

            if nnum == 1:
                pcum = val1d
            else:
                pavg = val1d / nnum
                pcum = pcum * (nnum - 1) / nnum
                pcum = pcum + pavg

            print(
                f"Current avg for running mean {propname} ({real}) is {pcum.mean()}",
            )

        # store the average pcum which is running average
        param.values = pcum
        param.name = propname
        outfile = outfolder + "/" + GRID_NAME + "--mean--" + propname + ".roff"
        print(f"Write to file {outfile}")
        param.to_file(outfile)


if __name__ == "__main__":
    sum_running_stats()
