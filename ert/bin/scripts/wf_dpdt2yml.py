#!/usr/bin/env python
"""create dpdt gen obs file on yml format"""

import argparse

import numpy as np
import pandas as pd
import yaml

parser = argparse.ArgumentParser()
parser.add_argument("dpdt_file_saphir", help="Saphir pressure derivative file")
parser.add_argument("dpdt_file_yml", help="Pressure derivative yaml file")
parser.add_argument(
    "index_list",
    nargs="+",
    help="Index list for general observation, None, or the numbers in the list, "
    "f.ex. 0 10",
)
args = parser.parse_args()

dpdt_file_saphir = args.dpdt_file_saphir
dpdt_file_yml = args.dpdt_file_yml
index_list = args.index_list

unc = 0.1
min_unc_value = 0.05

time_name = "dTime"
dpdt_name = "Pressure derivative"


##############################################
# Main program
##############################################

df = pd.read_csv(dpdt_file_saphir, sep="\t")
df = df.iloc[1:]
df.reset_index(inplace=True, drop=True)
df[time_name].replace("", np.nan, inplace=True)
df.dropna(subset=[time_name], inplace=True)
df[dpdt_name].replace(np.nan, 0, inplace=True)

obs_group = {}
obs_group["key"] = "dpd(supt)_w2"
obs_group["observations"] = []

obs_values = {}

for i in df.index:
    calc_unc = float(df[dpdt_name][i]) * 0.1
    if calc_unc < min_unc_value:
        calc_unc = min_unc_value
    if index_list[0] != "None":
        index_list_int = list(map(int, index_list))
        index_list_set = set(index_list_int)
        if i in index_list_set:
            obs_values["HOURS"] = float(df[time_name][i])
            obs_values["error"] = calc_unc
            obs_values["value"] = float(df[dpdt_name][i])
            obs_values_copy = obs_values.copy()
            obs_group["observations"].append(obs_values_copy)
    else:
        obs_values["HOURS"] = float(df[time_name][i])
        obs_values["error"] = calc_unc
        obs_values["value"] = float(df[dpdt_name][i])
        obs_values_copy = obs_values.copy()
        obs_group["observations"].append(obs_values_copy)

data = dict(general=[obs_group])

with open(dpdt_file_yml, "w") as file:
    yaml.dump(data, file, default_flow_style=False)

print("Finished creating dpdt obs on yaml format!")
