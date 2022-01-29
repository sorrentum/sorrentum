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
import im_v2.common.universe.universe_utils as imvcuunut

_LOG = logging.getLogger(__name__)

# TODO(gp): @Grisha -> base_clients.py

# #############################################################################
# ImClient
# #############################################################################

# TODO(gp): Consider splitting in one file per class. Not sure about the trade-off
#  between file proliferation and more organization.

# TODO(gp): @Grisha Replace AbstractImClient -> ImClient everywhere

# TODO(gp): The output of ImClient should be in the form of `start_timestamp`,
#  `end_timestamp`, and `knowledge_timestamp` since these depend on the specific
#  data source
# @Grisha let's do this, but let's schedule a clean up later and not right now

class ImClient(abc.ABC):
    """
    Retrieve market data for different vendors and backends.

    The data in output of a class derived from `ImClient` is normalized so that:
    - the index:
      - represents the knowledge time
      - is the end of the sampling interval
      - is called `timestamp`
      - is a tz-aware timestamp in UTC
    - the data:
      - is resampled on a 1 minute grid and filled with NaN values
      - is sorted by index and `full_symbol`
      - is guaranteed to have no duplicates
      - belongs to intervals like [a, b]
      - has a `full_symbol` column with a string representing the canonical name
        of the instrument

    E.g.,
    ```
                                    full_symbol     close     volume
                    timestamp
    2021-07-26 13:42:00+00:00  binance:BTC_USDT  47063.51  29.403690
    2021-07-26 13:43:00+00:00  binance:BTC_USDT  46946.30  58.246946
    2021-07-26 13:44:00+00:00  binance:BTC_USDT  46895.39  81.264098
    ```
    """

    # TODO(gp): @Grisha: cache the mapping here.
    # def __init__(self):
    #     # Cache the mapping.
    #     self._asset_id_to_full_symbol_mapping = None

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
        # Check the requested interval.
        # TODO(gp): @Grisha use dassert_is_valid_interval.
        if start_ts is not None:
            hdbg.dassert_isinstance(start_ts, pd.Timestamp)
        if end_ts is not None:
            hdbg.dassert_isinstance(end_ts, pd.Timestamp)
        if start_ts is not None and end_ts is not None:
            hdbg.dassert_lte(start_ts, end_ts)
        #
        df = self._read_data(
            full_symbols,
            start_ts,
            end_ts,
            full_symbol_col_name=full_symbol_col_name,
            **kwargs,
        )
        # Rename index.
        df.index.name = "timestamp"
        #
        _LOG.debug("After read_data: df=\n%s", hpandas.df_to_str(df))
        # Normalize data for each symbol.
        hdbg.dassert_in(full_symbol_col_name, df.columns)
        _LOG.debug("full_symbols=%s", df[full_symbol_col_name].unique())
        dfs = []
        for full_symbol, df_tmp in df.groupby(full_symbol_col_name):
            _LOG.debug("apply_im_normalization: full_symbol=%s", full_symbol)
            df_tmp = self._apply_im_normalizations(
                df_tmp, full_symbol_col_name, start_ts, end_ts
            )
            self._dassert_is_valid(df_tmp, full_symbol_col_name)
            dfs.append(df_tmp)
        df = pd.concat(dfs, axis=0)
        _LOG.debug("After im_normalization: df=\n%s", hpandas.df_to_str(df))
        # Sort by index and `full_symbol_col_name`.
        # There is not a simple way to sort by index and columns in Pandas,
        # so we convert the index into a column, sort, and convert back.
        df = df.reset_index()
        df = df.sort_values(by=["timestamp", full_symbol_col_name])
        df = df.set_index("timestamp", drop=True)
        _LOG.debug("After sorting: df=\n%s", hpandas.df_to_str(df))
        return df

    # /////////////////////////////////////////////////////////////////////////

    def get_start_ts_for_symbol(
        self, full_symbol: imvcdcfusy.FullSymbol
    ) -> pd.Timestamp:
        """
        Return the earliest timestamp available for a given `full_symbol`.

        This implementation relies on reading all the data and then finding the
        min. Derived classes can override this method if there is a more efficient
        way to get this information.
        """
        mode = "start"
        return self._get_start_end_ts_for_symbol(full_symbol, mode)

    def get_end_ts_for_symbol(
        self, full_symbol: imvcdcfusy.FullSymbol
    ) -> pd.Timestamp:
        """
        Same as `get_start_ts_for_symbol()`.
        """
        mode = "end"
        return self._get_start_end_ts_for_symbol(full_symbol, mode)

    # /////////////////////////////////////////////////////////////////////////

    # TODO(gp): @Grisha if as_asset_ids=True is the output type correct? Maybe
    #  we should just have a separate function for FullSymbol -> asset_ids
    #  conversion.
    @staticmethod
    @abc.abstractmethod
    def get_universe(as_asset_ids: bool) -> List[imvcdcfusy.FullSymbol]:
        """
        Return the entire universe of valid full symbols.

        :param as_asset_ids: if True return universe as numeric ids,
            otherwise universe as full symbols
        """

    # TODO(gp): @Grisha we are mixing string vs int and asset_ids vs full_symbols.
    #  One is the type, the other is the semantic.
    # This should be called -> get_asset_ids_from_full_symbols
    @staticmethod
    def get_numerical_ids_from_full_symbols(
        full_symbols: List[imvcdcfusy.FullSymbol],
    ) -> List[int]:
        """
        Convert full symbols into asset ids.

        :param full_symbols: assets as full symbols
        :return: assets as numerical ids
        """
        numeric_asset_id = [
            imvcuunut.string_to_numeric_id(full_symbol)
            for full_symbol in full_symbols
        ]
        return numeric_asset_id

    # TODO(gp): @Grisha -> get_full_symbols_from_asset_ids
    def get_full_symbols_from_numerical_ids(
        self, asset_ids: List[int]
    ) -> List[imvcdcfusy.FullSymbol]:
        """
        Convert asset ids into full symbols.

        :param asset_ids: assets ids
        :return: assets as full symbols
        """
        # Get universe as full symbols to construct asset ids to full symbols
        # mapping.
        # TODO(gp): Cache.
        # if self._ids_to_symbols_mapping is None:
        full_symbol_universe = self.get_universe(as_asset_ids=False)
        self._ids_to_symbols_mapping = imvcuunut.build_num_to_string_id_mapping(
            tuple(full_symbol_universe)
        )
        # Check that provided ids are part of universe.
        hdbg.dassert_is_subset(asset_ids, ids_to_symbols_mapping)
        # Convert ids to full symbols.
        full_symbols = [
            ids_to_symbols_mapping[asset_id] for asset_id in asset_ids
        ]
        return full_symbols

    # //////////////////////////////////////////////////////////////////////////

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

    # TODO(gp): @Grisha move to full_symbol.py
    @staticmethod
    def _check_full_symbols(full_symbols: List[imvcdcfusy.FullSymbol]) -> None:
        """
        Verify that full symbols are passed in a list that has no duplicates.
        """
        hdbg.dassert_isinstance(full_symbols, list)
        hdbg.dassert_no_duplicates(full_symbols)

    def _get_start_end_ts_for_symbol(
        self, full_symbol: imvcdcfusy.FullSymbol, mode: str
    ) -> pd.Timestamp:
        _LOG.debug(hprint.to_str("full_symbol"))
        # Read data for the entire period of time available.
        start_timestamp = None
        end_timestamp = None
        data = self.read_data([full_symbol], start_timestamp, end_timestamp)
        # Assume that the timestamp is always stored as index.
        if mode == "start":
            timestamp = data.index.min()
        elif mode == "end":
            timestamp = data.index.max()
        else:
            raise ValueError("Invalid mode='%s'" % mode)
        #
        hdbg.dassert_isinstance(timestamp, pd.Timestamp)
        hdateti.dassert_has_specified_tz(timestamp, ["UTC"])
        return timestamp

    @staticmethod
    def _apply_im_normalizations(
        df: pd.DataFrame,
        full_symbol_col_name: str,
        start_ts: Optional[pd.Timestamp],
        end_ts: Optional[pd.Timestamp],
    ) -> pd.DataFrame:
        """
        Apply normalizations to IM data.
        """
        _LOG.debug(hprint.to_str("full_symbol_col_name start_ts end_ts"))
        hdbg.dassert(not df.empty, "Empty df=\n%s", df)
        # 1) Drop duplicates.
        df = hpandas.drop_duplicates(df)
        # 2) Trim the data keeping only the data with index in [start_ts, end_ts].
        # Trimming of the data is done because:
        # - some data sources can be only queried at day resolution so we get
        #   a date range and then we trim
        # - we want to guarantee that no derived class returns data outside the
        #   requested #   interval
        ts_col_name = None
        left_close = True
        right_close = True
        df = hpandas.trim_df(
            df, ts_col_name, start_ts, end_ts, left_close, right_close
        )
        # 3) Resample index to 1 min frequency
        df = hpandas.resample_df(df, "T")
        # Fill NaN values appeared after resampling in full symbol column.
        # Combination of full symbol and timestamp is a unique identifier,
        # so full symbol cannot be NaN.
        df[full_symbol_col_name] = df[full_symbol_col_name].fillna(method="bfill")
        # 4) Convert to UTC.
        df.index = df.index.tz_convert("UTC")
        return df

    # TODO(gp): @Grisha Can we remove this and do all the transformation in the
    #  `_read_data` method?
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

    # TODO(gp): @Grisha -> _dassert_output_data_is_valid
    @staticmethod
    def _dassert_is_valid(df: pd.DataFrame, full_symbol_col_name: str) -> None:
        """
        Verify that the normalized data is valid.
        """
        # Check that index is `pd.DatetimeIndex`.
        hpandas.dassert_index_is_datetime(df)
        # Check that index is monotonic increasing.
        hpandas.dassert_strictly_increasing_index(df)
        # Verify that index frequency is 1 minute.
        hdbg.dassert_eq(df.index.freq, "T")
        # Check that timezone info is correct.
        expected_tz = ["UTC"]
        # Assume that the first value of an index is representative.
        hdateti.dassert_has_specified_tz(
            df.index[0],
            expected_tz,
        )
        # Check that full symbol column has no NaNs.
        hdbg.dassert(df[full_symbol_col_name].notna().all())
        # Check that there are no duplicates in data by index and full symbol.
        n_duplicated_rows = (
            df.reset_index()
            .duplicated(subset=["timestamp", full_symbol_col_name])
            .sum()
        )
        hdbg.dassert_eq(
            n_duplicated_rows, 0, msg="There are duplicated rows in the data"
        )
        # TODO(gp): @Grisha pass start_ts and end_ts and have a check
        # # Ensure that all the data is in [start_ts, end_ts].
        #  dassert_lte(start_ts, index.min)
        #  dassert_lte(index.max, end_ts)


# #############################################################################
# ImClientReadingOneSymbol
# #############################################################################


class ImClientReadingOneSymbol(ImClient, abc.ABC):
    """
    IM client for a backend that can only read one symbol at a time.

    E.g., CSV with data organized by-asset.
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
            # Normalize data according to the specific vendor.
            df = self._apply_vendor_normalization(df)
            # Insert column with full symbol into the result dataframe.
            hdbg.dassert_is_not(full_symbol_col_name, df.columns)
            df.insert(0, full_symbol_col_name, full_symbol)
            # Add data to the result dict.
            full_symbol_to_df[full_symbol] = df
        # Combine results dict in a dataframe.
        df = pd.concat(full_symbol_to_df.values())
        # We rely on the parent class to sort.
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
        Read data for a single symbol in [start_ts, end_ts).

        Parameters have the same meaning as in `read_data()`.
        """
        ...


# #############################################################################
# ImClientReadingMultipleSymbols
# #############################################################################


class ImClientReadingMultipleSymbols(ImClient, abc.ABC):
    """
    IM client for backend that can read multiple symbols at the same time.

    E.g., Parquet by-date or by-asset files allow to read data for multiple assets
    stored in the same file.
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
        Same as the parent class.
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
        ...
