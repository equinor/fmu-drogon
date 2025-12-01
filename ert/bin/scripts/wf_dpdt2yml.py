#!/usr/bin/env python
"""create dpdt gen obs file on yml format"""

import argparse

import numpy as np
import pandas as pd
import yaml

UNC = 0.1
MIN_UNC_VALUE = 0.05
TIME_NAME = "dTime"
DPDT_NAME = "Pressure derivative"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("dpdt_file_saphir", help="Saphir pressure derivative file")
    parser.add_argument("dpdt_file_yml", help="Pressure derivative yaml file")
    parser.add_argument(
        "index_list",
        nargs="+",
        help="Index list for general observation, None, or the numbers in the list, "
        "f.ex. 0 10",
    )
    return parser.parse_args()


def load_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, sep="\t").iloc[1:].reset_index(drop=True)
    df[TIME_NAME] = df[TIME_NAME].replace("", np.nan)
    df = df.dropna(subset=[TIME_NAME])
    df[DPDT_NAME] = df[DPDT_NAME].replace(np.nan, 0)
    return df


def create_observations(
    df: pd.DataFrame, index_list: list[str]
) -> list[dict[str, float]]:
    if index_list[0] != "None":
        index_list_set = set(map(int, index_list))
        df = df[df.index.isin(index_list_set)]
    observations = []
    for _, row in df.iterrows():
        calc_unc = max(float(row[DPDT_NAME]) * UNC, MIN_UNC_VALUE)

        observations.append(
            {
                "HOURS": float(row[TIME_NAME]),
                "error": calc_unc,
                "value": float(row[DPDT_NAME]),
            }
        )

    return observations


def main() -> None:
    args = parse_args()
    df = load_data(args.dpdt_file_saphir)
    observations = create_observations(df, args.index_list)

    data = {
        "general": [
            {
                "key": "dpd(supt)_w2",
                "observations": observations,
            }
        ]
    }

    with open(args.dpdt_file_yml, "w") as file:
        yaml.dump(data, file, default_flow_style=False)

    print("Finished creating dpdt obs on yaml format!")


if __name__ == "__main__":
    main()
