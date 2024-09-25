#! /usr/bin/env python
"""
This script executes Petro-Elastic Modelling using the petro_elastic library
available on Komodo

Author: Jimmy Zurcher (jiz@equinor.com), November 2020
"""
import argparse

import fmu.config.utilities as utils
import open_petro_elastic as pem
import pandas as pd
from open_petro_elastic.__main__ import make_input

CFG = utils.yaml_load("../../fmuconfig/output/global_variables.yml")

INITDATE = str(CFG["global"]["dates"]["ECLIPSE_INIT_DATE"]).replace("-", "")
print("INITDATE is", INITDATE)

PROPS_DATE_NAME = ["PRESSURE", "RS", "SWAT", "SGAS"]

PEM_CSV = "../../sim2seis/input/pem/pem_geoseis_input.csv"
PEM_CSV_RESULTS = "../../sim2seis/output/pem/pem_geoseis_results.csv"

RUN_ID = "_geo"


def run_pem(pem_config_file):
    listdates = []
    listdates.append(INITDATE)

    for date in listdates:
        print(date)

        # INPUTS - using generic names for dynamic properties
        df = pd.read_csv(PEM_CSV)
        for pname in PROPS_DATE_NAME:
            df[pname] = df[pname + "_" + date]
        df.to_csv(PEM_CSV_RESULTS, index=False)

        with open(pem_config_file) as f:
            pem_input = make_input(f, PEM_CSV_RESULTS)

        # PEM CALCULATION
        print(">> PEM calculation")
        pressure = pem_input.pressure
        mixed_mineral = pem_input.minerals.as_mixture
        mixed_fluid = pem_input.fluids.as_mixture(pressure)
        dry_rock_material = pem_input.dry_rock.material(mixed_mineral, pressure)
        dense_packing = pem_input.dry_rock.nonporous(mixed_mineral)
        saturated_rock = pem.material.fluid_substitution(
            dry_rock_material,
            dense_packing,
            mixed_fluid,
            pem_input.dry_rock.porosity,
        )

        # OUTPUTS
        vp = saturated_rock.primary_velocity
        vs = saturated_rock.secondary_velocity
        df["VP_" + date + RUN_ID] = vp
        df["VS_" + date + RUN_ID] = vs
        df["AI_" + date + RUN_ID] = saturated_rock.acoustic_impedance
        df["SI_" + date + RUN_ID] = saturated_rock.shear_impedance
        df["DENS_" + date + RUN_ID] = saturated_rock.density
        df["VPVS_" + date + RUN_ID] = vp / vs

        # Compute dT properties (used for TWT properties)
        dz = df["dZ"]
        dtpp = 2000.0 * dz / vp
        dtss = 2000.0 * dz / vs
        dtps = (dtpp + dtss) / 2.0

        df["DTPP_" + date + RUN_ID] = dtpp
        df["DTSS_" + date + RUN_ID] = dtss
        df["DTPS_" + date + RUN_ID] = dtps

        df.to_csv(PEM_CSV_RESULTS, index=False)


if __name__ == "__main__":
    # parse input arguments
    parser = argparse.ArgumentParser(description="Run pem with pem config as input")
    parser.add_argument(
        "filename",
        metavar="Filname for pem config file",
        type=str,
        nargs="?",
        help="Filename for pem config file",
    )

    args = parser.parse_args()
    filename = str(args.filename)

    run_pem(filename)
    print("done.")
