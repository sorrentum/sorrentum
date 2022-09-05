"""
Import as:

import oms.call_optimizer as ocalopti
"""

import logging
import os
from typing import Any, List

import invoke
import pandas as pd

import core.config as cconfig
import core.finance as cofinanc
import helpers.hdbg as hdbg
import helpers.hgit as hgit
import helpers.hio as hio
import helpers.hpandas as hpandas
import helpers.hpickle as hpickle
import helpers.hsystem as hsystem

_LOG = logging.getLogger(__name__)


def check_notional_limits(broker: Any, target_trades: Any):
    return target_trades


def _check_notional_limit(broker: Any, order: Any):
    """
    Check if the order matches the minimum quantity for the asset.

    The functions check both the flat amount of the asset and the total
    cost of the asset in the order. If the order amount does not match,
    the order is changed to be slightly above the minimal amount.

    :param order: order to be submitted
    """
    asset_limits = broker.minimal_order_limits[order.asset_id]
    min_amount = asset_limits["min_amount"]
    if abs(order.diff_num_shares) < min_amount:
        if order.diff_num_shares < 0:
            min_amount = -min_amount
        _LOG.warning(
            "Order: %s\nAmount of asset in order is below minimal: %s. Setting to min amount: %s",
            str(order),
            order.diff_num_shares,
            min_amount,
        )
        order.diff_num_shares = min_amount
    # Check if the order is not below minimal cost.
    #
    # Estimate the total cost of the order based on the low market price.
    #  Note: low price is chosen to account for possible price spikes.
    low_price = broker.get_low_market_price(order.asset_id)
    total_cost = low_price * abs(order.diff_num_shares)
    min_cost = asset_limits["min_cost"]
    if total_cost <= min_cost:
        # Set amount based on minimal notional price.
        required_amount = round(min_cost * 3 / low_price, 2)
        if order.diff_num_shares < 0:
            required_amount = -required_amount
        _LOG.warning(
            "Order: %s\nAmount of asset in order is below minimal base: %s. \
                Setting to following amount based on notional limit: %s",
            str(order),
            min_cost,
            required_amount,
        )
        # Change number of shares to minimal amount.
        order.diff_num_shares = required_amount
    return order


def compute_target_cc_positions_in_cash(
    df: pd.DataFrame,
    *,
    style: str,
    broker: Any,
    **kwargs,
) -> pd.DataFrame:
    """
    Compute target trades from holdings (dollar-valued) and predictions.

    This is a stand-in for optimization. This function does not have access to
    prices and so does not perform any conversions to or from shares. It also
    needs to be told the id associated with cash.

    :param df: a dataframe with current positions (in dollars) and predictions
    :return: a dataframe with target positions and trades
        (denominated in dollars)
    """
    # Sanity-check the dataframe.
    hdbg.dassert_isinstance(df, pd.DataFrame)
    hdbg.dassert(not df.empty)
    hdbg.dassert_is_subset(
        ["asset_id", "prediction", "volatility", "position"], df.columns
    )
    hdbg.dassert_not_in("target_position", df.columns)
    hdbg.dassert_not_in("target_trade", df.columns)
    #
    hdbg.dassert(not df["prediction"].isna().any())
    hdbg.dassert(not df["volatility"].isna().any())
    hdbg.dassert(not df["position"].isna().any())
    #
    df = df.set_index("asset_id")
    hdbg.dassert(not df.index.has_duplicates)
    #
    predictions = df["prediction"].rename(0).to_frame().T
    volatility = df["volatility"].rename(0).to_frame().T
    if style == "cross_sectional":
        target_positions = cofinanc.compute_target_positions_cross_sectionally(
            predictions,
            volatility,
            **kwargs,
        )
    elif style == "longitudinal":
        target_positions = cofinanc.compute_target_positions_longitudinally(
            predictions,
            volatility,
            spread=None,
            **kwargs,
        )
    else:
        raise ValueError("Unsupported `style`=%s", style)
    hdbg.dassert_eq(target_positions.shape[0], 1)
    target_positions = pd.Series(
        target_positions.values[0],
        index=target_positions.columns,
        name="target_position",
        dtype="float",
    )
    _LOG.debug(
        "`target_positions`=\n%s",
        hpandas.df_to_str(
            target_positions, print_dtypes=True, print_shape_info=True
        ),
    )
    # These positions are expressed in dollars.
    current_positions = df["position"]
    _LOG.debug(
        "`current_positions`=\n%s",
        hpandas.df_to_str(
            current_positions, print_dtypes=True, print_shape_info=True
        ),
    )
    target_trades = target_positions - current_positions
    # Check the target trades for matching the minimal notional limit.
    df["target_position"] = target_positions
    df["target_notional_trade"] = target_trades
    return df


