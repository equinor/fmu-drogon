#!/usr/bin/env python
#
# Make xsection plots of planned wells
#
# jriv, rnyb, June 2021
# alifb June 2024

import argparse
import pathlib
import re

import xtgeo
from xtgeoviz import plot

DESCRIPTION = """ Create a png file with cross section of well path and surfaces and
optional grid properties. Input argument is RUNPATH.

Hardcoded:
Location (relative to RUNPATH) and name of data (surfaces, wells and polygons).
Data must be located in share/results/ wells, maps, polygons and grids folders.
Name of output files (written to share/results/images folder, created if missing)
Optional input:
List of well names (will then overwrite hardcoded list)
"""


# ------- User settings --------------------------------

DEFAULT_DEPTH_INTERVAL = [1550, 1700]

HORIZ_FOLDER = "share/results/maps"

HORIZ = [
    "topvolantis--ds_extract_postprocess.gri",
    "toptherys--ds_extract_postprocess.gri",
    "topvolon--ds_extract_postprocess.gri",
    "basevolantis--ds_extract_postprocess.gri",
]
HNAMES = ["Valysar", "Therys", "Volon", "Base"]

WELL_FOLDER = "share/results/wells"
W_LIST = ["MLW_OP5_Y1.rmswell", "MLW_OP5_Y2.rmswell"]  # list of .rmswell files

POLY = "share/results/polygons/toptherys--gl_faultlines_extract_postprocess.pol"

GRID = "share/results/grids/eclgrid.roff"

IMAGE_FOLDER = "share/results/images"

# Tuple of property name, file path (ROFF file) and plot range
# (ignore to use auto range)
GRID_PROPS = [
    ("SOIL_20200701", "share/results/grids/eclgrid--soil--20200701.roff", [0, 1]),
    ("SGAS_20200701", "share/results/grids/eclgrid--sgas--20200701.roff", [0, 1]),
    ("PRESSURE_20200701", "share/results/grids/eclgrid--pressure--20200701.roff"),
    ("FIPNUM", "share/results/grids/eclgrid--fipnum.roff"),
]


# -----------------------------------------------------
def calculate_optimum_zrange(well, zonelog, z_extension=100):
    if zonelog not in well.dataframe.columns:
        return DEFAULT_DEPTH_INTERVAL
    df = well.dataframe.dropna(subset=[zonelog])
    if df.empty:
        return DEFAULT_DEPTH_INTERVAL
    min_zone = int(df[zonelog].min())
    max_zone = int(df[zonelog].max()) + 1
    df = df[df[zonelog].isin(range(min_zone, max_zone))]
    if df.empty:
        return DEFAULT_DEPTH_INTERVAL
    default_min, default_max = DEFAULT_DEPTH_INTERVAL
    zrange_min = df["Z_TVDSS"].min() - z_extension
    zrange_max = df["Z_TVDSS"].max() + z_extension
    return [max(zrange_min, default_min), min(zrange_max, default_max)]


def get_parser():
    """Construct a parser for command line and for command line help"""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        "runpath", help="ERT runpath where data is located, typically <RUNPATH>"
    )
    parser.add_argument("--wells", nargs="+", default=W_LIST)
    return parser


def get_surfaces(runpath):
    surfaces = []
    for ino, horiz in enumerate(HORIZ):
        path = runpath / HORIZ_FOLDER / horiz
        s = xtgeo.surface_from_file(path)
        s.name = HNAMES[ino]
        surfaces.append(s)
    return surfaces


def get_wells(runpath, well_list):
    wells = []
    for well in well_list:
        path = runpath / WELL_FOLDER / well
        w = xtgeo.well_from_file(path)
        wells.append(w)
    return wells


def get_realization(runpath):
    r = re.search(r"(?<=realization-)\d+", str(runpath))
    return r.group(0) if r else "unknown"


def create_plot(
    surfs, wells, real, grid, polygons, runpath, prop=None, prop_range=None
):
    image_folder = runpath / IMAGE_FOLDER
    image_folder.mkdir(parents=True, exist_ok=True)
    for well in wells:
        min_depth, max_depth = calculate_optimum_zrange(well, "zonelog")
        myplot = plot.XSection(
            zmin=min_depth,
            zmax=max_depth,
            well=well,
            surfaces=surfs,
            sampling=10,
            nextend=2,
            zonelogshift=0,
            outline=polygons,
            # colormap="xtgeo",
            grid=grid,
            gridproperty=prop,
        )

        myplot.colormap_facies = "xtgeo"
        myplot.colormap_perf = "xtgeo"
        myplot.colormap_zonelog = "random40"

        myplot.has_legend = True
        myplot.legendsize = 6

        myplot.canvas(
            title=f"{well.name}{' - ' + prop.name if prop else ''}",
            subtitle=f"Cross section, realization {real}",
        )

        if prop:
            # myplot._colorlegend_grid = True  # Show legend for 3D grid property
            if prop_range:
                vmin, vmax = prop_range
            else:
                # Use the full property range, so that the sampled -999 undefined
                # value in a section does not stretch the colour scale
                vmin, vmax = prop.values.min(), prop.values.max()
            myplot.plot_grid3d(
                vmin=vmin,
                vmax=vmax,
                colormap="rainbow",
                alpha=0.9,
                zinc=0.5,
                interpolation="nearest",
            )

            out = image_folder / f"{well.name}_{prop.name}_xsection.png"
        else:
            myplot.plot_surfaces(
                fill=True,
                axisname="main",
                gridlines=True,
                legend=True,
                colormap="random40",
            )
            out = image_folder / f"{well.name}_xsection.png"

        myplot.has_legend = False
        myplot.plot_well(
            zonelogname="zonelog",
            perflogname="Perf_log",
        )

        myplot.plot_surfaces(
            fill=False, axisname="lines", legend=False, linewidth=0.5, onecolor="black"
        )

        myplot.plot_map()
        myplot.plot_wellmap()

        print("Creating file:", out)
        myplot.savefig(out)


def main():
    """Parse command line options and start calculation"""
    parser = get_parser()
    args = parser.parse_args()

    runpath = pathlib.Path(args.runpath)

    wells = get_wells(runpath, args.wells)
    surfs = get_surfaces(runpath)
    real = get_realization(runpath)
    grd = xtgeo.grid_from_file(runpath / GRID)
    polygons = xtgeo.polygons_from_file(runpath / POLY)

    create_plot(surfs, wells, real, grd, polygons, runpath)
    for name, path, *plot_range in GRID_PROPS:
        if len(plot_range) == 0:
            plot_range = None
        else:
            plot_range = plot_range[0]
        prop = xtgeo.gridproperty_from_file(
            runpath / path,
            grid=grd,
            name=name,
        )
        create_plot(surfs, wells, real, grd, polygons, runpath, prop, plot_range)

    print("Done")


if __name__ == "__main__":
    main()
