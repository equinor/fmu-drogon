#! /usr/bin/env python3
"""
This script executes Petro-Elastic Modelling using the petro_elastic library
available on{
        "parameter": "Zone",
        "values": "3",
        "PEM config": "../../sim2seis/model/pem/pem_config_hdn_aare5_3_4_2.yml",
    },
 Komodo.

Author: Jimmy Zurcher (jiz@equinor.com), November 2020
Updated April 2021 to use several PEM config depending a discrete parameter.
Vegard Berg 28.02.2022 - for use in Heidrun N segment - multi PEM use
"""
import os
import pandas as pd
from open_petro_elastic.__main__ import (
    make_input,
    load_data_from_csv,
)
import open_petro_elastic as pem
import fmu.config.utilities as utils
from os import getenv

CFG = utils.yaml_load("../../fmuconfig/output/global_variables.yml")
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


PROPS_DATE_NAME = ["PRESSURE", "RS", "SWAT", "SGAS"]

PEM_CSV = "../../sim2seis/input/pem/pem_data_input.csv"

RUN_ID = ""

MULTI_PEM_CONFIG = [
    {
        "parameter": "Zone",
        "values": "1,3",
        "PEM config": "../../sim2seis/model/pem/pem_config_valysar_volon.yml",
    },
    {
        "parameter": "Zone",
        "values": "2",
        "PEM config": "../../sim2seis/model/pem/pem_config_therys.yml",
    },

]
KEEP_MISSING_ROWS = True
UNDEF_VALUES = None


def check_config(config, data):
    assert isinstance(config, list), "Config should be a list of dict!"
    for num, subset in enumerate(config):
        assert isinstance(subset, dict), f"Subset {num} should be a dict!"
        check = all(
            item in subset.keys() for item in ["parameter", "values", "PEM config"]
        )
        message = (
            f"Subset {num} should contain keys 'parameter', 'values' and 'PEM config'!"
        )
        assert check, message
        message = f"Subset {num} has invalid parameter {subset['parameter']}!"
        assert subset["parameter"] in data.columns, message
        message = f"Subset {num} has invalid PEM config {subset['PEM config']}!"
        assert os.path.isfile(subset["PEM config"]), message


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


def check_coverage(my_config, input_df):
    coverage = True
    coverage_list = []
    for i_subset, subset in enumerate(my_config):
        param = subset["parameter"]
        values = get_values_list(i_subset, subset["values"])
        # Compute corresponding indexes from input_df for param and values
        indexes = input_df.loc[input_df[param].isin(values)].index.tolist()
        # Add indexes to a list
        coverage_list.extend(indexes)
    # Check for multiples in coverage_list (--> overlap)
    if len(coverage_list) != len(set(coverage_list)):
        raise ValueError("ERROR: Overlap between different subsets!")
    # Compare list and input_df.index (--> missing values)
    if len(coverage_list) < len(input_df.index.tolist()):
        print("WARNING: some input data are not covered by the sum of subsets!")
        coverage = False
    return coverage


def add_missing_rows(data, results, res_col, undef_value):
    all_indexes = data.index
    res_indexes = results.index
    missing_indexes = list(set(all_indexes) - set(res_indexes))
    empty_res = pd.DataFrame(index=missing_indexes, columns=res_col)
    if undef_value is not None:
        empty_res.fillna(value=undef_value, inplace=True)
    empty_data = data.iloc[missing_indexes]
    subset_missing = pd.concat([empty_data, empty_res], axis=1)
    return results.append(subset_missing)


def run_multi_config_pem(
    config, data_file, date, keep_missing_rows=True, undef_value=None
):
    """Run multiple (PEM configurations / data subsets) at a given date

    Args:
        config: a list of dictionaries corresponding to each subset of data.
        data_file: the relative path of the input data file as csv file.
        date: a String with the date of modelling (in case of 4D modelling).
        keep_missing_rows: in case the sum of subsets of data in config does
            not cover the entire span of input data, the rows of data not
            covered will be kept if keep_missing_rows is True, those rows
            will be removed from the output file otherwise.
        undef_value: the value to assign to the output rows if no coverage
            and keep_missing_rows is True.

    """
    # Load input data
    data = load_data_from_csv(data_file)

    # Check config
    check_config(config, data)

    # Check overlap or missing coverage
    cov = check_coverage(config, data)

    # Launch calculations
    results = pd.DataFrame()
    n_subsets = len(config)
    print(f">> {n_subsets} subset(s) identified...")

    for i, subset in enumerate(config):

        print(f">> Subset {i+1}/{n_subsets}: {subset['PEM config']}...")

        # Make subset of the input
        subset_data = make_sub_dataframe(data, subset, i)
        subset_data_file = "input_subset_" + str(i) + ".csv"
        subset_data.to_csv(subset_data_file)

        # Define inputs
        inp = make_input(subset["PEM config"], subset_data_file)

        # Compute PEM results
        mixed_mineral = inp.minerals.as_mixture
        mixed_fluid = inp.fluids.as_mixture(inp.pressure)
        dry_rock_material = inp.dry_rock.material(mixed_mineral, inp.pressure)
        dense_packing = inp.dry_rock.nonporous(mixed_mineral)
        saturated_rock = pem.material.fluid_substitution(
            dry_rock_material,
            dense_packing,
            mixed_fluid,
            inp.dry_rock.porosity,
        )

        # Compute DT properties and make DataFrame with results
        dz = subset_data["dZ"]
        vp = saturated_rock.primary_velocity
        vs = saturated_rock.secondary_velocity
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
        results = pd.concat([results,subset_results])

        # Delete csv file for subset data
        os.remove(subset_data_file)

    # Manage data points not covered by config
    if not cov and keep_missing_rows:
        results = add_missing_rows(data, results, res.columns, undef_value)

    # Re-order the results in increasing indexes to match the data format
    results.sort_index(inplace=True)
    # If index = True, keep the indexing (for QC)
    # should be False to import results back to RMS
    results.to_csv(data_file, index=False)


def run_pem():
    for date in SEISDATES:
        date = str(date).replace("-", "")
        print("Date: " + date)

        # Create new input names using generic names for dynamic properties
        dframe = load_data_from_csv(PEM_CSV)
        for pname in PROPS_DATE_NAME:
            dframe[pname] = dframe[pname + "_" + date]
        dframe.to_csv(PEM_CSV, index=False)

        # Run PEM on every subset defined in MULTI_PEM_CONFIG for given date
        run_multi_config_pem(
            MULTI_PEM_CONFIG,
            PEM_CSV,
            date,
            keep_missing_rows=KEEP_MISSING_ROWS,
            undef_value=UNDEF_VALUES,
        )
    print(f"Results saved as <{PEM_CSV}>")


if __name__ == "__main__":
    run_pem()
    print("done.")
