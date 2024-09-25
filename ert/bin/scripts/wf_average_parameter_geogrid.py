#!/usr/bin/env python3
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
               facprop: facies1 (good sand), facies2 (med sand), facies12
               (good + med sand)

               added conversion from discrete to continuous parameter --> important
               for correct average

Important: with respect to the facies parameter, the script must be set up carefully to
           fit the model it is run on, contact rnyb for assistance if needed

"""

import os.path
import sys

import numpy as np
import xtgeo

# read arguments
outfolder = sys.argv[1]
casedir = sys.argv[2]
iterdir = sys.argv[3]
firstreal = int(sys.argv[4])
lastreal = int(sys.argv[5]) + 1


FULLPATH = casedir + "/realization-#/" + iterdir + "/share/results/grids"

GRID_NAME = "geogrid"  # grid file name without extension
FEXT = ".roff"

PROPS = ["phit", "klogh", "facies1", "facies12"]
# Note how the facies parameter is given with an additional number tag representing
# facies value.

GFILEROOT = os.path.join(FULLPATH, GRID_NAME)

# -------- main ----------------


def _get_values1d(prop, propname, factag):
    """Return xtgeo property values as 1d numpy array. Special treatment of klogh and
    facies"""

    if propname == "klogh":
        return np.log(prop.values1d)

    if propname == "facies":
        val1d_orig = prop.values1d.copy()
        val1d = prop.values1d.astype(float)

        val1d = np.ones_like(val1d)
        val1d[val1d_orig < factag - 0.1] = 0.0
        val1d[val1d_orig > factag + 0.1] = 0.0
        return val1d

    return prop.values1d


def sum_running_stats():
    """Find avg per realisation and do a cumulative rolling mean."""

    for propname in PROPS:
        print(f"---- Working on {propname} ----")

        # facies spesific
        factag = None
        if propname.startswith("facies"):
            factag = int(propname.replace("facies", ""))
            propname = "facies"

        nnum = 0.0
        for real in range(firstreal, lastreal):
            pfile = GFILEROOT.replace("#", str(real)) + "--" + propname + FEXT

            if not os.path.isfile(pfile):
                print(f"Real {real}: {pfile} does not exist, skipping this real...")
                continue

            print(f"Realization {real}")
            print(f"Loading {pfile}")

            prop = xtgeo.gridproperty_from_file(pfile)
            prop.discrete_to_continuous()  # important to always ensure cont param

            val1d = _get_values1d(prop, propname, factag)

            nnum += 1.0

            # Calculate cummulative average
            if nnum == 1:
                pcum = val1d.copy()
            else:
                pavg = val1d.copy() / nnum
                pcum = pcum * (nnum - 1) / nnum
                pcum = pcum + pavg

            print(f"Current avg for {propname} running mean is {pcum.mean()}")

        # store the average pcum which is running average
        if propname == "klogh":
            prop.values = np.exp(pcum.reshape(prop.dimensions))
        else:
            prop.values = pcum  # .reshape(prop.dimensions)

        if propname == "facies":
            prop.name = "fac" + str(factag) + "prob"
            outfile = (
                outfolder
                + "/"
                + GRID_NAME
                + "--mean--"
                + "fac"
                + str(factag)
                + "prob"
                + FEXT
            )
        else:
            prop.name = propname
            outfile = outfolder + "/" + GRID_NAME + "--mean--" + propname + FEXT

        print(f"Write to file {outfile}")
        prop.to_file(outfile)


if __name__ == "__main__":
    sum_running_stats()
