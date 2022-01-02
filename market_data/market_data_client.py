"""
Import as:

import market_data.market_data_client as mdmadacl
"""

from typing import Any, List, Optional

import pandas as pd

import helpers.dbg as hdbg
import im_v2.common.data.client as ivcdclcl
import market_data.market_data_interface as mdmadain


# TODO(gp): -> MarketDataImClient?
class MarketDataInterface(mdmadain.AbstractMarketDataInterface):
    """
    Implement a `MarketDataInterface` that uses a `ImClient` as backend.
    """

    def __init__(
        self,
        *args: Any,
        im_client: ivcdclcl.AbstractImClient,
        **kwargs: Any,
    ) -> None:
        """
        Constructor.

        :param args: see `AbstractMarketDataInterface`
        :param im_client: IM client
        """
        super().__init__(*args, **kwargs)
        #hdbg.dassert_is_instance(im_client, )
        self._im_client = im_client

    def should_be_online(self, wall_clock_time: pd.Timestamp) -> bool:
        """
        See the parent class.
        """
        # TODO(gp): It should delegate to the ImClient.
        return True

    def _get_data(
        self,
        start_ts: pd.Timestamp,
        end_ts: pd.Timestamp,
        ts_col_name: str,
        asset_ids: Optional[List[str]],
        left_close: bool,
        right_close: bool,
        normalize_data: bool,
        limit: Optional[int],
    ) -> pd.DataFrame:
        """
        See the parent class.
        """
        # `ImClient` uses the convention [start_ts, end_ts).
        if not left_close:
            # Add one millisecond to not include the left boundary.
            start_ts = start_ts + pd.Timedelta(1, "ms")
        if right_close:
            # Add one millisecond to include the right boundary.
            end_ts = end_ts + pd.Timedelta(1, "ms")
        if not asset_ids:
            # If `asset_ids` is None, get all symbols from the universe.
            asset_ids = self._im_client.get_universe()
        # Load the data using `im_client`.
        full_symbols = asset_ids
        market_data = self._im_client.read_data(
            full_symbols,
            start_ts,
            end_ts,
        )
        if self._columns:
            # Select only specified columns.
            hdbg.dassert_is_subset(self._columns, market_data.columns)
            market_data = market_data[self._columns]
        if limit:
            # Keep only top N records.
            hdbg.dassert_lte(1, limit)
            market_data = market_data.head(limit)
        if normalize_data:
            market_data = self._convert_im_data(market_data)
            market_data = self.process_data(market_data)
        return market_data

    @staticmethod
    def _convert_im_data(data: pd.DataFrame) -> pd.DataFrame:
        """
        Convert IM data to the format required by `AbstractMarketDataInterface`.

        Input data example:
        ```
                                  full_symbol     close     volume
        2021-07-26 13:42:00  binance:BTC_USDT  47063.51  29.403690
        2021-07-26 13:43:00  binance:BTC_USDT  46946.30  58.246946
        2021-07-26 13:44:00  binance:BTC_USDT  46895.39  81.264098
        ```

        Output data example:
        ```
                        end_ts       full_symbol     close     volume             start_ts
        0  2021-07-26 13:42:00  binance:BTC_USDT  47063.51  29.403690  2021-07-26 13:41:00
        1  2021-07-26 13:43:00  binance:BTC_USDT  46946.30  58.246946  2021-07-26 13:42:00
        2  2021-07-26 13:44:00  binance:BTC_USDT  46895.39  81.264098  2021-07-26 13:43:00
        ```

        :param data: IM data to transform
        :return: transformed data
        """
        data = data.reset_index()
        data = data.rename(columns={"index": "end_ts"})
        # `IM` data is assumed to have 1 minute frequency.
        data["start_ts"] = data["end_ts"] - pd.Timedelta(minutes=1)
        return data

    # TODO(Grisha): implement the method.
    def _get_last_end_time(self) -> Optional[pd.Timestamp]:
        return NotImplementedError
