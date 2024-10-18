#!/usr/bin/env python
"""
Based on a scripts from Johan Sverdrup
Script to create LGR and with corresponding well completions
and update the Eclipse .DATA file
Also option for dual porosity modelling

Cecilie Otterlei, Feb 2020
"""

import argparse
import os

import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument("file_well", help="RMS file with well completions")
parser.add_argument("file_eclipse", help="Eclipse .DATA file")
parser.add_argument("file_runspec", help="LGR runspec file")
parser.add_argument("file_grid", help="LGR grid file")
parser.add_argument("file_sch", help="LGR schedule file")
parser.add_argument("size", help="LGR size")
parser.add_argument("file_dual", help="File with dual porosoty option")


def create_wellspec_dataframe(f):
    # Create pandas dataframe with WELSPECS data
    flag1 = False
    flag2 = False
    df_welspecs = None
    i = 0
    for line in f:
        if line.strip():  # Remove empty lines
            words = line.split()
            if flag2 is True:
                if words[0] == "/":
                    flag2 = False
                else:
                    words = words[:-1]  # Remove last item in list, /
                    df_welspecs.loc[i] = words
                    i += 1
            if flag1 is True:
                df_welspecs = pd.DataFrame(columns=words)
                flag1 = False
                flag2 = True
            if words[0] == "WELSPECS":
                flag1 = True
    return df_welspecs


def test_create_wellspec_dataframe():
    assert (
        create_wellspec_dataframe(["WELSPECS", "--WELL I J K", "/"]).to_csv()
        == ",--WELL,I,J,K\n"
    )
    assert (
        create_wellspec_dataframe(
            ["WELSPECS", "--WELL I J K", "name 1.0 2.0 3.0 /", "/"]
        ).to_csv()
        == ",--WELL,I,J,K\n0,name,1.0,2.0,3.0\n"
    )


def create_compdat_dataframe(f):
    # Create pandas dataframe with COMPDAT data
    flag1 = False
    flag2 = False
    df_compdat = None
    i = 0
    for line in f:
        if line.strip():  # Remove empty lines
            words = line.split()
            if flag2 is True and not words[0].startswith("-------------------------"):
                if words[0] == "/":
                    flag2 = False
                else:
                    words = words[:-1]  # Remove last item in list, /
                    df_compdat.loc[i] = words
                    i += 1
            if flag1 is True:
                df_compdat = pd.DataFrame(columns=words)
                flag1 = False
                flag2 = True
            if words[0] == "COMPDAT":
                flag1 = True
    return df_compdat


def test_create_compdat_dataframe():
    assert (
        create_compdat_dataframe(["COMPDAT", "--WELL I J K", "/"]).to_csv()
        == ",--WELL,I,J,K\n"
    )
    assert (
        create_compdat_dataframe(
            ["COMPDAT", "--WELL I J K", "name 1.0 2.0 3.0 /", "/"]
        ).to_csv()
        == ",--WELL,I,J,K\n0,name,1.0,2.0,3.0\n"
    )


def add_num_lgr(df_compdat):
    # Find number of LGRs and add column to pandas dataframe
    lgr = []
    data = []
    for i in range(len(df_compdat)):
        if [df_compdat["I"].loc[i], df_compdat["J"].loc[i]] not in lgr:
            lgr.append([df_compdat["I"].loc[i], df_compdat["J"].loc[i]])
        for j in range(len(lgr)):
            if [df_compdat["I"].loc[i], df_compdat["J"].loc[i]] == lgr[j]:
                data.append(j + 1)
    df_compdat["LGR"] = data
    return lgr


def test_add_num_lgr():
    df = create_compdat_dataframe(["COMPDAT", "--WELL I J", "name 2 3 /", "/"])
    lgr = add_num_lgr(df)
    assert df.to_csv() == ",--WELL,I,J,LGR\n0,name,2,3,1\n"
    assert lgr == [["2", "3"]]


def remove_same_layer_completions(df_compdat):
    # Remove completions if same layer for different LGRs
    list = []
    for i in range(len(df_compdat) - 1):
        if (
            df_compdat["K1"].loc[i] == df_compdat["K1"].loc[i + 1]
            and df_compdat["LGR"].loc[i] != df_compdat["LGR"].loc[i + 1]
        ):
            list.append(i + 1)
    for i in range(len(list)):
        df_compdat.drop(list[i], inplace=True)
    df_compdat.reset_index(inplace=True)


def test_remove_same_layer_completions():
    df = create_compdat_dataframe(
        ["COMPDAT", "--WELL I J K1", "name1 2 3 4 /", "name2 4 5 4 /", "/"]
    )
    lgr = add_num_lgr(df)
    remove_same_layer_completions(df)
    assert df.to_csv() == ",index,--WELL,I,J,K1,LGR\n0,0,name1,2,3,4,1\n"


