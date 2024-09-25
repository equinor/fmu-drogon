#!/usr/bin/env python
"""extract_tracer_breakthrough_time"""

import argparse
import logging
import pathlib

import pandas as pd
from res2df import ResdataFiles, summary

DESCRIPTION = """
Extract tracer breakthrough time from eclipse simulation,
writing integer values to file to be fed into GEN_DATA in ERT.

The well and tracer list *must* be aligned with the observation file
(same wells&tracers, and in same order, looping over wells first.)
"""

logger = logging.getLogger(__file__)

W_LIST = ["A1", "A2", "A3", "A4"]
T_LIST = ["WTPTWT1", "WTPTWT2"]


def get_parser():
    """Construct a parser for command line and for command line help"""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("ECLNAME", help="Eclipse path + rootname, typically <ECLBASE>")
    parser.add_argument(
        "output", help="Output file that will contain breakthrough times"
    )
    parser.add_argument("--wells", nargs="+", default=W_LIST)
    parser.add_argument("--tracers", nargs="+", default=T_LIST)
    parser.add_argument(
        "--max_bt_time",
        type=int,
        default=912,
        help="Breakthrough time used when there is no breakthrough. Unit days.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    return parser


def extract_tracer_breakthrough_time(
    summary_df, output, wells, tracers, max_bt_time=9999
):
    """Determine tracer breakthrough time for a combination of wells and tracers,
    and write results to a text file.

    The text file will only contain one value pr. line. Loops over wells first.

    """

    assert isinstance(summary_df.index, pd.DatetimeIndex)

    pathlib.Path(output).parent.mkdir(parents=True, exist_ok=True)

    file = open(output, "w")
    for tracer in tracers:
        for well in wells:
            tracer_rows = summary_df[tracer + ":" + well] > 0.000001
            if tracer_rows.any():
                tbt = summary_df[summary_df[tracer + ":" + well] > 0.000001].index[0]
                diff = tbt - summary_df.index.min()
                file.write(str(int(diff.days)) + "\n")
                msg = "Tracer {}, well {}, difference: {} days".format(
                    tracer, well, diff.days
                )
                logger.info(msg)
                if diff.days > max_bt_time:
                    msg = (
                        "Breakthrough time {} is larger than the value "
                        "used when there is no breakthrough ({})"
                    ).format(diff.days, max_bt_time)
                    logger.error(msg)
            else:
                msg = "No breakthrough for tracer {} in well {}, using {} days".format(
                    tracer, well, max_bt_time
                )
                logger.warning(msg)
                file.write("{}\n".format(max_bt_time))

    file.close()


def main():
    """Parse command line options and start calculation"""
    parser = get_parser()
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.INFO)

    eclfiles = ResdataFiles(args.ECLNAME + ".DATA")
    summary_df = summary.df(eclfiles)

    extract_tracer_breakthrough_time(
        summary_df=summary_df,
        output=args.output,
        wells=args.wells,
        tracers=args.tracers,
        max_bt_time=args.max_bt_time,
    )
    logger.info("Done")


if __name__ == "__main__":
    main()


def test_breakthrough(tmpdir):
    """Mock a simple dataframe and test the breatkthrough time extraction"""
    tmpdir.chdir()
    summary_df = pd.DataFrame(
        columns=["DATE", "WTPTWT2:A-1"],
        data=[["2020-01-01", 0], ["2020-02-01", 0], ["2020-03-01", 0.001]],
    )
    summary_df["DATE"] = pd.to_datetime(summary_df["DATE"])
    summary_df.set_index("DATE", inplace=True)
    print(summary_df.index.dtype)
    print(summary_df)
    print(summary_df.dtypes)
    extract_tracer_breakthrough_time(
        summary_df, "foo.txt", wells=["A-1"], tracers=["WTPTWT2"]
    )
    print(open("foo.txt").readlines())
    assert open("foo.txt").readlines() == ["60\n"]
