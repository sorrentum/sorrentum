#!/usr/bin/env python
r"""
Run a single config through a run_config()

# Use example:
> run_configs_stub.py \
    --dst_dir nlp/test_results \
    --experiment_builder "dataflow.backtest.master_backtest.run_experiment" \
    --config_builder "nlp.build_configs.build_PTask1088_configs()" \
    --num_threads 2

Import as:

import dataflow.backtest.run_config_stub as dtfmruexst
"""


import argparse
import importlib
import logging
import re
from typing import cast

import core.config as cconfig
import helpers.hdbg as hdbg
import helpers.hparser as hparser

_LOG = logging.getLogger(__name__)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    # Options that `run_config_list.py` propagates here.
    parser.add_argument(
        "--experiment_builder",
        action="store",
        required=True,
        help="E.g., 'dataflow.backtest.master_backtest.run_experiment'",
    )
    parser.add_argument(
        "--config_builder",
        action="store",
        required=True,
        help="E.g., 'nlp.build_configs.build_PTask1088_configs()'",
    )
    parser.add_argument(
        "--dst_dir",
        action="store",
        required=True,
        help="Destination dir for the entire experiment list, not for this"
        " specific single experiment",
    )
    # Select which config to execute.
    parser.add_argument(
        "--config_idx",
        action="store",
        required=True,
        help="Index of the config generated by `config_builder` to run",
    )
    parser: argparse.ArgumentParser = hparser.add_verbosity_arg(parser)
    return parser


# A command line like:
# ```
# > /app/amp/dataflow/backtest/run_config_list.py \
#   --experiment_builder 'amp.dataflow.backtest.master_backtest.run_tiled_backtest' \
#   --config_builder 'dataflow_lime.system.E8.E8_tile_config_builders.build_E8e_tile_config_list("eg_v2_0-top1.5T.2020-01-01_2020-03-01")' --dst_dir /app/dataflow_lime/system/E8/test/outcomes/Test_E8e_TiledBacktest1.test_top1_JanFeb2020/tmp.scratch/run_model \
#   --aws_profile am \
#   --clean_dst_dir --no_confirm --num_threads serial \
#   -v DEBUG \
# ```
# get expanded into a series of command like:
# ```
# /app/amp/dataflow/backtest/run_config_stub.py \
#   --experiment_builder 'amp.dataflow.backtest.master_backtest.run_tiled_backtest' \
#   --config_builder 'dataflow_lime.system.E8.E8_tile_config_builders.build_E8e_tile_config_list("eg_v2_0-top1.5T.2020-01-01_2020-03-01")' \
#   --config_idx 0 \
#   --dst_dir /app/dataflow_lime/system/E8/test/outcomes/Test_E8e_TiledBacktest1.test_top1_JanFeb2020/tmp.scratch/run_model \
#   -v INFO
# ```


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    report_memory_usage = True
    # report_memory_usage = True
    hdbg.init_logger(
        verbosity=args.log_level, report_memory_usage=report_memory_usage
    )
    # 1) Get the actual config to execute using the command line parameters.
    config_idx = int(args.config_idx)
    experiment_list_params = {
        "experiment_builder": args.experiment_builder,
        "config_builder": args.config_builder,
        "dst_dir": args.dst_dir,
    }
    config_list = cconfig.get_config_from_experiment_list_params(
        config_idx, experiment_list_params
    )
    hdbg.dassert_isinstance(config_list, cconfig.ConfigList)
    _LOG.info("config_list=\n%s", config_list)
    # 2) Execute the `experiment_builder` passing the config to execute.
    experiment_builder = args.experiment_builder
    # E.g., `amp.dataflow.backtest.master_backtest.run_tiled_backtest`.
    _LOG.info("experiment_builder='%s'", experiment_builder)
    hdbg.dassert(
        not experiment_builder.endswith("()"),
        "Invalid experiment_builder='%s'",
        experiment_builder,
    )
    experiment_builder = f"{experiment_builder}(config_list)"
    # TODO(gp): Use hintrospection.get_function_from_string().
    m = re.match(r"^(\S+)\.(\S+)\((.*)\)$", experiment_builder)
    hdbg.dassert(m, "experiment_builder='%s'", experiment_builder)
    m = cast(re.Match, m)
    import_, function, args = m.groups()
    _LOG.debug("import=%s", import_)
    _LOG.debug("function=%s", function)
    _LOG.debug("args=%s", args)
    # Import the needed module.
    imp = importlib.import_module(import_)
    # Force the linter not to remove this import which is needed in the following
    # eval.
    _ = imp
    python_code = "imp.%s(%s)" % (function, args)
    # E.g., `imp.build_E8e_tile_config_list("eg_v2_0-top1.5T.2020-01-01_2020-03-01")`
    _LOG.debug("executing '%s'", python_code)
    exec(python_code)  # pylint: disable=exec-used


if __name__ == "__main__":
    _main(_parse())