def change_layers_to_int(df_compdat):
    # Change layers from string to integer type
    df_compdat["K1"] = df_compdat["K1"].astype(int)
    df_compdat["K2"] = df_compdat["K2"].astype(int)


def test_change_layers_to_int():
    import numpy

    df = create_compdat_dataframe(
        ["COMPDAT", "--WELL I J K1 K2", "name1 2 3 4 5 /", "name2 6 7 8 9 /", "/"]
    )
    add_num_lgr(df)
    change_layers_to_int(df)
    assert df["K1"].dtypes == numpy.dtype("int64")


def write_lgr_runspec_file(df_compdat, f):
    maxcls = 2000000  # The maximum number of cells in each LGR
    mcoars = 2000  # The maximum number of amalgamated coarse cells
    f.write("LGR\n")
    f.write("--MAXLGR  MAXCLS  MCOARS MAMALG MXLALG LSTACK Pressure NCHCOR\n")
    f.write(str(df_compdat["LGR"].max()) + " " + str(maxcls) + " ")
    if df_compdat["LGR"].max() > 1:
        f.write(str(mcoars) + " " + str(1) + " " + str(df_compdat["LGR"].max()) + " ")
    f.write("/\n")
    f.write("\n")
    f.write("LGRCOPY\n")


def test_write_lgr_runspec_file():
    from io import StringIO

    buffer = StringIO()
    write_lgr_runspec_file(pd.DataFrame({"LGR": [1.0]}), buffer)
    assert (
        buffer.getvalue()
        == """LGR
--MAXLGR  MAXCLS  MCOARS MAMALG MXLALG LSTACK Pressure NCHCOR
1.0 2000000 /

LGRCOPY
"""
    )


def write_lgr_config_file(lgr, df_compdat, f, ncells, size, dual):
    for i in range(len(lgr)):
        f.write("CARFIN\n")
        f.write("--Name    I1  I2   J1  J2   K1  K2   NX  NY  NZ\n")
        f.write(
            " LGR"
            + str(i + 1)
            + " "
            + str(int(lgr[i][0]) - ncells)
            + " "
            + str(int(lgr[i][0]) + ncells)
            + " "
            + str(int(lgr[i][1]) - ncells)
            + " "
            + str(int(lgr[i][1]) + ncells)
            + " "
            + str(df_compdat["K1"][df_compdat["LGR"] == i + 1].min())
            + " "
            + str(df_compdat["K2"][df_compdat["LGR"] == i + 1].max())
        )
        if size == "small":
            f.write(" 21 21 ")
        elif size == "large":
            f.write(" 77 77 ")
        if dual == 0:
            f.write(
                str(
                    df_compdat["K2"][df_compdat["LGR"] == i + 1].max()
                    - df_compdat["K1"][df_compdat["LGR"] == i + 1].min()
                    + 1
                )
                + " /\n"
            )
        elif dual == 1 or dual == 2:
            f.write(
                str(
                    (
                        df_compdat["K2"][df_compdat["LGR"] == i + 1].max()
                        - df_compdat["K1"][df_compdat["LGR"] == i + 1].min()
                        + 1
                    )
                    * 2
                )
                + " /\n"
            )
        f.write("\n")
        f.write("NXFIN\n")
        if size == "small":
            f.write("  2 4 9 4 2 /\n")
        elif size == "large":
            f.write("  2  4  4  4  4  8  8  9  8  8  4  4  4  4  2 /\n")
        f.write("\n")
        f.write("HXFIN\n")
        if size == "small":
            f.write(
                "  2*1  4*1  0.21  0.16 0.08  0.04 0.02 0.04 0.08 0.16 0.21  4*1  2*1 /\n"
            )
        elif size == "large":
            f.write(
                "  2*1 4*1 4*1 4*1 4*1 8*1 8*1 0.21 0.16"
                "  0.08 0.04 0.02 0.04 0.08 0.16 0.21  8*1 8*1 4*1 4*1 4*1 4*1 2*1 /\n"
            )
        f.write("\n")
        f.write("NYFIN\n")
        if size == "small":
            f.write("  2 4 9 4 2 /\n")
        elif size == "large":
            f.write("  2  4  4  4  4  8  8  9  8  8  4  4  4  4  2 /\n")
        f.write("\n")
        f.write("HYFIN\n")
        if size == "small":
            f.write(
                "  2*1  4*1  0.21  0.16 0.08  0.04 0.02 0.04 0.08 0.16 0.21  4*1  2*1 /\n"
            )
        elif size == "large":
            f.write(
                "  2*1 4*1 4*1 4*1 4*1 8*1 8*1 0.21 0.16"
                "  0.08 0.04 0.02 0.04 0.08 0.16 0.21  8*1 8*1 4*1 4*1 4*1 4*1 2*1 /\n"
            )
        f.write("\n")
        f.write("ENDFIN\n")
        f.write("\n")

    if df_compdat["LGR"].max() > 1:
        f.write("AMALGAM\n")
        for i in df_compdat["LGR"].unique():
            f.write("LGR" + str(i) + " ")
        f.write("/\n")
        f.write("/\n")


