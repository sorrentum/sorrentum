#"""
#Import as:
#
#import market_data_lime.ig_replayed_market_data as mdlermada
#"""
#
#import asyncio
#import logging
#from typing import Any, Dict, List, Optional, Union
#
#import pandas as pd
#
#import core.real_time as creatime
#import helpers.hdbg as hdbg
#import helpers.hpandas as hpandas
#import helpers.hprint as hprint
#import market_data as mdata
#import market_data_lime.ig_real_time_market_data as mdlertmda
#
#_LOG = logging.getLogger(__name__)
#
#
## #############################################################################
## IgReplayedMarketData
## #############################################################################
#
#
## TODO(gp): IgReplayedMarketDataFromFile or allow to pass a df.
#class IgReplayedMarketData(mdata.ReplayedMarketData):
#    """
#    A market data interface that mocks the IG RT DB using data extracted from
#    the real DB and played back.
#    """
#
#    def __init__(
#        self,
#        file_name: str,
#        # TODO(gp): The IG name for this is `timestamp_db` so no need to pass.
#        knowledge_datetime_col_name: str,
#        event_loop: Optional[asyncio.AbstractEventLoop],
#        delay_in_secs: int,
#        replayed_delay_in_mins_or_timestamp: Union[int, str],
#        *,
#        asset_ids: Optional[List[int]] = None,
#        columns: Optional[List[str]] = None,
#        column_remap: Optional[Dict[str, Any]] = None,
#        **load_market_data_kwargs: Any,
#    ):
#        """
#        Constructor.
#
#        :param file_name: file with the data
#        :param knowledge_datetime_col_name: column name for the knowledge time for
#            the corresponding data row
#        :param replayed_delay_in_mins_or_timestamp: when the replayed wall-clock time starts
#            with respect to the beginning of the data.
#            - E.g., the with `replayed_delay_in_mins_or_timestamp = -5` the data is replayed
#              starting from 5 mins before the beginning of the data
#            - The token 'last_timestamp' means aligning the wall-clock time to the
#              end of the data
#        :param asset_ids: list of IG ids to play back. `None` means all the EG ids
#            available in the file are used
#        :param columns: list of columns to emit or `None` for all the available
#            columns
#        """
#        _LOG.debug(
#            hprint.to_str(
#                "file_name knowledge_datetime_col_name delay_in_secs "
#                "replayed_delay_in_mins_or_timestamp asset_ids"
#            )
#        )
#        # Read the data generated by `save_market_data()`.
#        df = mdata.load_market_data(file_name, **load_market_data_kwargs)
#        _LOG.debug(hpandas.df_to_str(df, tag="df", max_rows=6))
#        # TODO(gp): It looks like the historical TAQ bar has some nan rows.
#        #  We should drop the all nan rows before we dump the data.
#        # df = df.dropna(how="all")
#        df = df.dropna(subset=["asset_id"])
#        # TODO(Paul): There are floats because of nan in asset_id so we force
#        #  them to int.
#        df["asset_id"] = df["asset_id"].astype(int)
#        # Apply the tz.
#        for col_name in ("start_time", "end_time", "timestamp_db"):
#            if col_name in df.columns:
#                df[col_name] = pd.to_datetime(df[col_name], utc=True)
#                df[col_name] = df[col_name].dt.tz_convert("America/New_York")
#        if "timestamp_db" not in df:
#            # TODO(gp): We need to use end_time, but sometimes is an index so
#            #  we use start_time.
#            # TODO(gp): The MarketData should add timestamp_db.
#            df["timestamp_db"] = df["start_time"] + pd.Timedelta(minutes=1)
#            df["timestamp_db"] = df["timestamp_db"] + pd.Timedelta(seconds=30)
#        # Print information about the types.
#        _LOG.debug(hpandas.df_to_str(df, tag="df", print_dtypes=True, max_rows=6))
#        min_time = df["start_time"].min()
#        max_time = df["start_time"].max()
#        _LOG.debug(hprint.to_str("min_time max_time"))
#        _ = max_time
#        # Handle the asset_ids.
#        asset_ids_from_file = df["asset_id"].unique()
#        if asset_ids is None:
#            asset_ids = asset_ids_from_file
#        hdbg.dassert_is_subset(asset_ids, asset_ids_from_file)
#        _LOG.debug(
#            "len(asset_ids_from_file)=%s len(asset_ids)=%s",
#            len(asset_ids_from_file),
#            len(asset_ids),
#        )
#        # TODO(gp): This and the get_wall_clock_time could be pushed to the parent
#        #  class.
#        if isinstance(replayed_delay_in_mins_or_timestamp, str):
#            hdbg.dassert_eq(replayed_delay_in_mins_or_timestamp, "last_timestamp")
#            # Use the last available time.
#            initial_replayed_timestamp = pd.Timestamp(max_time)
#        else:
#            # Use a replayed real-time with respect to the beginning of the data.
#            initial_replayed_timestamp = pd.Timestamp(min_time) + pd.Timedelta(
#                minutes=replayed_delay_in_mins_or_timestamp
#            )
#        asset_id_col = "asset_id"
#        if column_remap is None:
#            column_remap = {}
#        # column_remap = {
#        #     # TODO(gp): Some pipelines call volume "vol", which could be
#        #     # confused with volatility. We should be explicit and call it
#        #     # "volume".
#        #     # "volume": "vol",
#        # }
#        start_time_col_name = "start_time"
#        end_time_col_name = "end_time"
#        get_wall_clock_time = creatime.get_replayed_wall_clock_time(
#            "ET", initial_replayed_timestamp, event_loop=event_loop
#        )
#        sleep_in_secs = 1
#        time_out_in_secs = 60 * 5
#        # Build the object.
#        super().__init__(
#            df,
#            knowledge_datetime_col_name,
#            delay_in_secs,
#            #
#            asset_id_col,
#            asset_ids,
#            start_time_col_name,
#            end_time_col_name,
#            columns,
#            get_wall_clock_time,
#            sleep_in_secs=sleep_in_secs,
#            time_out_in_secs=time_out_in_secs,
#            column_remap=column_remap,
#        )
#
#    def should_be_online(self, current_time: pd.Timestamp) -> bool:
#        _ = self
#        return mdlertmda.ig_db_should_be_online(current_time)