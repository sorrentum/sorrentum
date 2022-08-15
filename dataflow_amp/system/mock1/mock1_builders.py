"""
Import as:

import dataflow_amp.system.mock1.mock1_builders as dtfasmmobu
"""
import logging
from typing import Any, Dict

import core.config as cconfig
import dataflow.core as dtfcore
import dataflow.system as dtfsys
import helpers.hdbg as hdbg
import market_data as mdata

_LOG = logging.getLogger(__name__)

# TODO(gp): -> example1_system_builder.py? What's the convention now?

# #############################################################################
# Market data instances
# #############################################################################


def get_Mock1_MarketData_example2(
    system: dtfsys.System,
) -> mdata.ImClientMarketData:
    """
    Build a replayed MarketData from an ImClient feeding data from a df.
    """
    im_client = system.config["market_data_config", "im_client"]
    asset_ids = system.config["market_data_config", "asset_ids"]
    # TODO(gp): Specify only the columns that are needed.
    columns = None
    columns_remap = None
    market_data = mdata.get_HistoricalImClientMarketData_example1(
        im_client, asset_ids, columns, columns_remap
    )
    return market_data


# #############################################################################
# Process forecasts configs.
# #############################################################################


def get_Mock1_process_forecasts_dict_example1(
    system: dtfsys.System,
) -> Dict[str, Any]:
    """
    Get the dictionary with `ProcessForecastsNode` config params for Example1
    pipeline.
    """
    prediction_col = "feature1"
    volatility_col = "vwap.ret_0.vol"
    spread_col = None
    order_duration_in_mins = 5
    style = "cross_sectional"
    compute_target_positions_kwargs = {
        "bulk_frac_to_remove": 0.0,
        "bulk_fill_method": "zero",
        "target_gmv": 1e5,
    }
    log_dir = None
    process_forecasts_dict = dtfsys.get_process_forecasts_dict_example1(
        system.portfolio,
        prediction_col,
        volatility_col,
        spread_col,
        order_duration_in_mins,
        style,
        compute_target_positions_kwargs,
        log_dir,
    )
    return process_forecasts_dict


# #############################################################################
# DAG instances.
# #############################################################################


def get_Mock1_HistoricalDag_example1(system: dtfsys.System) -> dtfcore.DAG:
    """
    Build a DAG with `HistoricalDataSource` for simulation.
    """
    hdbg.dassert_isinstance(system, dtfsys.System)
    # Create HistoricalDataSource.
    stage = "read_data"
    market_data = system.market_data
    # TODO(gp): This in the original code was
    #  `ts_col_name = "timestamp_db"`.
    ts_col_name = "end_datetime"
    multiindex_output = True
    col_names_to_remove = ["start_ts"]
    node = dtfsys.HistoricalDataSource(
        stage,
        market_data,
        ts_col_name,
        multiindex_output,
        col_names_to_remove=col_names_to_remove,
    )
    dag = dtfsys.build_dag_with_data_source_node(system, node)
    return dag


# TODO(Grisha): -> `..._example1`.
def get_Mock1_RealtimeDag_example2(system: dtfsys.System) -> dtfcore.DAG:
    """
    Build a DAG with `RealTimeDataSource`.
    """
    hdbg.dassert_isinstance(system, dtfsys.System)
    # How much history is needed for the DAG to compute.
    lookback_in_days = 1
    system = dtfsys.apply_history_lookback(system, days=lookback_in_days)
    dag = dtfsys.add_real_time_data_source(system)
    return dag


# TODO(Grisha): -> `..._example2`.
def get_Mock1_RealtimeDag_example3(system: dtfsys.System) -> dtfcore.DAG:
    """
    Build a DAG with `RealTimeDataSource` and `ForecastProcessorNode`.
    """
    # How much history is needed for the DAG to compute.
    lookback_in_days = 7
    system = dtfsys.apply_history_lookback(system, days=lookback_in_days)
    dag = dtfsys.add_real_time_data_source(system)
    # Configure a `ProcessForecastNode`.
    process_forecasts_config = get_Mock1_process_forecasts_dict_example1(
        system
    )
    system.config[
        "process_forecasts_config"
    ] = cconfig.get_config_from_nested_dict(process_forecasts_config)
    # Append the `ProcessForecastNode`.
    dag = dtfsys.add_process_forecasts_node(system, dag)
    return dag