def test_write_lgr_config_file():
    from io import StringIO

    buffer = StringIO()
    write_lgr_config_file(
        [[1, 2]],
        pd.DataFrame({"LGR": [1.0], "K1": [1], "K2": [2]}),
        buffer,
        1,
        "small",
        False,
    )
    assert (
        buffer.getvalue()
        == """CARFIN
--Name    I1  I2   J1  J2   K1  K2   NX  NY  NZ
 LGR1 0 2 1 3 1 2 21 21 2 /

NXFIN
  2 4 9 4 2 /

HXFIN
  2*1  4*1  0.21  0.16 0.08  0.04 0.02 0.04 0.08 0.16 0.21  4*1  2*1 /

NYFIN
  2 4 9 4 2 /

HYFIN
  2*1  4*1  0.21  0.16 0.08  0.04 0.02 0.04 0.08 0.16 0.21  4*1  2*1 /

ENDFIN

"""
    )


def write_welspecl(df_welspecs, df_compdat, index, f):
    f.write("WELSPECL\n")
    f.write(
        df_welspecs.columns.values[0] + " " + df_welspecs.columns.values[1] + " LGR "
    )
    for i in range(2, len(df_welspecs.columns.values)):
        f.write(df_welspecs.columns.values[i] + " ")
    f.write("\n")
    for i in range(len(df_welspecs)):
        f.write(
            df_welspecs["--WELL"].loc[i]
            + " "
            + df_welspecs["GROUP"].loc[i]
            + " LGR"
            + str(df_compdat["LGR"].loc[0])
            + " "
            + str(index)
            + " "
            + str(index)
            + " "
            + df_welspecs["DREF"].loc[i]
            + " "
            + df_welspecs["PHASE"].loc[i]
            + " /\n"
        )
    f.write("/\n")
    f.write("\n")


def test_write_welspecl():
    from io import StringIO

    buffer = StringIO()
    write_welspecl(
        pd.DataFrame(
            {
                "--WELL": ["well"],
                "GROUP": ["group"],
                "DREF": ["dref"],
                "PHASE": ["phase"],
            }
        ),
        pd.DataFrame({"LGR": [3], "K1": [4], "K2": [7]}),
        50,
        buffer,
    )
    assert (
        buffer.getvalue()
        == """WELSPECL
--WELL GROUP LGR DREF PHASE 
well group LGR3 50 50 dref phase /
/

"""
    )


def write_compdatl(df_compdat, dual, index, f):
    f.write("COMPDATL\n")
    f.write(df_compdat.columns.values[1] + " LGR ")
    for i in range(2, len(df_compdat.columns.values) - 1):
        f.write(df_compdat.columns.values[i] + " ")
    f.write("\n")
    for i in range(len(df_compdat)):
        k = df_compdat["K1"][
            df_compdat["LGR"] == df_compdat["LGR"].loc[i]
        ].min()  # Adjust layer to within LGR
        if dual == 0 or dual == 2:
            f.write(
                df_compdat["--WELL"].loc[i]
                + " LGR"
                + str(df_compdat["LGR"].loc[i])
                + " "
                + str(index)
                + " "
                + str(index)
                + " "
                + str(df_compdat["K1"].loc[i] - k + 1)
                + " "
                + str(df_compdat["K2"].loc[i] - k + 1)
                + " "
                + df_compdat["OP/SH"].loc[i]
                + " 2* "
                + df_compdat["WBDIA"].loc[i]
                + " 1* "
                + df_compdat["SKIN"].loc[i]
                + " 1* "
                + df_compdat["DIR"].loc[i]
                + " /\n"
            )
    for i in range(len(df_compdat)):
        k = df_compdat["K1"][
            df_compdat["LGR"] == df_compdat["LGR"].loc[i]
        ].min()  # Adjust layer to within LGR
        if dual == 1 or dual == 2:
            nz = (
                df_compdat["K2"][df_compdat["LGR"] == df_compdat["LGR"].loc[i]].max()
                - df_compdat["K1"][df_compdat["LGR"] == df_compdat["LGR"].loc[i]].min()
                + 1
            )
            f.write(
                df_compdat["--WELL"].loc[i]
                + " LGR"
                + str(df_compdat["LGR"].loc[i])
                + " "
                + str(index)
                + " "
                + str(index)
                + " "
                + str(df_compdat["K1"].loc[i] - k + 1 + nz)
                + " "
                + str(df_compdat["K2"].loc[i] - k + 1 + nz)
                + " "
                + df_compdat["OP/SH"].loc[i]
                + " 2* "
                + df_compdat["WBDIA"].loc[i]
                + " 1* "
                + df_compdat["SKIN"].loc[i]
                + " 1* "
                + df_compdat["DIR"].loc[i]
                + " /\n"
            )
    f.write("/\n")


