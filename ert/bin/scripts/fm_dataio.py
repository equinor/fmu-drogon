#!/usr/bin/env python
# Take existing maps on /share/tmp/maps and process through fmu-dataio
# This is a TMP solution

from pathlib import Path

import xtgeo


def get_parser():
    pass


def main(runpath):
    mfolder = Path(runpath) / "share/tmp/maps"

    for mapfile in mfolder.glob("*.gri"):
        map_ = xtgeo.surface_from_file(mapfile)
        print(map_.name)


if __name__ == "__main__":
    """Parse command line options and start calculation"""
    parser = get_parser()
    args = parser.parse_args()

    runpath = args.runpath

    main(runpath)

    print("Done")
