#!/usr/bin/env python
"""
Convert data from csv to daily PQ files.

# Example:
> im_v2/common/data/transform/csv_to_pq.py \
    --src-dir test/ccxt_test \
    --dst-dir test_pq

Import as:

import im_v2.common.data.transform.csv_to_pq as imvcdtctpq
"""

import argparse
import logging
import os
from typing import List, Tuple

import helpers.csv_helpers as hcsv
import helpers.dbg as hdbg
import helpers.io_ as hio
import helpers.parser as hparser

_LOG = logging.getLogger(__name__)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--src_dir",
        action="store",
        type=str,
        required=True,
        help="Location of input CSV to convert to PQ format",
    )
    parser.add_argument(
        "--dst_dir",
        action="store",
        type=str,
        required=True,
        help="Destination dir where to save converted PQ files",
    )
    parser.add_argument(
        "--num_threads",
        action="store",
        default="serial",
        help="Number of threads to execute in parallel. -1 is treated as max threads.",
    )
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Skip files that have already been converted",
    )
    parser.add_argument(
        "--dry_run", action="store_true", help="Print workload without executing"
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _get_csv_to_pq_file_names(
    src_dir: str, dst_dir: str, incremental: bool
) -> List[Tuple[str, str]]:
    """
    Find all the CSV files in `src_dir` to transform and the corresponding
    destination PQ files.

    :param incremental: if True, skip CSV files for which the corresponding PQ file already exists
    :return: list of tuples (csv_file, pq_file)
    """
    hdbg.dassert_ne(len(os.listdir(src_dir)), 0, "No files inside '%s'", src_dir)
    # Find all the CSV files to convert.
    csv_ext, csv_gz_ext = ".csv", ".csv.gz"
    csv_files = []
    for f in os.listdir(src_dir):
        if f.endswith(csv_ext):
            filename = f[: -len(csv_ext)]
        elif f.endswith(csv_gz_ext):
            filename = f[: -len(csv_gz_ext)]
        else:
            _LOG.warning(f"Encountered non CSV file '{f}'")
            continue
        pq_path = os.path.join(dst_dir, f"{filename}.parquet")
        # Skip CSV files that do not need to be converted.
        if incremental and os.path.exists(pq_path):
            _LOG.warning(
                "Skipping the conversion of CSV file '%s' since '%s' already exists",
                filename,
                filename,
            )
        else:
            csv_path = os.path.join(src_dir, f)
            csv_files.append((csv_path, pq_path))
    return csv_files


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    hio.create_dir(args.dst_dir, args.incremental)
    files = _get_csv_to_pq_file_names(
        args.src_dir, args.dst_dir, args.incremental
    )
    # Transform CSV files.
    for csv_full_path, pq_full_path in files:
        hcsv.convert_csv_to_pq(csv_full_path, pq_full_path)


if __name__ == "__main__":
    _main(_parse())