def compute_target_positions_in_cash(
    df: pd.DataFrame,
    *,
    style: str,
    **kwargs,
) -> pd.DataFrame:
    """
    Compute target trades from holdings (dollar-valued) and predictions.

    This is a stand-in for optimization. This function does not have access to
    prices and so does not perform any conversions to or from shares. It also
    needs to be told the id associated with cash.

    :param df: a dataframe with current positions (in dollars) and predictions
    :return: a dataframe with target positions and trades
        (denominated in dollars)
    """
    # Sanity-check the dataframe.
    hdbg.dassert_isinstance(df, pd.DataFrame)
    hdbg.dassert(not df.empty)
    hdbg.dassert_is_subset(
        ["asset_id", "prediction", "volatility", "position"], df.columns
    )
    hdbg.dassert_not_in("target_position", df.columns)
    hdbg.dassert_not_in("target_trade", df.columns)
    #
    hdbg.dassert(not df["prediction"].isna().any())
    hdbg.dassert(not df["volatility"].isna().any())
    hdbg.dassert(not df["position"].isna().any())
    #
    df = df.set_index("asset_id")
    hdbg.dassert(not df.index.has_duplicates)
    #
    predictions = df["prediction"].rename(0).to_frame().T
    volatility = df["volatility"].rename(0).to_frame().T
    if style == "cross_sectional":
        target_positions = cofinanc.compute_target_positions_cross_sectionally(
            predictions,
            volatility,
            **kwargs,
        )
    elif style == "longitudinal":
        target_positions = cofinanc.compute_target_positions_longitudinally(
            predictions,
            volatility,
            spread=None,
            **kwargs,
        )
    else:
        raise ValueError("Unsupported `style`=%s", style)
    hdbg.dassert_eq(target_positions.shape[0], 1)
    target_positions = pd.Series(
        target_positions.values[0],
        index=target_positions.columns,
        name="target_position",
        dtype="float",
    )
    _LOG.debug(
        "`target_positions`=\n%s",
        hpandas.df_to_str(
            target_positions, print_dtypes=True, print_shape_info=True
        ),
    )
    # These positions are expressed in dollars.
    current_positions = df["position"]
    _LOG.debug(
        "`current_positions`=\n%s",
        hpandas.df_to_str(
            current_positions, print_dtypes=True, print_shape_info=True
        ),
    )
    target_trades = target_positions - current_positions
    target_trades = check_notional_limits(target_trades)
    df["target_position"] = target_positions
    df["target_notional_trade"] = target_trades
    return df


def run_optimizer(
    config: cconfig.Config,
    df: pd.DataFrame,
    *,
    tmp_dir: str = "tmp.optimizer_stub",
) -> pd.DataFrame:
    """
    Run the optimizer through Docker.

    The flow is:
       - Save the input data in a temp dir
       - Start an `opt` Docker container
       - Run the optimizer
       - Save the optimizer output to a temp dir

    :param tmp_dir: local dir to use to exchange parameters with the "remote"
        optimizer
    """
    # Login in the Docker on AWS to pull the `opt` image.
    # TODO(Grisha): Move this inside the `opt_docker_cmd`.
    # TODO(Grisha): maybe move `docker_login` to the entrypoint?
    # To avoid to call init_logger overwriting the call to it from `main`.
    import helpers.lib_tasks_docker as hlitadoc

    ctx = invoke.context.Context()
    hlitadoc.docker_login(ctx)
    # Serialize the inputs in `tmp_dir`.
    hio.create_dir(tmp_dir, incremental=True)
    input_obj = {"config": config, "df": df}
    input_file = os.path.join(tmp_dir, "input.pkl")
    hpickle.to_pickle(input_obj, input_file)
    # Get path to the `optimizer_stub.py`.
    root_dir = hgit.get_client_root(False)
    optimizer_stub_file_path = os.path.join(
        root_dir, "optimizer/optimizer_stub.py"
    )
    hdbg.dassert_file_exists(optimizer_stub_file_path)
    # Build the command to be executed in `opt` container.
    docker_cmd_: List[str] = []
    docker_cmd_.append(optimizer_stub_file_path)
    docker_cmd_.append(f"--input_file {input_file}")
    output_file = os.path.join(tmp_dir, "output.pkl")
    docker_cmd_.append(f"--output_file {output_file}")
    docker_cmd_.append("-v INFO")
    docker_cmd = " ".join(docker_cmd_)
    # Call `optimizer_stub` through `opt` Docker container.
    optimizer_cmd_: List[str] = []
    # `opt` invokes can only be run from `optimizer` dir.
    optimizer_cmd_.append("cd optimizer &&")
    optimizer_cmd_.append(f"invoke opt_docker_cmd --cmd '{docker_cmd}'")
    optimizer_cmd = " ".join(optimizer_cmd_)
    # TODO(Grisha): call `opt_docker_cmd` directly.
    hsystem.system(optimizer_cmd)
    # Read the output from `tmp_dir`.
    output_file = os.path.join(tmp_dir, "output.pkl")
    output_df = hpickle.from_pickle(output_file)
    return output_df