def test_write_compdatl():
    from io import StringIO

    buffer = StringIO()
    write_compdatl(
        pd.DataFrame(
            {
                "index": [0],
                "--WELL": ["well"],
                "LGR": ["name"],
                "K1": [2],
                "K2": [3],
                "OP/SH": ["1.0"],
                "WBDIA": ["wbdia"],
                "SKIN": ["skin"],
                "DIR": ["dir"],
            }
        ),
        False,
        50,
        buffer,
    )
    assert (
        buffer.getvalue()
        == """COMPDATL
--WELL LGR LGR K1 K2 OP/SH WBDIA SKIN 
well LGRname 50 50 1 2 1.0 2* wbdia 1* skin 1* dir /
/
"""
    )


def run(file_well, file_eclipse, file_runspec, file_grid, file_sch, size, file_dual):
    if size == "small":
        index = 11
        ncells = 2
    elif size == "large":
        index = 39
        ncells = 7

    # -------------------------------------------------

    # Dual porosity modelling option
    # 0 = SP, 1 = DP, 2 = DPDK
    f = open(file_dual)
    dual = int(f.read(1))
    f.close()

    # -------------------------------------------------

    f = open(file_well)
    df_welspecs = create_wellspec_dataframe(f)
    f.close()

    f = open(file_well)
    df_compdat = create_compdat_dataframe(f)
    f.close()

    add_num_lgr(df_compdat)
    lgr = remove_same_layer_completions(df_compdat)
    change_layers_to_int(df_compdat)

    # -------------------------------------------------

    f = open(file_runspec, "w")
    write_lgr_runspec_file(df_compdat, f)
    f.close()

    # LGR grid file
    f = open(file_grid, "w")
    write_lgr_config_file(lgr, df_compdat, f, ncells, size, dual)
    f.close()

    # LGR schedule file
    f = open(file_sch, "w")

    f2 = open(file_well)

    flag = False
    for line in f2:
        if line.strip():  # Remove empty lines
            words = line.split()
            if flag is True:
                if words[0] == "/":
                    f.write(line)
                    flag = False
                else:
                    f.write(line)
            if words[0] == "GRUPTREE":
                f.write(line)
                flag = True
    f.write("\n")

    f2.close()

    write_welspecl(df_welspecs, df_compdat, index, f)
    write_compdatl(df_compdat, dual, index, f)
    f.close()

    # -------------------------------------------------

    # Update Eclipse .DATA file
    f = open(file_eclipse)
    f2 = open(file_eclipse + ".tmp", "w")
    for line in f:
        if line.startswith("GRID") and not line.startswith("GRIDFILE"):
            f2.write("INCLUDE\n")
            f2.write(" '../include/runspec/" + file_runspec.split("/")[-1] + "' /\n")
            f2.write("\n")
        if line.startswith("EDIT"):
            f2.write("INCLUDE\n")
            f2.write(" '../include/grid/" + file_grid.split("/")[-1] + "' /\n")
            f2.write("\n")
        if ".sch" in line:
            sch = line.split()[0].split("/")[-1].replace("'", "")
        f2.write(line)
    f2.close()
    f.close()
    os.rename(file_eclipse + ".tmp", file_eclipse)

    # Update Eclipse schedule file
    sch2 = file_sch.split("/")
    dir = file_sch.rsplit("/", 1)[0]
    f = open(dir + "/" + sch)
    f2 = open(dir + "/" + sch + ".tmp", "w")
    for line in f:
        if "schedule" in line:
            sch3 = line.split()[0].split("/")[-1].replace("'", "")
            line = line.replace(sch3, sch2[-1])
        f2.write(line)
    f2.close()
    f.close()
    os.rename(dir + "/" + sch + ".tmp", dir + "/" + sch)


if __name__ == "__main__":
    args = parser.parse_args()
    run(
        args.file_well,
        args.file_eclipse,
        args.file_runspec,
        args.file_grid,
        args.file_sch,
        args.size,
        args.file_dual,
    )
