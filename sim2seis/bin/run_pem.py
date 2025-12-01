#! /usr/bin/env python
"""
This script executes Petro-Elastic Modelling using the petro_elastic library
available on Komodo

Author: Jimmy Zurcher (jiz@equinor.com), November 2020
"""

import argparse
import time
from os import getenv

import fmu.config.utilities as utils
import open_petro_elastic as pem
import pandas as pd
from open_petro_elastic.__main__ import make_input

# Read environment variable
SIM2SEIS_PRED = getenv("FLOWSIM_IS_PREDICTION")
print(f"SIM2SEIS_PRED is {SIM2SEIS_PRED}")

# import pred dates if in pred mode
if SIM2SEIS_PRED:
    CFG = utils.yaml_load("../../fmuconfig/output/global_variables_pred.yml")
    SEISDATES = [
        str(sdate).replace("-", "")
        for sdate in CFG["global"]["dates"]["SEISMIC_PRED_DATES"]
    ]
    print(SEISDATES)
# import hist dates
else:
    CFG = utils.yaml_load("../../fmuconfig/output/global_variables.yml")
    SEISDATES = [
        str(sdate).replace("-", "")
        for sdate in CFG["global"]["dates"]["SEISMIC_HIST_DATES"]
    ]
    print(SEISDATES)

PROPS_DYNAMIC = ["PRESSURE", "RS", "SWAT", "SGAS"]
PROPS_STATIC = ["FSAND", "PORO", "dZ", "PRESSURE_INIT"]

PEM_CSV_INPUT = "../../sim2seis/input/pem/pem_data_input.csv"
PEM_CSV_RESULTS = "../../sim2seis/output/pem/pem_results.csv"

RUN_ID = ""


def run_pem(config_file):
    PEM_CONFIG_FILE = config_file
    t_start = time.perf_counter()

    df_ecl = pd.read_csv(PEM_CSV_INPUT)
    df_static = df_ecl[PROPS_STATIC].copy()

    print("start looping over dates")

    dfs = []
    for date in SEISDATES:
        print(date)
        date = str(date).replace("-", "")
        df_date = df_static.copy()

        for pname in PROPS_DYNAMIC:
            df_date[pname] = df_ecl[pname + "_" + date]

        df_date.to_csv(PEM_CSV_RESULTS, index=False)

        with open(PEM_CONFIG_FILE) as f:
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
        df_date["VP_" + date + RUN_ID] = vp
        df_date["VS_" + date + RUN_ID] = vs
        df_date["AI_" + date + RUN_ID] = saturated_rock.acoustic_impedance
        df_date["SI_" + date + RUN_ID] = saturated_rock.shear_impedance
        df_date["DENS_" + date + RUN_ID] = saturated_rock.density
        df_date["VPVS_" + date + RUN_ID] = vp / vs

        # Compute dT properties (used for TWT properties)
        dz = df_date["dZ"]
        dtpp = 2000.0 * dz / vp
        dtss = 2000.0 * dz / vs
        dtps = (dtpp + dtss) / 2.0

        df_date["DTPP_" + date + RUN_ID] = dtpp
        df_date["DTSS_" + date + RUN_ID] = dtss
        df_date["DTPS_" + date + RUN_ID] = dtps

        # drop columns already included (df_ecl), append the pem calculated
        drop_columns = PROPS_STATIC + PROPS_DYNAMIC
        dfs.append(df_date.drop(columns=drop_columns))

    df_all = pd.concat(dfs, axis=1)
    df_all.to_csv(PEM_CSV_RESULTS, index=False)

    print("6", time.perf_counter() - t_start)


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
