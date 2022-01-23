"""
Import as:

import im_v2.common.data.client.clients as imvcdclcl
"""

import abc
import logging
from typing import Any, Dict, List, Optional

import pandas as pd

import helpers.hdatetime as hdateti
import helpers.hdbg as hdbg
import helpers.hpandas as hpandas
import helpers.hprint as hprint
import im_v2.common.data.client.full_symbol as imvcdcfusy
import im_v2.common.universe.universe_utils as icuuut

_LOG = logging.getLogger(__name__)


# #############################################################################
# ImClient
# #############################################################################

# TODO(gp): Consider splitting in one file per class. Not sure about the trade-off
#  between file proliferation and more organization.


class ImClient(abc.ABC):
    """
    Retrieve market data for different vendors from different backends.

    Invariants:
    - data is normalized so that the index is a UTC timestamp
    - data is resampled on a 1min grid
    - data is guaranteed to have no duplicates
    """

    def read_data(
        self,
        full_symbols: List[imvcdcfusy.FullSymbol],
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        *,
        full_symbol_col_name: str = "full_symbol",
        **kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Read data in `[start_ts, end_ts)` for `imvcdcfusy.FullSymbol` symbols.

        ```
                                  full_symbol     close     volume
                  timestamp
        2021-07-26 13:42:00  binance:BTC_USDT  47063.51  29.403690
        2021-07-26 13:43:00  binance:BTC_USDT  46946.30  58.246946
        2021-07-26 13:44:00  binance:BTC_USDT  46895.39  81.264098
        ```

        :param full_symbols: list of full symbols, e.g.
            `['binance::BTC_USDT', 'kucoin::ETH_USDT']`
        :param start_ts: the earliest date timestamp to load data for
            - `None` means start from the beginning of the available data
        :param end_ts: the latest date timestamp to load data for
            - `None` means end at the end of the available data
        :param full_symbol_col_name: name of the column storing the full
            symbols (e.g., `asset_id`)
        :return: combined data for all the requested symbols
        """
        _LOG.debug(
            hprint.to_str(
                "full_symbols start_ts end_ts full_symbol_col_name kwargs"
            )
        )
        self._check_full_symbols(full_symbols)
        df = self._read_data(
            full_symbols,
            start_ts,
            end_ts,
            full_symbol_col_name=full_symbol_col_name,
            **kwargs,
        )
        hdbg.dassert_in(full_symbol_col_name, df.columns)
        df.index.name = "timestamp"
        _LOG.debug("After _read_data: df=\n%s", hprint.dataframe_to_str(df))
        # Normalize data for each symbol.
        dfs = []
        for _, df_tmp in df.groupby(full_symbol_col_name):
            df_tmp = self._apply_im_normalizations(df_tmp, start_ts, end_ts)
            self._dassert_is_valid(df_tmp)
            dfs.append(df_tmp)
        df = pd.concat(dfs, axis=0)
        _LOG.debug("After im_normalization: df=\n%s", hprint.dataframe_to_str(df))
        # Sort by index and `full_symbol_col_name`.
        # There is not a simple way to sort by index and columns in Pandas,
        # so we convert the index into a column, sort.
        df = df.reset_index()
        df = df.sort_values(by=["timestamp", full_symbol_col_name])
        df = df.set_index("timestamp", drop=True)
        _LOG.debug("After sorting: df=\n%s", hprint.dataframe_to_str(df))
        return df

    def get_start_ts_for_symbol(
        self, full_symbol: imvcdcfusy.FullSymbol
    ) -> pd.Timestamp:
        """
        Return the earliest timestamp available for a given
        `imvcdcfusy.FullSymbol`.

        This implementation relies on reading all the data and then
        finding the min. Derived classes can override this method if
        there is a more efficient way to get this information.
        """
        _LOG.debug(hprint.to_str("full_symbol"))
        # Read data for the entire period of time available.
        start_timestamp = None
        end_timestamp = None
        data = self.read_data([full_symbol], start_timestamp, end_timestamp)
        # Assume that the timestamp is always stored as index.
        start_ts = data.index.min()
        hdbg.dassert_isinstance(start_ts, pd.Timestamp)
        hdateti.dassert_has_specified_tz(start_ts, ["UTC"])
        return start_ts

    def get_end_ts_for_symbol(
        self, full_symbol: imvcdcfusy.FullSymbol
    ) -> pd.Timestamp:
        """
        Return the latest timestamp available for a given
        `imvcdcfusy.FullSymbol`.
        """
        _LOG.debug(hprint.to_str("full_symbol"))
        # Read data for the entire period of time available.
        start_timestamp = None
        end_timestamp = None
        data = self.read_data([full_symbol], start_timestamp, end_timestamp)
        # Assume that the timestamp is always stored as index.
        end_ts = data.index.max()
        hdbg.dassert_isinstance(end_ts, pd.Timestamp)
        hdateti.dassert_has_specified_tz(end_ts, ["UTC"])
        return end_ts

    @staticmethod
    @abc.abstractmethod
    def get_universe(as_asset_ids: bool) -> List[imvcdcfusy.FullSymbol]:
        """
        Get universe as full symbols.

        :param as_asset_ids: if True return universe as numeric ids, otherwise universe as full symbols
        """

    @staticmethod
    def get_numerical_ids_from_full_symbols(full_symbols: [imvcdcfusy.FullSymbol]) -> List[int]:
        """
        Convert assets as full symbols to assets as numeric ids.

        :param full_symbols: assets as full symbols
        :return: assets as numeric ids
        """
        numeric_asset_ids = [icuuut.string_to_numeric_id(full_symbol) for full_symbol in full_symbols]
        return numeric_asset_ids

    def get_full_symbols_from_numerical_ids(self, asset_ids: List[int]) -> List[imvcdcfusy.FullSymbol]:
        """
        Convert assets as numeric ids to assets as full symbols.

        :param asset_ids: assets as numeric ids
        :return: assets as full symbols
        """
        # Get universe as full symbols to construct numeric ids to full symbols mapping.
        full_symbol_universe = self.get_universe(as_asset_ids=False)
        ids_to_symbol_mapping = icuuut.build_num_to_string_id_mapping(tuple(full_symbol_universe))
        # Check that provided ids are part of universe.
        hdbg.dassert_is_subset(asset_ids, ids_to_symbol_mapping.keys())
        # Convert ids to full symbols.
        universe_as_symbols = [ids_to_symbol_mapping[asset_id] for asset_id in asset_ids]
        universe_as_symbols = sorted(universe_as_symbols)
        return universe_as_symbols

    @abc.abstractmethod
    def _read_data(
        self,
        full_symbols: List[imvcdcfusy.FullSymbol],
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        *,
        full_symbol_col_name: str = "full_symbol",
        **kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        ...

    @staticmethod
    def _check_full_symbols(full_symbols: List[imvcdcfusy.FullSymbol]) -> None:
        """
        Verify that full symbols are passed in a list that has no duplicates.
        """
        hdbg.dassert_isinstance(full_symbols, list)
        hdbg.dassert_no_duplicates(full_symbols)

    @staticmethod
    def _apply_im_normalizations(
        df: pd.DataFrame,
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
    ) -> pd.DataFrame:
        """
        Apply normalizations to IM data.

        Normalizations include:
        - drop duplicates
        - trim the data with index in specified date interval
        - resample data to 1 min frequency

        Data trimming is done because:
        - some data sources can be only queried at day resolution so we get
          the date range and then we trim
        - we want to guarantee that nobody returns data outside the requested
          interval
        """
        _LOG.debug(hprint.to_str("start_ts end_ts"))
        # Drop duplicates.
        df = hpandas.drop_duplicates(df)
        # Trim the data with index in [start_ts, end_ts].
        ts_col_name = None
        left_close = True
        right_close = True
        df = hpandas.trim_df(
            df, ts_col_name, start_ts, end_ts, left_close, right_close
        )
        # Resample index.
        df = hpandas.resample_df(df, "T")
        return df

    @staticmethod
    @abc.abstractmethod
    def _apply_vendor_normalization(df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformation specific of the vendor, e.g. rename columns,
        convert data types.

        :param df: raw data
        :return: normalized data
        """
        ...

    @staticmethod
    def _dassert_is_valid(df: pd.DataFrame) -> None:
        """
        Verify that the normalized data is valid.
        """
        # Check that index is `pd.DatetimeIndex`.
        hpandas.dassert_index_is_datetime(df)
        # Check that index is monotonic increasing.
        hpandas.dassert_strictly_increasing_index(df)
        # Verify that index frequency is "T" (1 minute).
        hdbg.dassert_eq(df.index.freq, "T")
        # Check that timezone info is correct.
        expected_tz = ["UTC"]
        # Assume that the first value of an index is representative.
        hdateti.dassert_has_specified_tz(
            df.index[0],
            expected_tz,
        )
        # Check that there are no duplicates in the data.
        n_duplicated_rows = df.dropna(how="all").duplicated().sum()
        hdbg.dassert_eq(
            n_duplicated_rows, 0, msg="There are duplicated rows in the data"
        )


# #############################################################################
# ImClientReadingOneSymbol
# #############################################################################


class ImClientReadingOneSymbol(ImClient, abc.ABC):
    """
    Abstract IM client for a backend that can read one symbol at a time.
    """

    def _read_data(
        self,
        full_symbols: List[imvcdcfusy.FullSymbol],
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        *,
        full_symbol_col_name: str = "full_symbol",
        **kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Same as the method in the parent class.
        """
        _LOG.debug(
            hprint.to_str(
                "full_symbols start_ts end_ts full_symbol_col_name kwargs"
            )
        )
        # Load the data for each symbol.
        full_symbol_to_df = {}
        for full_symbol in sorted(full_symbols):
            df = self._read_data_for_one_symbol(
                full_symbol,
                start_ts,
                end_ts,
                **kwargs,
            )
            # Normalize data.
            df = self._apply_vendor_normalization(df)
            # Insert column with full symbol to the dataframe.
            hdbg.dassert_is_not(full_symbol_col_name, df.columns)
            df.insert(0, full_symbol_col_name, full_symbol)
            # Add full symbol data to the results dict.
            full_symbol_to_df[full_symbol] = df
        # Combine results dict in a dataframe.
        df = pd.concat(full_symbol_to_df.values())
        return df

    @abc.abstractmethod
    def _read_data_for_one_symbol(
        self,
        full_symbol: imvcdcfusy.FullSymbol,
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        **kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Read data for a single `imvcdcfusy.FullSymbol` in [start_ts, end_ts).

        Parameters have the same meaning as parameters in `read_data()`
        with the same name.
        """
        ...


# #############################################################################
# ImClientReadingMultipleSymbols
# #############################################################################


class ImClientReadingMultipleSymbols(ImClient, abc.ABC):
    """
    Abstract IM client for backend that can read multiple symbols at the same
    time.

    This is used for reading data from Parquet by-date files, where
    multiple assets are stored in the same file and can be accessed
    together.
    """

    def _read_data(
        self,
        full_symbols: List[imvcdcfusy.FullSymbol],
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        *,
        full_symbol_col_name: str = "full_symbol",
        **kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Same as the abstract class.
        """
        _LOG.debug(
            hprint.to_str(
                "full_symbols start_ts end_ts full_symbol_col_name kwargs"
            )
        )
        df = self._read_data_for_multiple_symbols(
            full_symbols, start_ts, end_ts, full_symbol_col_name, **kwargs
        )
        df = self._apply_vendor_normalization(df)
        return df

    @abc.abstractmethod
    def _read_data_for_multiple_symbols(
        self,
        full_symbols: List[imvcdcfusy.FullSymbol],
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
        full_symbol_col_name: str,
        **kwargs: Dict[str, Any],
    ) -> pd.DataFrame:
        """
        Derived classes need to implement this.
        """
        ...
