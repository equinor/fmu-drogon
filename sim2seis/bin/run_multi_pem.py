#! /usr/bin/env python
"""
This script executes Petro-Elastic Modelling using the petro_elastic library
available on Komodo

Author: Jimmy Zurcher (jiz@equinor.com), November 2020
"""
import time
from os import getenv, remove

import pandas as pd
import open_petro_elastic as pem
from open_petro_elastic.__main__ import (
    make_input,
    load_data_from_csv,
)
import fmu.config.utilities as utils


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
PROPS_STATIC = ["FSAND", "PORO", "dZ", "PRESSURE_INIT", "Zone"]

PEM_CSV_INPUT = "../../sim2seis/input/pem/pem_data_input.csv"
PEM_CSV_RESULTS = "../../sim2seis/output/pem/pem_results.csv"

PEM_CONFIG_FILES = [
    {
        "parameter": "Zone",
        "values": "1,3",
        "PEM_config": "../../sim2seis/model/pem/pem_config_valysar_volon.yml",
    },
    {
        "parameter": "Zone",
        "values": "2",
        "PEM_config": "../../sim2seis/model/pem/pem_config_therys.yml",
    },
]
RUN_ID = ""

KEEP_MISSING_ROWS = True
UNDEF_VALUES = None

def get_values_list(subset_number, subset_values):
    values_list = []
    assert isinstance(subset_values, str), "Values should be defined as a String"
    for element in subset_values.replace(" ", "").split(","):
        numbers = element.split("-")
        if len(numbers) == 1:
            try:
                values_list.append(int(numbers[0]))
            except ValueError:
                print(f"{numbers} must be an integer !")
        elif len(numbers) == 2:
            try:
                int1 = int(numbers[0])
                int2 = int(numbers[1])
                values_list.extend(range(int1, int2 + 1))
            except ValueError:
                print(
                    "Incorrect values for subset #{}: {}".format(
                        subset_number + 1, element
                    )
                )
                print(
                    "It should be an integer or a string of "
                    "type 'a-b' with a,b integers so that a<b"
                )
        else:
            error_message = "Range must be defined as a-b with (a,b) integers, a<b"
            raise ValueError(error_message)
    return values_list

def make_sub_dataframe(dataframe, subset_dict, subset_number):
    param = subset_dict["parameter"]
    values_list = get_values_list(subset_number, subset_dict["values"])
    subset_df = dataframe.loc[dataframe[param].isin(values_list)]
    return subset_df


def run_pem(pem_configs):

    t_start = time.perf_counter()

    df_ecl = pd.read_csv(PEM_CSV_INPUT)
    df_static = df_ecl[PROPS_STATIC].copy()

    print("start looping over dates")

    n_subsets = len(pem_configs)
    print(f">> {n_subsets} subset(s) identified...")

    dfs = []
    for date in SEISDATES:

        print(date)
        df_date = df_static.copy()

        for pname in PROPS_DYNAMIC:
            df_date[pname] = df_ecl[pname + "_" + date]

        df_date.to_csv(PEM_CSV_RESULTS, index=False)

        results = pd.DataFrame()

        # Loop through different PEM configs for different zones
        for i, subset in enumerate(pem_configs):

            print(f">> Subset {i+1}/{n_subsets}: {subset['PEM_config']}...")

            # Make subset of the input
            subset_data = make_sub_dataframe(df_date, subset, i)
            subset_data_file = "input_subset_" + str(i) + ".csv"
            subset_data.to_csv(subset_data_file)

            # Define inputs
            config_file=subset["PEM_config"]
            with open(config_file, "r") as f:
                pem_input = make_input(f, subset_data_file)

            # Compute PEM results
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

            # Compute dT properties (used for TWT properties)
            dz = subset_data["dZ"]
            dtpp = 2000.0 * dz / vp
            dtss = 2000.0 * dz / vs
            dtps = (dtpp + dtss) / 2.0

            res = pd.DataFrame(
                {
                    "VP_" + date + RUN_ID: vp,
                    "VS_" + date + RUN_ID: vs,
                    "AI_" + date + RUN_ID: saturated_rock.acoustic_impedance,
                    "SI_" + date + RUN_ID: saturated_rock.shear_impedance,
                    "DENS_" + date + RUN_ID: saturated_rock.density,
                    "VPVS_" + date + RUN_ID: vp / vs,
                    "DTPP_" + date + RUN_ID: dtpp,
                    "DTSS_" + date + RUN_ID: dtss,
                    "DTPS_" + date + RUN_ID: dtps,
                },
                index=subset_data.index,
            )

            # Add PEM results to the inputs and merge it with "results"
            subset_results = pd.concat([subset_data, res], axis=1)
            results = pd.concat([results, subset_results])

            # Delete csv file for subset data
            remove(subset_data_file)

        # Re-order the results in increasing indexes to match the data format
        results.sort_index(inplace=True)

        # drop columns already included (df_ecl), append the pem calculated
        drop_columns = PROPS_STATIC + PROPS_DYNAMIC
        dfs.append(results.drop(columns=drop_columns))

    df_all = pd.concat(dfs, axis=1)
    df_all.to_csv(PEM_CSV_RESULTS, index=False)

    print("6", time.perf_counter() - t_start)



if __name__ == "__main__":
    run_pem(PEM_CONFIG_FILES)
    print("done.")
