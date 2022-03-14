#!/usr/bin/env python
r"""
Run a single config through a run_config()

# Use example:
> run_configs_stub.py \
    --dst_dir nlp/test_results \
    --experiment_builder "dataflow_model.master_experiment.run_experiment" \
    --config_builder "nlp.build_configs.build_PTask1088_configs()" \
    --num_threads 2

Import as:

import dataflow.model.run_experiment_stub as dtfmruexst
"""


# TODO(gp): -> run_config_stub.py

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
    # Options that `run_experiment.py` propagates here.
    parser.add_argument(
        "--experiment_builder",
        action="store",
        required=True,
        help="E.g., 'dataflow_model.master_experiment.run_experiment'",
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


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    report_memory_usage = False
    # report_memory_usage = True
    hdbg.init_logger(
        verbosity=args.log_level, report_memory_usage=report_memory_usage
    )
    # Get the actual config to execute using the command line parameters.
    config_idx = int(args.config_idx)
    experiment_list_params = {
        "experiment_builder": args.experiment_builder,
        "config_builder": args.config_builder,
        "dst_dir": args.dst_dir,
    }
    config = cconfig.get_config_from_experiment_list_params(
        config_idx, experiment_list_params
    )
    _LOG.info("config=\n%s", config)
    # Execute the `experiment_builder.`
    # E.g., `dataflow_model.master_experiment.run_experiment`
    builder = args.experiment_builder
    _LOG.info("experiment_builder='%s'", builder)
    hdbg.dassert(
        not builder.endswith("()"), "Invalid experiment_builder='%s'", builder
    )
    builder = f"{builder}(config)"
    # TODO(gp): Use hintrospection.get_function_from_string().
    m = re.match(r"^(\S+)\.(\S+)\((.*)\)$", builder)
    hdbg.dassert(m, "builder='%s'", builder)
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
    _LOG.debug("executing '%s'", python_code)
    exec(python_code)  # pylint: disable=exec-used


if __name__ == "__main__":
    _main(_parse())