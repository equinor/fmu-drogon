#!/usr/bin/env python
# Create misfit files

import os
from collections import defaultdict

import numpy as np
from pandas import DataFrame

from ert import ErtScript
from ert.data import MeasuredData


class ExportMisfit(ErtScript):
    def get_misfit(self):
        # Loads all misfit data for a given ensemble
        # Extracted from:
        # https://github.com/equinor/ert/blob/a83cbf2a0787d8b7fd1ff3f935f480a58285d316/src/ert/libres_facade.py#L241
        # to avoid accessing facade directly

        measured_data = MeasuredData(
            self.ensemble,
            keys=sorted(list(self.ensemble.experiment.observations.keys())),
        )
        misfit = DataFrame()
        for name in measured_data.data.columns.unique(0):
            df = (
                (
                    measured_data.data[name].loc["OBS"]
                    - measured_data.get_simulated_data()[name]
                )
                / measured_data.data[name].loc["STD"]
            ) ** 2
            misfit[f"MISFIT:{name}"] = df.sum(axis=1)
            misfit[f"COUNT:{name}"] = df.shape[1]
        misfit["MISFIT:TOTAL"] = misfit.sum(axis=1)
        misfit.index.name = "Realization"
        return misfit

    def run(self, output_path, source_case=None):
        output_path = output_path + "/" + self.ensemble.name
        if not os.path.isdir(output_path):
            os.makedirs(output_path, exist_ok=True)

        misfit = self.get_misfit()

        obs = self.ensemble.experiment.observations

        # Poor man solution for mapping between observation key to data key
        dict_obs_data_key = defaultdict(list)
        for key in obs:
            if "name" in obs[key].coords:
                data_key = obs[key].coords["name"].values[0]
            else:
                data_key = key
            dict_obs_data_key[data_key].append(key)
        dict_obs_data_key = dict(sorted(dict_obs_data_key.items()))

        # Create data frames for storage of data
        df_per_real_obs = DataFrame(index=misfit.index)
        for key in dict_obs_data_key:
            df_per_real_obs[key] = np.sqrt(
                misfit[["MISFIT:" + x for x in dict_obs_data_key[key]]].sum(axis=1)
                / misfit[["COUNT:" + x for x in dict_obs_data_key[key]]].sum(axis=1)
            )
        df_per_real_obs.to_csv(
            os.path.join(output_path, "misfit_one_value_per_real_per_well.csv"), sep=","
        )

        df_per_obs = DataFrame(index=range(1))
        df_per_obs.index.name = "Ensemble"
        for col in df_per_real_obs.columns:
            df_per_obs[col] = df_per_real_obs[col].mean()
        df_per_obs.to_csv(
            os.path.join(output_path, "misfit_one_value_per_well.csv"), sep=","
        )

        df_per_real_sum = misfit[["MISFIT:TOTAL"]].rename(
            columns={"MISFIT:TOTAL": "Total misfit"}
        )
        df_per_real_sum.to_csv(
            os.path.join(output_path, "misfit_per_real_SUMS.csv"), sep=","
        )

        df_per_real_norm = DataFrame()
        df_per_real_norm["Norm misfit"] = np.sqrt(
            misfit[["MISFIT:" + x for x in obs.keys()]].sum(axis=1)
            / misfit[["COUNT:" + x for x in obs.keys()]].sum(axis=1)
        )
        df_per_real_norm.to_csv(
            os.path.join(output_path, "misfit_per_real_NORM.csv"), sep=","
        )

        print(f"Output saved to: {output_path}")
