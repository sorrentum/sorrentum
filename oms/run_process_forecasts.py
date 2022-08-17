#!/usr/bin/env python

"""
Execute `process_forecasts.py` over a tiled backtest.
"""

import argparse
import asyncio
import datetime
import logging
from typing import Any, Dict

import helpers.hasyncio as hasynci
import helpers.hdbg as hdbg
import helpers.hparser as hparser
import oms.process_forecasts_example as oprfoexa
import oms.tiled_process_forecasts as otiprfor

_LOG = logging.getLogger(__name__)

# #############################################################################


# TODO(Paul): Specify
#   - backtest file name
#   - asset_id_col
#   - log_dir
def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # TODO(Paul): Consider making these optional or else pointing to config
    #   files.
    parser.add_argument(
        "--backtest_file_name",
        action="store",
        help="Path to the parquet tiles containing the forecasts generated by the backtest",
    )
    parser.add_argument(
        "--asset_id_col", action="store", help="Name of the asset id column"
    )
    parser.add_argument(
        "--log_dir", action="store", help="Directory for logging results"
    )
    hparser.add_verbosity_arg(parser)
    return parser


def get_market_data_tile_dict() -> Dict[str, Any]:
    dict_ = {
        "file_name": "/cache/tiled.bar_data.all.2010_2022.20220204",
        "price_col": "close",
        "knowledge_datetime_col": "end_time",
        "start_time_col": "start_time",
        "end_time_col": "end_time",
    }
    return config


def get_backtest_tile_dict() -> Dict[str, Any]:
    dict_ = {
        "file_name": "",
        "asset_id_col": "",
        "start_date": datetime.date(2020, 12, 1),
        "end_date": datetime.date(2020, 12, 31),
        "prediction_col": "prediction",
        "volatility_col": "vwap.ret_0.vol",
        "spread_col": "pct_bar_spread",
    }
    return dict_


async def _run_coro(
    event_loop: asyncio.AbstractEventLoop,
    market_data_tile_dict: Dict[str, Any],
    backtest_tile_dict: Dict[str, Any],
    process_forecasts_dict: Dict[str, Any],
) -> None:
    await otiprfor.run_tiled_process_forecasts(
        event_loop,
        market_data_tile_dict,
        backtest_tile_dict,
        process_forecasts_dict,
    )


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    #
    market_data_tile_dict = get_market_data_tile_dict()
    _LOG.info("market_data_tile_dict=\n%s", str(market_data_tile_dict))
    #
    backtest_tile_dict = get_backtest_tile_dict()
    # TODO(Paul): Warn if we are overriding.
    backtest_tile_dict["file_name"] = args.backtest_file_name
    backtest_tile_dict["asset_id_col"] = args.asset_id_col
    _LOG.info("backtest_tile_dict=\n%s", str(backtest_tile_dict))
    #
    process_forecasts_dict = oprfoexa.get_process_forecasts_dict_example1()
    process_forecasts_dict["log_dir"] = args.log_dir
    _LOG.info("process_forecasts_dict=\n%s", str(process_forecasts_dict))
    #
    with hasynci.solipsism_context() as event_loop:
        hasynci.run(
            _run_coro(
                event_loop,
                market_data_tile_dict,
                backtest_tile_dict,
                process_forecasts_dict,
            ),
            event_loop,
        )


if __name__ == "__main__":
    _main(_parse())
