import logging

import pandas as pd

import core.config as cconfig
import core.real_time_example as cretiexa
import dataflow.core.runners as dtfcorrunn
import dataflow.pipelines.dataflow_example as dtfpidtfexa
import dataflow.pipelines.real_time.pipeline as dtfpretipi
import helpers.hasyncio as hasynci
import helpers.unit_test as hunitest
import market_data.market_data_interface_example as mdmdinex
import oms.broker as ombroker
import oms.portfolio as omportfo

_LOG = logging.getLogger(__name__)


class TestRealTimeReturnPipeline1(hunitest.TestCase):
    """
    This test is similar to `TestRealTimeDagRunner1`. It uses:

    - a real DAG `ReturnPipeline`
    - a replayed time data source node using synthetic data
    """

    def test1(self) -> None:
        """
        Test `RealTimeReturnPipeline` using synthetic data.
        """
        with hasynci.solipsism_context() as event_loop:
            # Create the pipeline.
            dag_builder = dtfpretipi.RealTimeReturnPipeline()
            config = dag_builder.get_config_template()
            # Inject the real-time node.
            start_datetime = pd.Timestamp("2000-01-01 09:30:00-05:00")
            end_datetime = pd.Timestamp("2000-01-01 10:30:00-05:00")
            columns = ["close", "vol"]
            asset_ids = [1000]
            df = mdmdinex.generate_synthetic_db_data(
                start_datetime, end_datetime, columns, asset_ids
            )
            initial_replayed_delay = 5
            (
                market_data_interface,
                _,
            ) = mdmdinex.get_replayed_time_market_data_interface_example1(
                event_loop,
                start_datetime,
                end_datetime,
                initial_replayed_delay,
                df=df,
            )
            period = "last_5mins"
            source_node_kwargs = {
                "market_data_interface": market_data_interface,
                "period": period,
                "asset_id_col": "asset_id",
                "multiindex_output": False,
            }
            config["load_prices"] = cconfig.get_config_from_nested_dict(
                {
                    "source_node_name": "RealTimeDataSource",
                    "source_node_kwargs": source_node_kwargs,
                }
            )
            # Set up the event loop.
            sleep_interval_in_secs = 60 * 5
            execute_rt_loop_kwargs = (
                cretiexa.get_replayed_time_execute_rt_loop_kwargs(
                    sleep_interval_in_secs, event_loop=event_loop
                )
            )
            dag_runner_kwargs = {
                "config": config,
                "dag_builder": dag_builder,
                "fit_state": None,
                "execute_rt_loop_kwargs": execute_rt_loop_kwargs,
                "dst_dir": None,
            }
            # Run.
            dag_runner = dtfcorrunn.RealTimeDagRunner(**dag_runner_kwargs)
            result_bundles = hasynci.run(
                dag_runner.predict(), event_loop=event_loop
            )
            events = dag_runner.events
            # Check.
            # TODO(Paul): Factor this out.
            actual = []
            events_as_str = "\n".join(
                [
                    event.to_str(
                        include_tenths_of_secs=False,
                        include_wall_clock_time=False,
                    )
                    for event in events
                ]
            )
            actual.append("events_as_str=\n%s" % events_as_str)
            #
            result_bundles_as_str = "\n".join(map(str, result_bundles))
            actual.append("result_bundles=\n%s" % result_bundles_as_str)
            #
            actual = "\n".join(map(str, actual))
            self.check_string(actual)


