"""
Import as:

import dataflow.system.example_pipeline1_system_runner as dtfsepsyru
"""

import logging
from typing import List, Optional, Tuple

import pandas as pd

import core.config as cconfig
import dataflow.pipelines.examples.example1_pipeline as dtfpexexpi
import dataflow.system.system_runner as dtfsysyrun
import dataflow.core.dag_builder as dtfcodabui
import market_data as mdata
import oms
import dataflow.system.real_time_dag_runner as dtfsrtdaru
import dataflow.system.source_nodes as dtfsysonod
import helpers.hdatetime as hdateti


_LOG = logging.getLogger(__name__)


# TODO(gp): -> system_runner_example.py for symmetry with the other _example?


class Example1_ForecastSystem(dtfsysyrun.ForecastSystem):
    """
    Create a system with:
    - a ReplayedMarketData
    - an Example1 DAG
    """
    def __init__(self, asset_ids: List[int], event_loop=None):
        self._asset_ids = asset_ids
        self._event_loop = event_loop

    def get_market_data(
        self,
        data: pd.DataFrame,
        initial_replayed_delay: int = 5,
    ):
        market_data, _ = mdata.get_ReplayedTimeMarketData_from_df(
            self._event_loop,
            initial_replayed_delay,
            data,
        )
        return market_data

    def get_dag_config(
        self,
        # TODO(Danya): These parameters don't go anywhere,
        #  and it seems like they didn't in the original version.
        #  @gp should these be added to `get_config_template`?
        prediction_col: str,
        volatility_col: str,
        returns_col: str,
        timedelta: pd.Timedelta,
        asset_id_col: str,
        *
        spread_col: Optional[str],
        log_dir: Optional[str],
    ) -> Tuple[cconfig.Config, dtfcodabui.DagBuilder]:
        """
        See description in parent class.
        """
        config = cconfig.Config()
        # Save the `DagBuilder` and the `DagConfig` in the config object.
        dag_builder = dtfpexexpi.Example1_DagBuilder()
        dag_config = dag_builder.get_config_template()
        config["DAG"] = dag_config
        config["meta", "dag_builder"] = dag_builder
        return config

    def get_dag_runner(
        self,
        config: cconfig.Config,
        market_data, 
        *,
        real_time_loop_time_out_in_secs: Optional[int] = None,
    ) -> dtfsrtdaru.RealTimeDagRunner:
        """
        Build a DAG runner from a config.
        """

        stage = "read_data"
        asset_id_col = "asset_id"
        # The DAG works on multi-index dataframe containing multiple
        # features for multiple assets.
        multiindex_output = True
        # How much history is needed for the DAG to compute.
        timedelta = pd.Timedelta("20T")
        node = dtfsysonod.RealTimeDataSource(
                stage,
                market_data,
                timedelta,
                asset_id_col,
                #ts_col_name,
                multiindex_output,
                #col_names_to_remove=col_names_to_remove,
            )
        # Build the DAG.
        dag_builder = config["meta", "dag_builder"]
        dag = dag_builder.get_dag(config["DAG"])
        # # This is for debugging. It saves the output of each node in a `csv` file.
        # dag.set_debug_mode("df_as_csv", False, "crypto_forever")
        # if False:
        #     dag.force_freeing_nodes = True
        # Add the data source node.
        dag.insert_at_head(stage, node)
        sleep_interval_in_secs = 5 * 60
        # Set up the event loop.
        get_wall_clock_time = market_data.get_wall_clock_time
        execute_rt_loop_kwargs = {
                "get_wall_clock_time": get_wall_clock_time,
                "sleep_interval_in_secs": sleep_interval_in_secs,
                "time_out_in_secs": real_time_loop_time_out_in_secs,
            }
        dag_runner_kwargs = {
                "config": config,
                # TODO(Danya): Add a more fitting/transparent name.
                "dag_builder": dag,
                "fit_state": None,
                "execute_rt_loop_kwargs": execute_rt_loop_kwargs,
                "dst_dir": None,
            }
        dag_runner = dtfsrtdaru.RealTimeDagRunner(**dag_runner_kwargs)
        return dag_runner

# #############################################################################
class Example1_Dataframe_ForecastSystem(Example1_ForecastSystem):
    def get_portfolio(
        self,
        market_data: mdata.MarketData,
    ) -> oms.AbstractPortfolio:
        portfolio = oms.get_DataFramePortfolio_example1(
            self._event_loop,
            market_data=market_data,
            mark_to_market_col="close",
            pricing_method="twap.5T",
            asset_ids=self._asset_ids,
        )
        portfolio.broker._column_remap = {
            "bid": "bid",
            "ask": "ask",
            "midpoint": "midpoint",
            "price": "close",
        }
        return portfolio
class Example1_Database_SystemRunner(
    dtfsysyrun.SystemWithSimulatedOmsRunner, Example1_ForecastSystem
):
     def get_portfolio(
         self,
         market_data: mdata.MarketData,
     ) -> oms.AbstractPortfolio:
         table_name = oms.CURRENT_POSITIONS_TABLE_NAME
         portfolio = oms.get_mocked_portfolio_example1(
             self._event_loop,
             self._db_connection,
             table_name,
             market_data=market_data,
             mark_to_market_col="close",
             pricing_method="twap.5T",
             asset_ids=self._asset_ids,
         )
         portfolio.broker._column_remap = {
             "bid": "bid",
             "ask": "ask",
             "midpoint": "midpoint",
             "price": "close",
         }
         return portfolio