class TestRealTimePipelineWithOms1(hunitest.TestCase):
    """
    This test uses:

    - a DAG mimicking a true dataflow pipeline (e.g., resampling)
    - a DAG whose forecasts can be passed through a df
    - a replayed time data source node using synthetic data for prices
    """

    def test1(self) -> None:
        """
        Test `RealTimeReturnPipeline` using synthetic data.
        """
        with hasynci.solipsism_context() as event_loop:
            # Create the pipeline.
            # TODO(Paul): use another DAG instead of NaivePipeline().
            # dag_builder = dtfpretipi.RealTimeReturnPipeline()
            dag_builder = dtfpidtfexa._NaivePipeline()
            config = dag_builder.get_config_template()
            # Inject the real-time node.
            start_datetime = pd.Timestamp(
                "2000-01-01 09:30:00-05:00", tz="America/New_York"
            )
            end_datetime = pd.Timestamp(
                "2000-01-01 10:30:00-05:00", tz="America/New_York"
            )
            columns = ["price", "vol"]
            asset_ids = [1000, 1001]
            df = mdmdinex.generate_synthetic_db_data(
                start_datetime, end_datetime, columns, asset_ids
            )
            initial_replayed_delay = 0
            (
                market_data_interface,
                get_wall_clock_time,
            ) = mdmdinex.get_replayed_time_market_data_interface_example1(
                event_loop,
                start_datetime,
                end_datetime,
                initial_replayed_delay,
                df=df,
            )
            period = "last_5mins"
            source_node_kwargs = {
                "market_data_interface": market_data_interface,
                "period": period,
                "asset_id_col": "asset_id",
                "multiindex_output": True,
            }
            # TODO(gp): We are making a mess by getting a DAG and then overriding
            #  the source node.
            config["get_data"] = cconfig.get_config_from_nested_dict(
                {
                    "source_node_name": "RealTimeDataSource",
                    "source_node_kwargs": source_node_kwargs,
                }
            )
            # Build Portfolio.
            # TODO(Paul): We want to have builder functions in the same class as
            #  the objects to build "standard" objects.
            strategy_id = "str1"
            account = "paper"
            asset_id_col = "asset_id"
            mark_to_market_col = "price"
            # mark_to_market_col = "close"
            timestamp_col = "end_datetime"
            broker = ombroker.Broker(market_data_interface, get_wall_clock_time)
            initial_timestamp = pd.Timestamp(
                "2000-01-01 09:30:00-05:00", tz="America/New_York"
            )
            portfolio = omportfo.Portfolio.from_cash(
                strategy_id,
                account,
                market_data_interface,
                get_wall_clock_time,
                asset_id_col,
                mark_to_market_col,
                timestamp_col,
                broker=broker,
                initial_cash=1e6,
                initial_timestamp=initial_timestamp,
            )
            order_type = "price@twap"
            # Populate place trades.
            config["process_forecasts"]["process_forecasts_config"] = {
                "market_data_interface": market_data_interface,
                "portfolio": portfolio,
                "order_type": order_type,
                "ath_start_time": pd.Timestamp(
                    "2000-01-01 09:30:00-05:00", tz="America/New_York"
                ).time(),
                "trading_start_time": pd.Timestamp(
                    "2000-01-01 09:30:00-05:00", tz="America/New_York"
                ).time(),
                "ath_end_time": pd.Timestamp(
                    "2000-01-01 16:40:00-05:00", tz="America/New_York"
                ).time(),
                "trading_end_time": pd.Timestamp(
                    "2000-01-01 16:40:00-05:00", tz="America/New_York"
                ).time(),
                #
            }
            # Set up the event loop.
            sleep_interval_in_secs = 60 * 5
            execute_rt_loop_kwargs = (
                cretiexa.get_replayed_time_execute_rt_loop_kwargs(
                    sleep_interval_in_secs, event_loop=event_loop
                )
            )
            dag_runner_kwargs = {
                "config": config,
                "dag_builder": dag_builder,
                "fit_state": None,
                "execute_rt_loop_kwargs": execute_rt_loop_kwargs,
                "dst_dir": None,
            }
            # Run.
            dag_runner = dtfcorrunn.RealTimeDagRunner(**dag_runner_kwargs)
            result_bundles = hasynci.run(
                dag_runner.predict(), event_loop=event_loop
            )
            events = dag_runner.events
            # Check.
            # TODO(Paul): Factor this out and from these tests. We want to have
            # several tests and share the code.
            actual = []
            events_as_str = "\n".join(
                [
                    event.to_str(
                        include_tenths_of_secs=False,
                        include_wall_clock_time=False,
                    )
                    for event in events
                ]
            )
            actual.append("events_as_str=\n%s" % events_as_str)
            #
            result_bundles_as_str = "\n".join(map(str, result_bundles))
            actual.append("result_bundles=\n%s" % result_bundles_as_str)
            #
            actual = "\n".join(map(str, actual))
            self.check_string(actual)
