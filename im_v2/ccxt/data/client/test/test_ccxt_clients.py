import os
from typing import List

import pandas as pd
import pytest

import core.finance as cofinanc
import helpers.hdatetime as hdateti
import helpers.hparquet as hparque
import helpers.hsql as hsql
import im_v2.ccxt.data.client.ccxt_clients as imvcdccccl
import im_v2.ccxt.data.client.ccxt_clients_example as imvcdcccex
import im_v2.ccxt.db.utils as imvccdbut
import im_v2.common.data.client as icdc
import im_v2.common.db.db_utils as imvcddbut
import im_v2.common.universe as ivcu


def get_expected_column_names() -> List[str]:
    """
    Return a list of expected column names.
    """
    expected_column_names = [
        "full_symbol",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    return expected_column_names


# #############################################################################
# TestCcxtCsvClient1
# #############################################################################


class TestCcxtCsvClient1(icdc.ImClientTestCase):
    """
    For all the test methods see description of corresponding private method in
    the parent class.
    """

    def test_read_data1(self) -> None:
        im_client = imvcdcccex.get_CcxtCsvClient_example2()
        full_symbol = "binance::BTC_USDT"
        #
        expected_length = 100
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {"full_symbol": ["binance::BTC_USDT"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(100, 6)
                                         full_symbol     open     high      low    close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.00  6319.04  6310.32  6311.64   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.64  6311.77  6302.81  6302.81  16.781206
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6302.81  6306.00  6292.79  6297.26  55.373226
        ...
        2018-08-17 01:37:00+00:00  binance::BTC_USDT  6346.96  6347.00  6343.00  6343.14  10.787817
        2018-08-17 01:38:00+00:00  binance::BTC_USDT  6345.98  6345.98  6335.04  6339.25  38.197244
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.25  6348.91  6339.00  6342.95  16.394692
        """
        # pylint: enable=line-too-long
        self._test_read_data1(
            im_client,
            full_symbol,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data2(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtCsvClient_example1(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        #
        expected_length = 199
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(199, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        ...
        2018-08-17 01:38:00+00:00   kucoin::ETH_USDT   292.158945   293.007409   292.158945   293.007409   0.001164
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.250000  6348.910000  6339.000000  6342.950000  16.394692
        2018-08-17 01:39:00+00:00   kucoin::ETH_USDT   292.158945   292.158946   292.158945   292.158946   0.235161
        """
        # pylint: enable=line-too-long
        self._test_read_data2(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data3(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtCsvClient_example1(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.Timestamp("2018-08-17T00:02:00-00:00")
        #
        expected_length = 196
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:02:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(196, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6302.810000  6306.000000  6292.790000  6297.260000  55.373226
        2018-08-17 00:02:00+00:00   kucoin::ETH_USDT   286.405988   286.405988   285.400193   285.400197   0.162255
        2018-08-17 00:03:00+00:00  binance::BTC_USDT  6299.970000  6299.970000  6286.930000  6294.520000  34.611797
        ...
        2018-08-17 01:38:00+00:00   kucoin::ETH_USDT   292.158945   293.007409   292.158945   293.007409   0.001164
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.250000  6348.910000  6339.000000  6342.950000  16.394692
        2018-08-17 01:39:00+00:00   kucoin::ETH_USDT   292.158945   292.158946   292.158945   292.158946   0.235161
        """
        # pylint: enable=line-too-long
        self._test_read_data3(
            im_client,
            full_symbols,
            start_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data4(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtCsvClient_example1(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        end_ts = pd.Timestamp("2018-08-17T00:04:00-00:00")
        #
        expected_length = 9
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 00:04:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(9, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        ...
        2018-08-17 00:03:00+00:00   kucoin::ETH_USDT   285.400193   285.400193   285.400193   285.400193   0.020260
        2018-08-17 00:04:00+00:00  binance::BTC_USDT  6294.520000  6299.980000  6290.000000  6296.100000  22.088586
        2018-08-17 00:04:00+00:00   kucoin::ETH_USDT   285.400193   285.884638   285.400193   285.884638   0.074655
        """
        # pylint: enable=line-too-long
        self._test_read_data4(
            im_client,
            full_symbols,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data5(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtCsvClient_example1(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.Timestamp("2018-08-17T00:01:00-00:00")
        end_ts = pd.Timestamp("2018-08-17T00:04:00-00:00")
        #
        expected_length = 8
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-17 00:04:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(8, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6302.810000  6306.000000  6292.790000  6297.260000  55.373226
        ...
        2018-08-17 00:03:00+00:00   kucoin::ETH_USDT   285.400193   285.400193   285.400193   285.400193   0.020260
        2018-08-17 00:04:00+00:00  binance::BTC_USDT  6294.520000  6299.980000  6290.000000  6296.100000  22.088586
        2018-08-17 00:04:00+00:00   kucoin::ETH_USDT   285.400193   285.884638   285.400193   285.884638   0.074655
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            im_client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data6(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtCsvClient_example1(resample_1min)
        full_symbol = "unsupported_exchange::unsupported_currency"
        self._test_read_data6(im_client, full_symbol)

    def test_read_data7(self) -> None:
        resample_1min = False
        im_client = imvcdcccex.get_CcxtCsvClient_example1(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        #
        expected_length = 174
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(174, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        ...
        2018-08-17 01:38:00+00:00   kucoin::ETH_USDT   292.158945   293.007409   292.158945   293.007409   0.001164
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.250000  6348.910000  6339.000000  6342.950000  16.394692
        2018-08-17 01:39:00+00:00   kucoin::ETH_USDT   292.158945   292.158946   292.158945   292.158946   0.235161
                """
        # pylint: enable=line-too-long
        self._test_read_data7(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    # ////////////////////////////////////////////////////////////////////////

    def test_get_start_ts_for_symbol1(self) -> None:
        im_client = imvcdcccex.get_CcxtCsvClient_example2()
        full_symbol = "binance::BTC_USDT"
        expected_start_ts = pd.to_datetime("2018-08-17 00:00:00", utc=True)
        self._test_get_start_ts_for_symbol1(
            im_client, full_symbol, expected_start_ts
        )

    def test_get_end_ts_for_symbol1(self) -> None:
        im_client = imvcdcccex.get_CcxtCsvClient_example2()
        full_symbol = "binance::BTC_USDT"
        expected_end_ts = pd.to_datetime("2018-08-17 01:39:00", utc=True)
        self._test_get_end_ts_for_symbol1(im_client, full_symbol, expected_end_ts)

    # ////////////////////////////////////////////////////////////////////////

    def test_get_universe1(self) -> None:
        im_client = imvcdcccex.get_CcxtCsvClient_example2()
        expected_length = 3
        expected_first_elements = [
            "binance::BTC_USDT",
            "gateio::XRP_USDT",
            "kucoin::ETH_USDT",
        ]
        expected_last_elements = [
            "binance::BTC_USDT",
            "gateio::XRP_USDT",
            "kucoin::ETH_USDT",
        ]
        self._test_get_universe1(
            im_client,
            expected_length,
            expected_first_elements,
            expected_last_elements,
        )


# #############################################################################
# TestCcxtPqByAssetClient1
# #############################################################################


class TestCcxtPqByAssetClient1(icdc.ImClientTestCase):
    """
    For all the test methods see description of corresponding private method in
    the parent class.
    """

    def test_read_data1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbol = "binance::BTC_USDT"
        #
        expected_length = 100
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {"full_symbol": ["binance::BTC_USDT"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(100, 6)
                                         full_symbol     open     high      low    close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.00  6319.04  6310.32  6311.64   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.64  6311.77  6302.81  6302.81  16.781206
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6302.81  6306.00  6292.79  6297.26  55.373226
        ...
        2018-08-17 01:37:00+00:00  binance::BTC_USDT  6346.96  6347.00  6343.00  6343.14  10.787817
        2018-08-17 01:38:00+00:00  binance::BTC_USDT  6345.98  6345.98  6335.04  6339.25  38.197244
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.25  6348.91  6339.00  6342.95  16.394692
        """
        # pylint: enable=line-too-long
        self._test_read_data1(
            im_client,
            full_symbol,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data2(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        #
        expected_length = 199
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(199, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        ...
        2018-08-17 01:38:00+00:00   kucoin::ETH_USDT   292.158945   293.007409   292.158945   293.007409   0.001164
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.250000  6348.910000  6339.000000  6342.950000  16.394692
        2018-08-17 01:39:00+00:00   kucoin::ETH_USDT   292.158945   292.158946   292.158945   292.158946   0.235161
        """
        # pylint: enable=line-too-long
        self._test_read_data2(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data3(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.Timestamp("2018-08-17T00:02:00-00:00")
        #
        expected_length = 196
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:02:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(196, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6302.810000  6306.000000  6292.790000  6297.260000  55.373226
        2018-08-17 00:02:00+00:00   kucoin::ETH_USDT   286.405988   286.405988   285.400193   285.400197   0.162255
        2018-08-17 00:03:00+00:00  binance::BTC_USDT  6299.970000  6299.970000  6286.930000  6294.520000  34.611797
        ...
        2018-08-17 01:38:00+00:00   kucoin::ETH_USDT   292.158945   293.007409   292.158945   293.007409   0.001164
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.250000  6348.910000  6339.000000  6342.950000  16.394692
        2018-08-17 01:39:00+00:00   kucoin::ETH_USDT   292.158945   292.158946   292.158945   292.158946   0.235161
        """
        # pylint: enable=line-too-long
        self._test_read_data3(
            im_client,
            full_symbols,
            start_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data4(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        end_ts = pd.Timestamp("2018-08-17T00:04:00-00:00")
        #
        expected_length = 9
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 00:04:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(9, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        ...
        2018-08-17 00:03:00+00:00   kucoin::ETH_USDT   285.400193   285.400193   285.400193   285.400193   0.020260
        2018-08-17 00:04:00+00:00  binance::BTC_USDT  6294.520000  6299.980000  6290.000000  6296.100000  22.088586
        2018-08-17 00:04:00+00:00   kucoin::ETH_USDT   285.400193   285.884638   285.400193   285.884638   0.074655
        """
        # pylint: enable=line-too-long
        self._test_read_data4(
            im_client,
            full_symbols,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data5(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.Timestamp("2018-08-17T00:01:00-00:00")
        end_ts = pd.Timestamp("2018-08-17T00:04:00-00:00")
        #
        expected_length = 8
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-17 00:04:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(8, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6302.810000  6306.000000  6292.790000  6297.260000  55.373226
        ...
        2018-08-17 00:03:00+00:00   kucoin::ETH_USDT   285.400193   285.400193   285.400193   285.400193   0.020260
        2018-08-17 00:04:00+00:00  binance::BTC_USDT  6294.520000  6299.980000  6290.000000  6296.100000  22.088586
        2018-08-17 00:04:00+00:00   kucoin::ETH_USDT   285.400193   285.884638   285.400193   285.884638   0.074655
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            im_client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data6(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbol = "unsupported_exchange::unsupported_currency"
        self._test_read_data6(im_client, full_symbol)

    def test_read_data7(self) -> None:
        resample_1min = False
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        #
        expected_length = 174
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:00:00+00:00, 2018-08-17 01:39:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(174, 6)
                                         full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:00:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        ...
        2018-08-17 01:38:00+00:00   kucoin::ETH_USDT   292.158945   293.007409   292.158945   293.007409   0.001164
        2018-08-17 01:39:00+00:00  binance::BTC_USDT  6339.250000  6348.910000  6339.000000  6342.950000  16.394692
        2018-08-17 01:39:00+00:00   kucoin::ETH_USDT   292.158945   292.158946   292.158945   292.158946   0.235161
        """
        # pylint: enable=line-too-long
        self._test_read_data7(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    # ////////////////////////////////////////////////////////////////////////

    def test_get_start_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbol = "binance::BTC_USDT"
        expected_start_ts = pd.to_datetime("2018-08-17 00:00:00", utc=True)
        self._test_get_start_ts_for_symbol1(
            im_client, full_symbol, expected_start_ts
        )

    def test_get_end_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        full_symbol = "binance::BTC_USDT"
        expected_end_ts = pd.to_datetime("2018-08-17 01:39:00", utc=True)
        self._test_get_end_ts_for_symbol1(im_client, full_symbol, expected_end_ts)

    # ////////////////////////////////////////////////////////////////////////

    def test_get_universe1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtParquetByAssetClient_example1(
            resample_1min
        )
        expected_length = 3
        expected_first_elements = [
            "binance::BTC_USDT",
            "gateio::XRP_USDT",
            "kucoin::ETH_USDT",
        ]
        expected_last_elements = [
            "binance::BTC_USDT",
            "gateio::XRP_USDT",
            "kucoin::ETH_USDT",
        ]
        self._test_get_universe1(
            im_client,
            expected_length,
            expected_first_elements,
            expected_last_elements,
        )


# #############################################################################
# TestCcxtSqlRealTimeImClient1
# #############################################################################


class TestCcxtSqlRealTimeImClient1(
    icdc.ImClientTestCase, imvcddbut.TestImDbHelper
):
    """
    For all the test methods see description of corresponding private method in
    the parent class.
    """

    _TABLE_NAME = "ccxt_ohlcv_spot"

    # This will be run before and after each test.
    @pytest.fixture(autouse=True)
    def setup_teardown_test(self):
        # Run before each test.
        self.set_up_test()
        yield
        # Run after each test.
        self.tear_down_test()

    def set_up_test(self) -> None:
        self._create_test_table()
        test_data = self._get_test_data()
        hsql.copy_rows_with_copy_from(
            self.connection, test_data, self._TABLE_NAME
        )

    def tear_down_test(self) -> None:
        hsql.remove_table(self.connection, self._TABLE_NAME)

    @classmethod
    def get_id(cls) -> int:
        return hash(cls.__name__) % 10000

    def get_expected_column_names(self) -> List[str]:
        """
        Return a list of expected column names.
        """
        expected_column_names = [
            "id",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "end_download_timestamp",
            "knowledge_timestamp",
            "full_symbol",
        ]
        return expected_column_names

    def test_read_data1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        #
        expected_length = 5
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {"full_symbol": ["binance::BTC_USDT"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:02:00+00:00, 2021-09-09 00:06:00+00:00]
        columns=id,open,high,low,close,volume,end_download_timestamp,knowledge_timestamp,full_symbol
        shape=(5, 9)
                                    id  open  high   low  close  volume    end_download_timestamp       knowledge_timestamp        full_symbol
        timestamp
        2021-09-09 00:02:00+00:00  1.0  30.0  40.0  50.0   60.0    70.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00  2.0  31.0  41.0  51.0   61.0    71.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:04:00+00:00  NaN   NaN   NaN   NaN    NaN     NaN                       NaT                       NaT  binance::BTC_USDT
        2021-09-09 00:05:00+00:00  NaN   NaN   NaN   NaN    NaN     NaN                       NaT                       NaT  binance::BTC_USDT
        2021-09-09 00:06:00+00:00  4.0  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        """
        # pylint: enable=line-too-long
        self._test_read_data1(
            im_client,
            full_symbol,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data2(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        #
        expected_length = 9
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:02:00+00:00, 2021-09-09 00:06:00+00:00]
        columns=id,open,high,low,close,volume,end_download_timestamp,knowledge_timestamp,full_symbol
        shape=(9, 9)
                                    id  open  high   low  close  volume    end_download_timestamp       knowledge_timestamp        full_symbol
        timestamp
        2021-09-09 00:02:00+00:00  1.0  30.0  40.0  50.0   60.0    70.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00  2.0  31.0  41.0  51.0   61.0    71.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00  3.0  32.0  42.0  52.0   62.0    72.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        ...
        2021-09-09 00:05:00+00:00  NaN   NaN   NaN   NaN    NaN     NaN                       NaT                       NaT  binance::ETH_USDT
        2021-09-09 00:06:00+00:00  4.0  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:06:00+00:00  5.0  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        """
        # pylint: enable=line-too-long
        self._test_read_data2(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data3(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        start_ts = pd.Timestamp("2021-09-09T00:02:00-00:00")
        #
        expected_length = 9
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:02:00+00:00, 2021-09-09 00:06:00+00:00]
        columns=id,open,high,low,close,volume,end_download_timestamp,knowledge_timestamp,full_symbol
        shape=(9, 9)
                                    id  open  high   low  close  volume    end_download_timestamp       knowledge_timestamp        full_symbol
        timestamp
        2021-09-09 00:02:00+00:00  1.0  30.0  40.0  50.0   60.0    70.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00  2.0  31.0  41.0  51.0   61.0    71.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00  3.0  32.0  42.0  52.0   62.0    72.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        ...
        2021-09-09 00:05:00+00:00  NaN   NaN   NaN   NaN    NaN     NaN                       NaT                       NaT  binance::ETH_USDT
        2021-09-09 00:06:00+00:00  4.0  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:06:00+00:00  5.0  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        """
        # pylint: enable=line-too-long
        self._test_read_data3(
            im_client,
            full_symbols,
            start_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data4(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        end_ts = pd.Timestamp("2021-09-09T00:04:00-00:00")
        #
        expected_length = 3
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:02:00+00:00, 2021-09-09 00:03:00+00:00]
        columns=id,open,high,low,close,volume,end_download_timestamp,knowledge_timestamp,full_symbol
        shape=(3, 9)
                                id  open  high   low  close  volume    end_download_timestamp       knowledge_timestamp        full_symbol
        timestamp
        2021-09-09 00:02:00+00:00   1  30.0  40.0  50.0   60.0    70.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00   2  31.0  41.0  51.0   61.0    71.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00   3  32.0  42.0  52.0   62.0    72.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        """
        # pylint: enable=line-too-long
        self._test_read_data4(
            im_client,
            full_symbols,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data5(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        start_ts = pd.Timestamp("2021-09-09T00:01:00-00:00")
        end_ts = pd.Timestamp("2021-09-09T00:03:00-00:00")
        #
        expected_length = 3
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:02:00+00:00, 2021-09-09 00:03:00+00:00]
        columns=id,open,high,low,close,volume,end_download_timestamp,knowledge_timestamp,full_symbol
        shape=(3, 9)
                                id  open  high   low  close  volume    end_download_timestamp       knowledge_timestamp        full_symbol
        timestamp
        2021-09-09 00:02:00+00:00   1  30.0  40.0  50.0   60.0    70.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00   2  31.0  41.0  51.0   61.0    71.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00   3  32.0  42.0  52.0   62.0    72.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            im_client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data6(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "unsupported_exchange::unsupported_currency"
        self._test_read_data6(im_client, full_symbol)

    def test_read_data7(self) -> None:
        resample_1min = False
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = [
            "binance::BTC_USDT",
            "binance::ETH_USDT",
            "kucoin::ETH_USDT",
        ]
        #
        expected_length = 6
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": [
                "binance::BTC_USDT",
                "binance::ETH_USDT",
                "kucoin::ETH_USDT",
            ]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""# df=
        index=[2021-09-09 00:02:00+00:00, 2021-09-09 00:06:00+00:00]
        columns=id,open,high,low,close,volume,end_download_timestamp,knowledge_timestamp,full_symbol
        shape=(6, 9)
                                id  open  high   low  close  volume    end_download_timestamp       knowledge_timestamp        full_symbol
        timestamp
        2021-09-09 00:02:00+00:00   1  30.0  40.0  50.0   60.0    70.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00   2  31.0  41.0  51.0   61.0    71.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:03:00+00:00   3  32.0  42.0  52.0   62.0    72.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        2021-09-09 00:05:00+00:00   6  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00   kucoin::ETH_USDT
        2021-09-09 00:06:00+00:00   4  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::BTC_USDT
        2021-09-09 00:06:00+00:00   5  34.0  44.0  54.0   64.0    74.0 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00  binance::ETH_USDT
        """
        # pylint: enable=line-too-long
        self._test_read_data7(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    # ///////////////////////////////////////////////////////////////////////

    def test_repr1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        expected_str = r"""
        <im_v2.ccxt.data.client.ccxt_clients.CcxtSqlRealTimeImClient at 0x>:
            _table_name='ccxt_ohlcv_spot' <str>
            _db_connection='<connection object at 0x; dsn: 'user=aljsdalsd password=xxx dbname=im_postgres_db_local host=xxx port=xxx', closed: 0>' <psycopg2.extensions.connection>
            _vendor='ccxt' <str>
            _universe_version='infer_from_data' <str>
            _resample_1min='True' <bool>
            _timestamp_col_name='timestamp' <str>
            _full_symbol_col_name='None' <NoneType>
            _asset_id_to_full_symbol_mapping= <dict>
                {1464553467: 'binance::ETH_USDT',
                1467591036: 'binance::BTC_USDT',
                3187272957: 'kucoin::ETH_USDT'}
            """
        self.run_test_repr(im_client, expected_str)

    def test_str1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        expected_str = r"""
        CcxtSqlRealTimeImClient at 0x=(_table_name=ccxt_ohlcv_spot <str>, _db_connection=<connection object at 0x; dsn: 'user=aljsdalsd password=xxx dbname=im_postgres_db_local host=xxx port=xxx', closed: 0> <psycopg2.extensions.connection>, _vendor=ccxt <str>, _universe_version=infer_from_data <str>, _resample_1min=True <bool>, _timestamp_col_name=timestamp <str>, _full_symbol_col_name=None <NoneType>, _asset_id_to_full_symbol_mapping={3187272957: 'kucoin::ETH_USDT', 1467591036: 'binance::BTC_USDT', 1464553467: 'binance::ETH_USDT'} <dict>)
        """
        self.run_test_str(im_client, expected_str)

    # ///////////////////////////////////////////////////////////////////////

    def test_get_start_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        expected_start_ts = pd.to_datetime("2021-09-09 00:02:00", utc=True)
        self._test_get_start_ts_for_symbol1(
            im_client, full_symbol, expected_start_ts
        )

    def test_get_end_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        expected_end_ts = pd.to_datetime("2021-09-09 00:06:00", utc=True)
        self._test_get_end_ts_for_symbol1(im_client, full_symbol, expected_end_ts)

    # ///////////////////////////////////////////////////////////////////////

    def test_get_universe1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        expected_length = 3
        expected_first_elements = [
            "kucoin::ETH_USDT",
            "binance::BTC_USDT",
            "binance::ETH_USDT",
        ]
        expected_last_elements = [
            "kucoin::ETH_USDT",
            "binance::BTC_USDT",
            "binance::ETH_USDT",
        ]
        self._test_get_universe1(
            im_client,
            expected_length,
            expected_first_elements,
            expected_last_elements,
        )

    # ///////////////////////////////////////////////////////////////////////
    @pytest.mark.slow
    def test_filter_columns1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        columns = ["full_symbol", "open", "high", "low", "close", "volume"]
        self._test_filter_columns1(im_client, full_symbols, columns)

    @pytest.mark.slow
    def test_filter_columns2(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        columns = ["full_symbol", "whatever"]
        self._test_filter_columns2(im_client, full_symbol, columns)

    @pytest.mark.slow
    def test_filter_columns3(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        columns = ["open", "close"]
        self._test_filter_columns3(im_client, full_symbol, columns)
        # TODO(Juraj): this logic is not correct. When the tests fails somewhere in the middle,
        # the teardown is not ran which means other test cases do not start from an idempotent
        # state and can fail because of unrelated reasons. See `TestCcxtSqlRealTimeImClient2` for fixture implementation.

    # ///////////////////////////////////////////////////////////////////////

    @staticmethod
    def _get_test_data() -> pd.DataFrame:
        """
        Create a test CCXT OHLCV dataframe.
        """
        end_download_timestamp = pd.Timestamp("2021-09-09")
        test_data = pd.DataFrame(
            columns=[
                "id",
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "currency_pair",
                "exchange_id",
                "end_download_timestamp",
                "knowledge_timestamp",
            ],
            # fmt: off
            # pylint: disable=line-too-long
            data=[
                [1, pd.Timestamp("2021-09-09 00:01:00+00:00"), 30, 40, 50, 60, 70, "BTC_USDT", "binance", end_download_timestamp, end_download_timestamp],
                [2, pd.Timestamp("2021-09-09 00:02:00+00:00"), 31, 41, 51, 61, 71, "BTC_USDT", "binance", end_download_timestamp, end_download_timestamp],
                [3, pd.Timestamp("2021-09-09 00:02:00+00:00"), 32, 42, 52, 62, 72, "ETH_USDT", "binance", end_download_timestamp, end_download_timestamp],
                [4, pd.Timestamp("2021-09-09 00:05:00+00:00"), 34, 44, 54, 64, 74, "BTC_USDT", "binance", end_download_timestamp, end_download_timestamp],
                [5, pd.Timestamp("2021-09-09 00:05:00+00:00"), 34, 44, 54, 64, 74, "ETH_USDT", "binance", end_download_timestamp, end_download_timestamp],
                [6, pd.Timestamp("2021-09-09 00:05:00+00:00"), 34, 44, 54, 64, 74, "ETH_USDT", "kucoin", end_download_timestamp, end_download_timestamp],
            ]
            # pylint: enable=line-too-long
            # fmt: on
        )
        test_data["timestamp"] = test_data["timestamp"].apply(
            hdateti.convert_timestamp_to_unix_epoch
        )
        return test_data

    def _create_test_table(self) -> None:
        """
        Create a test CCXT OHLCV table in DB.
        """
        query = imvccdbut.get_ccxt_ohlcv_create_table_query()
        self.connection.cursor().execute(query)


# TODO(Juraj): there is some violation of DRY principle because this is mostly copy paste
# from TestCcxtSqlRealTimeImClient1. Unclear if it is worth to refactor it.
@pytest.mark.slow("Due to the local IM DB setup.")
class TestCcxtSqlRealTimeImClient2(
    icdc.ImClientTestCase, imvcddbut.TestImDbHelper
):
    """
    For all the test methods see description of corresponding private method in
    the parent class.
    """

    _TABLE_NAME = "ccxt_bid_ask_futures_resampled_1min"

    # This will be run before and after each test.
    @pytest.fixture(autouse=True)
    def setup_teardown_table(self):
        # Run before each test.
        self._create_test_table()
        test_data = self._get_test_data()
        hsql.copy_rows_with_copy_from(
            self.connection, test_data, self._TABLE_NAME
        )
        yield
        # Run after each test.
        hsql.remove_table(self.connection, self._TABLE_NAME)

    @classmethod
    def get_id(cls) -> int:
        return hash(cls.__name__) % 10000

    def get_expected_column_names(self) -> List[str]:
        """
        Return a list of expected column names.
        """
        level = 1
        expected_column_names = cofinanc.get_bid_ask_columns_by_level(level) + [
            "end_download_timestamp",
            "full_symbol",
            "knowledge_timestamp",
        ]
        return expected_column_names

    def test_read_data1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        #
        expected_length = 5
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {"full_symbol": ["binance::BTC_USDT"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:01:00+00:00, 2021-09-09 00:05:00+00:00]
        columns=end_download_timestamp,knowledge_timestamp,full_symbol,level_1.bid_size.open,level_1.bid_size.close,level_1.bid_size.min,level_1.bid_size.max,level_1.bid_size.mean,level_1.bid_price.open,level_1.bid_price.close,level_1.bid_price.high,level_1.bid_price.low,level_1.bid_price.mean,level_1.ask_size.open,level_1.ask_size.close,level_1.ask_size.min,level_1.ask_size.max,level_1.ask_size.mean,level_1.ask_price.open,level_1.ask_price.close,level_1.ask_price.high,level_1.ask_price.low,level_1.ask_price.mean,level_1.bid_ask_midpoint.open,level_1.half_spread.open,level_1.log_size_imbalance.open,level_1.bid_ask_midpoint.close,level_1.half_spread.close,level_1.log_size_imbalance.close,level_1.bid_ask_midpoint.min,level_1.half_spread.min,level_1.log_size_imbalance.min,level_1.bid_ask_midpoint.max,level_1.half_spread.max,level_1.log_size_imbalance.max,level_1.bid_ask_midpoint.mean,level_1.half_spread.mean,level_1.log_size_imbalance.mean,level_1.bid_ask_midpoint_var.100ms,level_1.bid_ask_midpoint_autocovar.100ms,level_1.log_size_imbalance_var.100ms,level_1.log_size_imbalance_autocovar.100ms
        shape=(5, 42)
        end_download_timestamp knowledge_timestamp full_symbol level_1.bid_size.open level_1.bid_size.close level_1.bid_size.min level_1.bid_size.max level_1.bid_size.mean level_1.bid_price.open level_1.bid_price.close level_1.bid_price.high level_1.bid_price.low level_1.bid_price.mean level_1.ask_size.open level_1.ask_size.close level_1.ask_size.min level_1.ask_size.max level_1.ask_size.mean level_1.ask_price.open level_1.ask_price.close level_1.ask_price.high level_1.ask_price.low level_1.ask_price.mean level_1.bid_ask_midpoint.open level_1.half_spread.open level_1.log_size_imbalance.open level_1.bid_ask_midpoint.close level_1.half_spread.close level_1.log_size_imbalance.close level_1.bid_ask_midpoint.min level_1.half_spread.min level_1.log_size_imbalance.min level_1.bid_ask_midpoint.max level_1.half_spread.max level_1.log_size_imbalance.max level_1.bid_ask_midpoint.mean level_1.half_spread.mean level_1.log_size_imbalance.mean level_1.bid_ask_midpoint_var.100ms level_1.bid_ask_midpoint_autocovar.100ms level_1.log_size_imbalance_var.100ms level_1.log_size_imbalance_autocovar.100ms
        timestamp
        2021-09-09 00:01:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:03:00+00:00 NaT NaT binance::BTC_USDT NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN
        2021-09-09 00:04:00+00:00 NaT NaT binance::BTC_USDT NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        """
        # pylint: enable=line-too-long
        self._test_read_data1(
            im_client,
            full_symbol,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data2(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        #
        expected_length = 9
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:01:00+00:00, 2021-09-09 00:05:00+00:00]
        columns=end_download_timestamp,knowledge_timestamp,full_symbol,level_1.bid_size.open,level_1.bid_size.close,level_1.bid_size.min,level_1.bid_size.max,level_1.bid_size.mean,level_1.bid_price.open,level_1.bid_price.close,level_1.bid_price.high,level_1.bid_price.low,level_1.bid_price.mean,level_1.ask_size.open,level_1.ask_size.close,level_1.ask_size.min,level_1.ask_size.max,level_1.ask_size.mean,level_1.ask_price.open,level_1.ask_price.close,level_1.ask_price.high,level_1.ask_price.low,level_1.ask_price.mean,level_1.bid_ask_midpoint.open,level_1.half_spread.open,level_1.log_size_imbalance.open,level_1.bid_ask_midpoint.close,level_1.half_spread.close,level_1.log_size_imbalance.close,level_1.bid_ask_midpoint.min,level_1.half_spread.min,level_1.log_size_imbalance.min,level_1.bid_ask_midpoint.max,level_1.half_spread.max,level_1.log_size_imbalance.max,level_1.bid_ask_midpoint.mean,level_1.half_spread.mean,level_1.log_size_imbalance.mean,level_1.bid_ask_midpoint_var.100ms,level_1.bid_ask_midpoint_autocovar.100ms,level_1.log_size_imbalance_var.100ms,level_1.log_size_imbalance_autocovar.100ms
        shape=(9, 42)
        end_download_timestamp knowledge_timestamp full_symbol level_1.bid_size.open level_1.bid_size.close level_1.bid_size.min level_1.bid_size.max level_1.bid_size.mean level_1.bid_price.open level_1.bid_price.close level_1.bid_price.high level_1.bid_price.low level_1.bid_price.mean level_1.ask_size.open level_1.ask_size.close level_1.ask_size.min level_1.ask_size.max level_1.ask_size.mean level_1.ask_price.open level_1.ask_price.close level_1.ask_price.high level_1.ask_price.low level_1.ask_price.mean level_1.bid_ask_midpoint.open level_1.half_spread.open level_1.log_size_imbalance.open level_1.bid_ask_midpoint.close level_1.half_spread.close level_1.log_size_imbalance.close level_1.bid_ask_midpoint.min level_1.half_spread.min level_1.log_size_imbalance.min level_1.bid_ask_midpoint.max level_1.half_spread.max level_1.log_size_imbalance.max level_1.bid_ask_midpoint.mean level_1.half_spread.mean level_1.log_size_imbalance.mean level_1.bid_ask_midpoint_var.100ms level_1.bid_ask_midpoint_autocovar.100ms level_1.log_size_imbalance_var.100ms level_1.log_size_imbalance_autocovar.100ms
        timestamp
        2021-09-09 00:01:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        ...
        2021-09-09 00:04:00+00:00 NaT NaT binance::ETH_USDT NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        """
        # pylint: enable=line-too-long
        self._test_read_data2(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data3(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        start_ts = pd.Timestamp("2021-09-09T00:01:00-00:00")
        #
        expected_length = 9
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:01:00+00:00, 2021-09-09 00:05:00+00:00]
        columns=end_download_timestamp,knowledge_timestamp,full_symbol,level_1.bid_size.open,level_1.bid_size.close,level_1.bid_size.min,level_1.bid_size.max,level_1.bid_size.mean,level_1.bid_price.open,level_1.bid_price.close,level_1.bid_price.high,level_1.bid_price.low,level_1.bid_price.mean,level_1.ask_size.open,level_1.ask_size.close,level_1.ask_size.min,level_1.ask_size.max,level_1.ask_size.mean,level_1.ask_price.open,level_1.ask_price.close,level_1.ask_price.high,level_1.ask_price.low,level_1.ask_price.mean,level_1.bid_ask_midpoint.open,level_1.half_spread.open,level_1.log_size_imbalance.open,level_1.bid_ask_midpoint.close,level_1.half_spread.close,level_1.log_size_imbalance.close,level_1.bid_ask_midpoint.min,level_1.half_spread.min,level_1.log_size_imbalance.min,level_1.bid_ask_midpoint.max,level_1.half_spread.max,level_1.log_size_imbalance.max,level_1.bid_ask_midpoint.mean,level_1.half_spread.mean,level_1.log_size_imbalance.mean,level_1.bid_ask_midpoint_var.100ms,level_1.bid_ask_midpoint_autocovar.100ms,level_1.log_size_imbalance_var.100ms,level_1.log_size_imbalance_autocovar.100ms
        shape=(9, 42)
        end_download_timestamp knowledge_timestamp full_symbol level_1.bid_size.open level_1.bid_size.close level_1.bid_size.min level_1.bid_size.max level_1.bid_size.mean level_1.bid_price.open level_1.bid_price.close level_1.bid_price.high level_1.bid_price.low level_1.bid_price.mean level_1.ask_size.open level_1.ask_size.close level_1.ask_size.min level_1.ask_size.max level_1.ask_size.mean level_1.ask_price.open level_1.ask_price.close level_1.ask_price.high level_1.ask_price.low level_1.ask_price.mean level_1.bid_ask_midpoint.open level_1.half_spread.open level_1.log_size_imbalance.open level_1.bid_ask_midpoint.close level_1.half_spread.close level_1.log_size_imbalance.close level_1.bid_ask_midpoint.min level_1.half_spread.min level_1.log_size_imbalance.min level_1.bid_ask_midpoint.max level_1.half_spread.max level_1.log_size_imbalance.max level_1.bid_ask_midpoint.mean level_1.half_spread.mean level_1.log_size_imbalance.mean level_1.bid_ask_midpoint_var.100ms level_1.bid_ask_midpoint_autocovar.100ms level_1.log_size_imbalance_var.100ms level_1.log_size_imbalance_autocovar.100ms
        timestamp
        2021-09-09 00:01:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        ...
        2021-09-09 00:04:00+00:00 NaT NaT binance::ETH_USDT NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN NaN
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        """
        # pylint: enable=line-too-long
        self._test_read_data3(
            im_client,
            full_symbols,
            start_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data4(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        end_ts = pd.Timestamp("2021-09-09T00:03:00-00:00")
        #
        expected_length = 3
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:01:00+00:00, 2021-09-09 00:02:00+00:00]
        columns=end_download_timestamp,knowledge_timestamp,full_symbol,level_1.bid_size.open,level_1.bid_size.close,level_1.bid_size.min,level_1.bid_size.max,level_1.bid_size.mean,level_1.bid_price.open,level_1.bid_price.close,level_1.bid_price.high,level_1.bid_price.low,level_1.bid_price.mean,level_1.ask_size.open,level_1.ask_size.close,level_1.ask_size.min,level_1.ask_size.max,level_1.ask_size.mean,level_1.ask_price.open,level_1.ask_price.close,level_1.ask_price.high,level_1.ask_price.low,level_1.ask_price.mean,level_1.bid_ask_midpoint.open,level_1.half_spread.open,level_1.log_size_imbalance.open,level_1.bid_ask_midpoint.close,level_1.half_spread.close,level_1.log_size_imbalance.close,level_1.bid_ask_midpoint.min,level_1.half_spread.min,level_1.log_size_imbalance.min,level_1.bid_ask_midpoint.max,level_1.half_spread.max,level_1.log_size_imbalance.max,level_1.bid_ask_midpoint.mean,level_1.half_spread.mean,level_1.log_size_imbalance.mean,level_1.bid_ask_midpoint_var.100ms,level_1.bid_ask_midpoint_autocovar.100ms,level_1.log_size_imbalance_var.100ms,level_1.log_size_imbalance_autocovar.100ms
        shape=(3, 42)
        end_download_timestamp knowledge_timestamp full_symbol level_1.bid_size.open level_1.bid_size.close level_1.bid_size.min level_1.bid_size.max level_1.bid_size.mean level_1.bid_price.open level_1.bid_price.close level_1.bid_price.high level_1.bid_price.low level_1.bid_price.mean level_1.ask_size.open level_1.ask_size.close level_1.ask_size.min level_1.ask_size.max level_1.ask_size.mean level_1.ask_price.open level_1.ask_price.close level_1.ask_price.high level_1.ask_price.low level_1.ask_price.mean level_1.bid_ask_midpoint.open level_1.half_spread.open level_1.log_size_imbalance.open level_1.bid_ask_midpoint.close level_1.half_spread.close level_1.log_size_imbalance.close level_1.bid_ask_midpoint.min level_1.half_spread.min level_1.log_size_imbalance.min level_1.bid_ask_midpoint.max level_1.half_spread.max level_1.log_size_imbalance.max level_1.bid_ask_midpoint.mean level_1.half_spread.mean level_1.log_size_imbalance.mean level_1.bid_ask_midpoint_var.100ms level_1.bid_ask_midpoint_autocovar.100ms level_1.log_size_imbalance_var.100ms level_1.log_size_imbalance_autocovar.100ms
        timestamp
        2021-09-09 00:01:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        """
        # pylint: enable=line-too-long
        self._test_read_data4(
            im_client,
            full_symbols,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data5(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = ["binance::BTC_USDT", "binance::ETH_USDT"]
        start_ts = pd.Timestamp("2021-09-09T00:01:00-00:00")
        end_ts = pd.Timestamp("2021-09-09T00:03:00-00:00")
        #
        expected_length = 3
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "binance::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:01:00+00:00, 2021-09-09 00:02:00+00:00]
        columns=end_download_timestamp,knowledge_timestamp,full_symbol,level_1.bid_size.open,level_1.bid_size.close,level_1.bid_size.min,level_1.bid_size.max,level_1.bid_size.mean,level_1.bid_price.open,level_1.bid_price.close,level_1.bid_price.high,level_1.bid_price.low,level_1.bid_price.mean,level_1.ask_size.open,level_1.ask_size.close,level_1.ask_size.min,level_1.ask_size.max,level_1.ask_size.mean,level_1.ask_price.open,level_1.ask_price.close,level_1.ask_price.high,level_1.ask_price.low,level_1.ask_price.mean,level_1.bid_ask_midpoint.open,level_1.half_spread.open,level_1.log_size_imbalance.open,level_1.bid_ask_midpoint.close,level_1.half_spread.close,level_1.log_size_imbalance.close,level_1.bid_ask_midpoint.min,level_1.half_spread.min,level_1.log_size_imbalance.min,level_1.bid_ask_midpoint.max,level_1.half_spread.max,level_1.log_size_imbalance.max,level_1.bid_ask_midpoint.mean,level_1.half_spread.mean,level_1.log_size_imbalance.mean,level_1.bid_ask_midpoint_var.100ms,level_1.bid_ask_midpoint_autocovar.100ms,level_1.log_size_imbalance_var.100ms,level_1.log_size_imbalance_autocovar.100ms
        shape=(3, 42)
        end_download_timestamp knowledge_timestamp full_symbol level_1.bid_size.open level_1.bid_size.close level_1.bid_size.min level_1.bid_size.max level_1.bid_size.mean level_1.bid_price.open level_1.bid_price.close level_1.bid_price.high level_1.bid_price.low level_1.bid_price.mean level_1.ask_size.open level_1.ask_size.close level_1.ask_size.min level_1.ask_size.max level_1.ask_size.mean level_1.ask_price.open level_1.ask_price.close level_1.ask_price.high level_1.ask_price.low level_1.ask_price.mean level_1.bid_ask_midpoint.open level_1.half_spread.open level_1.log_size_imbalance.open level_1.bid_ask_midpoint.close level_1.half_spread.close level_1.log_size_imbalance.close level_1.bid_ask_midpoint.min level_1.half_spread.min level_1.log_size_imbalance.min level_1.bid_ask_midpoint.max level_1.half_spread.max level_1.log_size_imbalance.max level_1.bid_ask_midpoint.mean level_1.half_spread.mean level_1.log_size_imbalance.mean level_1.bid_ask_midpoint_var.100ms level_1.bid_ask_midpoint_autocovar.100ms level_1.log_size_imbalance_var.100ms level_1.log_size_imbalance_autocovar.100ms
        timestamp
        2021-09-09 00:01:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            im_client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data6(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "unsupported_exchange::unsupported_currency"
        self._test_read_data6(im_client, full_symbol)

    def test_read_data7(self) -> None:
        resample_1min = False
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbols = [
            "binance::BTC_USDT",
            "binance::ETH_USDT",
            "kucoin::ETH_USDT",
        ]
        #
        expected_length = 6
        expected_column_names = self.get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": [
                "binance::BTC_USDT",
                "binance::ETH_USDT",
                "kucoin::ETH_USDT",
            ]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2021-09-09 00:01:00+00:00, 2021-09-09 00:05:00+00:00]
        columns=end_download_timestamp,knowledge_timestamp,full_symbol,level_1.bid_size.open,level_1.bid_size.close,level_1.bid_size.min,level_1.bid_size.max,level_1.bid_size.mean,level_1.bid_price.open,level_1.bid_price.close,level_1.bid_price.high,level_1.bid_price.low,level_1.bid_price.mean,level_1.ask_size.open,level_1.ask_size.close,level_1.ask_size.min,level_1.ask_size.max,level_1.ask_size.mean,level_1.ask_price.open,level_1.ask_price.close,level_1.ask_price.high,level_1.ask_price.low,level_1.ask_price.mean,level_1.bid_ask_midpoint.open,level_1.half_spread.open,level_1.log_size_imbalance.open,level_1.bid_ask_midpoint.close,level_1.half_spread.close,level_1.log_size_imbalance.close,level_1.bid_ask_midpoint.min,level_1.half_spread.min,level_1.log_size_imbalance.min,level_1.bid_ask_midpoint.max,level_1.half_spread.max,level_1.log_size_imbalance.max,level_1.bid_ask_midpoint.mean,level_1.half_spread.mean,level_1.log_size_imbalance.mean,level_1.bid_ask_midpoint_var.100ms,level_1.bid_ask_midpoint_autocovar.100ms,level_1.log_size_imbalance_var.100ms,level_1.log_size_imbalance_autocovar.100ms
        shape=(6, 42)
        end_download_timestamp knowledge_timestamp full_symbol level_1.bid_size.open level_1.bid_size.close level_1.bid_size.min level_1.bid_size.max level_1.bid_size.mean level_1.bid_price.open level_1.bid_price.close level_1.bid_price.high level_1.bid_price.low level_1.bid_price.mean level_1.ask_size.open level_1.ask_size.close level_1.ask_size.min level_1.ask_size.max level_1.ask_size.mean level_1.ask_price.open level_1.ask_price.close level_1.ask_price.high level_1.ask_price.low level_1.ask_price.mean level_1.bid_ask_midpoint.open level_1.half_spread.open level_1.log_size_imbalance.open level_1.bid_ask_midpoint.close level_1.half_spread.close level_1.log_size_imbalance.close level_1.bid_ask_midpoint.min level_1.half_spread.min level_1.log_size_imbalance.min level_1.bid_ask_midpoint.max level_1.half_spread.max level_1.log_size_imbalance.max level_1.bid_ask_midpoint.mean level_1.half_spread.mean level_1.log_size_imbalance.mean level_1.bid_ask_midpoint_var.100ms level_1.bid_ask_midpoint_autocovar.100ms level_1.log_size_imbalance_var.100ms level_1.log_size_imbalance_autocovar.100ms
        timestamp
        2021-09-09 00:01:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:02:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::BTC_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 binance::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        2021-09-09 00:05:00+00:00 2021-09-09 00:00:00+00:00 2021-09-09 00:00:00+00:00 kucoin::ETH_USDT 11.0 21.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 61.0 71.0 31.0 41.0 51.0 5.0 10.0 15.0 20.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0 60.0 30.0 40.0 50.0
        """
        # pylint: enable=line-too-long
        self._test_read_data7(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    # ///////////////////////////////////////////////////////////////////////

    def test_get_start_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        # Only OHLCV 1 minute data get the +1 minute adjustment. Bid/ask resampling
        # is done by us before inserting, with correct labels.
        expected_start_ts = pd.to_datetime("2021-09-09 00:01:00", utc=True)
        self._test_get_start_ts_for_symbol1(
            im_client, full_symbol, expected_start_ts
        )

    def test_get_end_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        # Only OHLCV 1 minute data get the +1 minute adjustment. Bid/ask resampling
        # is done by us before inserting, with correct labels.
        expected_end_ts = pd.to_datetime("2021-09-09 00:05:00", utc=True)
        self._test_get_end_ts_for_symbol1(im_client, full_symbol, expected_end_ts)

    # ///////////////////////////////////////////////////////////////////////

    def test_get_universe1(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        expected_length = 3
        expected_first_elements = [
            "kucoin::ETH_USDT",
            "binance::BTC_USDT",
            "binance::ETH_USDT",
        ]
        expected_last_elements = [
            "kucoin::ETH_USDT",
            "binance::BTC_USDT",
            "binance::ETH_USDT",
        ]
        self._test_get_universe1(
            im_client,
            expected_length,
            expected_first_elements,
            expected_last_elements,
        )

    # ///////////////////////////////////////////////////////////////////////
    def test_filter_columns2(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        columns = ["full_symbol", "whatever"]
        self._test_filter_columns2(im_client, full_symbol, columns)

    def test_filter_columns3(self) -> None:
        resample_1min = True
        im_client = imvcdcccex.get_CcxtSqlRealTimeImClient_example2(
            self.connection, resample_1min, self._TABLE_NAME
        )
        full_symbol = "binance::BTC_USDT"
        columns = [
            "level_1.bid_size.close",
            "level_1.bid_size.min",
            "level_1.bid_size.max",
            "level_1.bid_size.mean",
        ]
        self._test_filter_columns3(im_client, full_symbol, columns)

    def _get_test_data(self) -> pd.DataFrame:
        """
        Create a test CCXT OHLCV dataframe.
        """
        end_download_timestamp = pd.Timestamp("2021-09-09")
        # DB data is collected in long format
        test_data = pd.DataFrame(
            columns=[
                "id",
                "timestamp",
                "bid_size_open",
                "bid_size_close",
                "bid_size_min",
                "bid_size_max",
                "bid_size_mean",
                "bid_price_open",
                "bid_price_close",
                "bid_price_high",
                "bid_price_low",
                "bid_price_mean",
                "ask_size_open",
                "ask_size_close",
                "ask_size_min",
                "ask_size_max",
                "ask_size_mean",
                "ask_price_open",
                "ask_price_close",
                "ask_price_high",
                "ask_price_low",
                "ask_price_mean",
                "bid_ask_midpoint_open",
                "half_spread_open",
                "log_size_imbalance_open",
                "bid_ask_midpoint_close",
                "half_spread_close",
                "log_size_imbalance_close",
                "bid_ask_midpoint_min",
                "half_spread_min",
                "log_size_imbalance_min",
                "bid_ask_midpoint_max",
                "half_spread_max",
                "log_size_imbalance_max",
                "bid_ask_midpoint_mean",
                "half_spread_mean",
                "log_size_imbalance_mean",
                "bid_ask_midpoint_var_100ms",
                "bid_ask_midpoint_autocovar_100ms",
                "log_size_imbalance_var_100ms",
                "log_size_imbalance_autocovar_100ms",
                "currency_pair",
                "exchange_id",
                "level",
                "end_download_timestamp",
                "knowledge_timestamp",
            ],
            # fmt: off
            # pylint: disable=line-too-long
            data=[
                [1, pd.Timestamp("2021-09-09 00:01:00+00:00"), 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, "BTC_USDT", "binance", 1, end_download_timestamp, end_download_timestamp],
                [2, pd.Timestamp("2021-09-09 00:02:00+00:00"), 11, 21, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, "BTC_USDT", "binance", 1, end_download_timestamp, end_download_timestamp],
                [3, pd.Timestamp("2021-09-09 00:02:00+00:00"), 11, 21, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, "ETH_USDT", "binance", 1, end_download_timestamp, end_download_timestamp],
                [4, pd.Timestamp("2021-09-09 00:05:00+00:00"), 11, 21, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, "BTC_USDT", "binance", 1, end_download_timestamp, end_download_timestamp],
                [5, pd.Timestamp("2021-09-09 00:05:00+00:00"), 11, 21, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, "ETH_USDT", "binance", 1, end_download_timestamp, end_download_timestamp],
                [6, pd.Timestamp("2021-09-09 00:05:00+00:00"), 11, 21, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 61, 71, 31, 41, 51, 5, 10, 15, 20, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, 60, 30, 40, 50, "ETH_USDT", "kucoin", 1, end_download_timestamp, end_download_timestamp],
            ]
            # pylint: enable=line-too-long
            # fmt: on
        )
        test_data["timestamp"] = test_data["timestamp"].apply(
            hdateti.convert_timestamp_to_unix_epoch
        )
        return test_data

    def _create_test_table(self) -> None:
        """
        Create a test CCXT OHLCV table in DB.
        """
        query = (
            imvccdbut.get_ccxt_create_bid_ask_futures_resampled_1min_table_query()
        )
        self.connection.cursor().execute(query)


# #############################################################################
# TestCcxtHistoricalPqByTileClient1
# #############################################################################


@pytest.mark.requires_aws
@pytest.mark.requires_ck_infra
class TestCcxtHistoricalPqByTileClient1(icdc.ImClientTestCase):
    """
    For all the test methods see description of corresponding private method in
    the parent class.
    """

    def get_im_client(
        self, resample_1min: bool
    ) -> imvcdccccl.CcxtHistoricalPqByTileClient:
        """
        Get `CcxtHistoricalPqByTileClient` based on data from S3.

        :param resample_1min: whether to resample data to 1 minute or
            not
        :return: Ccxt historical client
        """
        use_only_test_class = True
        s3_input_dir = self.get_s3_input_dir(
            use_only_test_class=use_only_test_class
        )
        root_dir = os.path.join(s3_input_dir, "historical.manual.pq")
        im_client = imvcdcccex.get_CcxtHistoricalPqByTileClient_example2(
            root_dir, resample_1min
        )
        return im_client

    @pytest.mark.requires_aws
    @pytest.mark.requires_ck_infra
    def test_read_data1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "binance::BTC_USDT"
        #
        expected_length = 2881
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {"full_symbol": ["binance::BTC_USDT"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-19 00:01:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(2881, 6)
                                        full_symbol     open     high      low    close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6316.00  6319.04  6310.32  6311.64   9.967395
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6311.64  6311.77  6302.81  6302.81  16.781206
        2018-08-17 00:03:00+00:00  binance::BTC_USDT  6302.81  6306.00  6292.79  6297.26  55.373226
        ...
        2018-08-18 23:59:00+00:00  binance::BTC_USDT  6385.48  6390.00  6385.48  6387.01  37.459319
        2018-08-19 00:00:00+00:00  binance::BTC_USDT  6390.00  6390.00  6386.82  6387.96  10.584910
        2018-08-19 00:01:00+00:00  binance::BTC_USDT  6387.96  6387.97  6375.64  6377.25  39.426236
        """
        # pylint: enable=line-too-long
        self._test_read_data1(
            im_client,
            full_symbol,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    @pytest.mark.slow("Slow via GH, but fast on the server")
    def test_read_data2(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        #
        expected_length = 5761
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-19 00:01:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(5761, 6)
                                        full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        ...
        2018-08-19 00:00:00+00:00  binance::BTC_USDT  6390.000000  6390.00  6386.820000  6387.96  10.584910
        2018-08-19 00:00:00+00:00   kucoin::ETH_USDT   293.870469   294.00   293.870469   294.00   0.704782
        2018-08-19 00:01:00+00:00  binance::BTC_USDT  6387.960000  6387.97  6375.640000  6377.25  39.426236
        """
        # pylint: enable=line-too-long
        self._test_read_data2(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    @pytest.mark.slow("Slow via GH, but fast on the server")
    def test_read_data3(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.Timestamp("2018-08-18T00:23:00-00:00")
        #
        expected_length = 2837
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-18 00:23:00+00:00, 2018-08-19 00:01:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(2837, 6)
                                        full_symbol         open         high          low        close     volume
        timestamp
        2018-08-18 00:23:00+00:00  binance::BTC_USDT  6564.160000  6570.830000  6561.940000  6570.830000  71.756629
        2018-08-18 00:23:00+00:00   kucoin::ETH_USDT   316.138881   316.138881   316.021676   316.021676   0.800971
        2018-08-18 00:24:00+00:00  binance::BTC_USDT  6570.830000  6573.800000  6567.980000  6573.800000  43.493238
        ...
        2018-08-19 00:00:00+00:00  binance::BTC_USDT  6390.000000  6390.00  6386.820000  6387.96  10.584910
        2018-08-19 00:00:00+00:00   kucoin::ETH_USDT   293.870469   294.00   293.870469   294.00   0.704782
        2018-08-19 00:01:00+00:00  binance::BTC_USDT  6387.960000  6387.97  6375.640000  6377.25  39.426236
        """
        # pylint: enable=line-too-long
        self._test_read_data3(
            im_client,
            full_symbols,
            start_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    @pytest.mark.slow("Slow via GH, but fast on the server")
    def test_read_data4(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        end_ts = pd.Timestamp("2018-08-17T00:04:00-00:00")
        #
        expected_length = 8
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-17 00:04:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(8, 6)
                                        full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        ...
        2018-08-17 00:03:00+00:00   kucoin::ETH_USDT   285.400193   285.400193   285.400193   285.400193   0.020260
        2018-08-17 00:04:00+00:00  binance::BTC_USDT  6299.970000  6299.970000  6286.930000  6294.520000  34.611797
        2018-08-17 00:04:00+00:00   kucoin::ETH_USDT   285.400193   285.884638   285.400193   285.884638   0.074655
        """
        # pylint: enable=line-too-long
        self._test_read_data4(
            im_client,
            full_symbols,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    @pytest.mark.slow("Slow via GH, but fast on the server")
    def test_read_data5(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.Timestamp("2018-08-17T00:01:00-00:00")
        end_ts = pd.Timestamp("2018-08-17T00:04:00-00:00")
        #
        expected_length = 8
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["binance::BTC_USDT", "kucoin::ETH_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-17 00:04:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(8, 6)
                                        full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        ...
        2018-08-17 00:03:00+00:00   kucoin::ETH_USDT   285.400193   285.400193   285.400193   285.400193   0.020260
        2018-08-17 00:04:00+00:00  binance::BTC_USDT  6299.970000  6299.970000  6286.930000  6294.520000  34.611797
        2018-08-17 00:04:00+00:00   kucoin::ETH_USDT   285.400193   285.884638   285.400193   285.884638   0.074655
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            im_client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_data6(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "unsupported_exchange::unsupported_currency"
        self._test_read_data6(im_client, full_symbol)

    @pytest.mark.slow("Slow via GH, but fast on the server")
    def test_read_data7(self) -> None:
        resample_1min = False
        im_client = self.get_im_client(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        #
        expected_length = 4791
        expected_column_names = get_expected_column_names()
        expected_column_unique_values = {
            "full_symbol": ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        }
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2018-08-17 00:01:00+00:00, 2018-08-19 00:01:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(4791, 6)
                                        full_symbol         open         high          low        close     volume
        timestamp
        2018-08-17 00:01:00+00:00  binance::BTC_USDT  6316.000000  6319.040000  6310.320000  6311.640000   9.967395
        2018-08-17 00:01:00+00:00   kucoin::ETH_USDT   286.712987   286.712987   286.712987   286.712987   0.017500
        2018-08-17 00:02:00+00:00  binance::BTC_USDT  6311.640000  6311.770000  6302.810000  6302.810000  16.781206
        ...
        2018-08-19 00:00:00+00:00  binance::BTC_USDT  6390.000000  6390.00  6386.820000  6387.96  10.584910
        2018-08-19 00:00:00+00:00   kucoin::ETH_USDT   293.870469   294.00   293.870469   294.00   0.704782
        2018-08-19 00:01:00+00:00  binance::BTC_USDT  6387.960000  6387.97  6375.640000  6377.25  39.426236
        """
        # pylint: enable=line-too-long
        self._test_read_data7(
            im_client,
            full_symbols,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    # ////////////////////////////////////////////////////////////////////////

    def test_repr1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        expected_str = r"""
        <im_v2.ccxt.data.client.ccxt_clients.CcxtHistoricalPqByTileClient at 0x>:
            _vendor='CCXT' <str>
            _universe_version='small' <str>
            _resample_1min='True' <bool>
            _timestamp_col_name='timestamp' <str>
            _full_symbol_col_name='None' <NoneType>
            _asset_id_to_full_symbol_mapping= <dict>
                {1467591036: 'binance::BTC_USDT',
                2002879833: 'gateio::XRP_USDT',
                3187272957: 'kucoin::ETH_USDT'}
            _root_dir='s3://cryptokaizen-unit-test/outcomes/TestCcxtHistoricalPqByTileClient1/input/historical.manual.pq' <str>
            _infer_exchange_id='True' <bool>
            _partition_mode='by_year_month' <str>
            _aws_profile='ck' <str>
            _dataset='ohlcv' <str>
            _contract_type='spot' <str>
            _data_snapshot='20220705' <str>
            _download_mode='periodic_daily' <str>
            _downloading_entity='airflow' <str>
            _version='' <str>
            _download_universe_version='v7_3' <str>
            _tag='' <str>
            _data_format='parquet' <str>
        """
        self.run_test_repr(im_client, expected_str)

    def test_str1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        expected_str = r"""
        CcxtHistoricalPqByTileClient at 0x=(_vendor=CCXT <str>, _universe_version=small <str>, _resample_1min=True <bool>, _timestamp_col_name=timestamp <str>, _full_symbol_col_name=None <NoneType>, _asset_id_to_full_symbol_mapping={1467591036: 'binance::BTC_USDT', 2002879833: 'gateio::XRP_USDT', 3187272957: 'kucoin::ETH_USDT'} <dict>, _root_dir=s3://cryptokaizen-unit-test/outcomes/TestCcxtHistoricalPqByTileClient1/input/historical.manual.pq <str>, _infer_exchange_id=True <bool>, _partition_mode=by_year_month <str>, _aws_profile=ck <str>, _dataset=ohlcv <str>, _contract_type=spot <str>, _data_snapshot=20220705 <str>, _download_mode=periodic_daily <str>, _downloading_entity=airflow <str>, _version= <str>, _download_universe_version=v7_3 <str>, _tag= <str>, _data_format=parquet <str>)
        """
        self.run_test_str(im_client, expected_str)

    # ////////////////////////////////////////////////////////////////////////

    # TODO(gp): Difference between cmamp1 and sorrentum. Why is there a
    # difference?
    @pytest.mark.slow("Slow via GH, but fast on the server")
    def test_filter_columns1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        columns = ["full_symbol", "open", "close"]
        self._test_filter_columns1(im_client, full_symbols, columns)

    def test_filter_columns2(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "binance::BTC_USDT"
        columns = ["full_symbol", "whatever"]
        self._test_filter_columns2(im_client, full_symbol, columns)

    @pytest.mark.skip(
        reason="AssertionError: AssertionError not raised. See CmTask4608."
    )
    def test_filter_columns3(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "binance::BTC_USDT"
        columns = ["open", "close"]
        self._test_filter_columns3(im_client, full_symbol, columns)

    @pytest.mark.skip("Full symbol should not be returned. See CmTask4608.")
    def test_filter_columns4(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "binance::BTC_USDT"
        columns = ["open", "close"]
        self._test_filter_columns4(
            im_client,
            full_symbol,
            columns,
        )

    # ////////////////////////////////////////////////////////////////////////

    @pytest.mark.requires_aws
    @pytest.mark.requires_ck_infra
    def test_get_start_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "binance::BTC_USDT"
        expected_start_ts = pd.to_datetime("2018-08-17 00:01:00", utc=True)
        self._test_get_start_ts_for_symbol1(
            im_client, full_symbol, expected_start_ts
        )

    @pytest.mark.requires_aws
    @pytest.mark.requires_ck_infra
    def test_get_end_ts_for_symbol1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        full_symbol = "binance::BTC_USDT"
        expected_end_ts = pd.to_datetime("2018-08-19 00:01:00", utc=True)
        self._test_get_end_ts_for_symbol1(im_client, full_symbol, expected_end_ts)

    # ////////////////////////////////////////////////////////////////////////

    def test_get_universe1(self) -> None:
        resample_1min = True
        im_client = self.get_im_client(resample_1min)
        expected_length = 3
        expected_first_elements = [
            "binance::BTC_USDT",
            "gateio::XRP_USDT",
            "kucoin::ETH_USDT",
        ]
        expected_last_elements = [
            "binance::BTC_USDT",
            "gateio::XRP_USDT",
            "kucoin::ETH_USDT",
        ]
        self._test_get_universe1(
            im_client,
            expected_length,
            expected_first_elements,
            expected_last_elements,
        )

    # ////////////////////////////////////////////////////////////////////////
    # TODO(gp): Do not commit this!
    @pytest.mark.skip("Enable when unit test data needs to be generated.")
    def test_write_test_data_to_s3(self) -> None:
        """
        Write unit test data to S3.
        """
        data = self._get_unit_test_data()
        partition_columns = ["currency_pair", "year", "month"]
        use_only_test_class = True
        s3_input_dir = self.get_s3_input_dir(
            use_only_test_class=use_only_test_class
        )
        dst_dir = os.path.join(
            s3_input_dir,
            "historical.manual.pq",
            "20220705",
            "ohlcv",
            "ccxt",
        )
        exchange_id_col_name = "exchange_id"
        for exchange_id, df_exchange_id in data.groupby(exchange_id_col_name):
            exchange_dir = os.path.join(dst_dir, exchange_id)
            df_exchange_id = df_exchange_id.drop(columns="exchange_id")
            hparque.to_partitioned_parquet(
                df_exchange_id,
                partition_columns,
                exchange_dir,
                aws_profile=aws_profile,
            )

    def _get_unit_test_data(self) -> pd.DataFrame:
        """
        Get small part of historical data from S3 for unit testing.

        Implemented transformations:
        - Add necessary columns for partitioning
        - Remove unnecessary column
        - Cut the data so that is light-weight enough for testing
        - Create gaps in data to test resampling

        return: data to be loaded to S3
        """
        universe_version = "v4"
        dataset = "ohlcv"
        contract_type = "spot"
        data_snapshot = "20220705"
        im_client = imvcdcccex.get_CcxtHistoricalPqByTileClient_example1(
            universe_version, dataset, contract_type, data_snapshot
        )
        full_symbols = ["kucoin::ETH_USDT", "binance::BTC_USDT"]
        start_ts = pd.to_datetime("2018-08-17 00:00:00", utc=True)
        end_ts = pd.to_datetime("2018-08-19 00:00:00", utc=True)
        columns = None
        filter_data_mode = "assert"
        data = im_client.read_data(
            full_symbols, start_ts, end_ts, columns, filter_data_mode
        )
        # Add missing columns.
        data["exchange_id"], data["currency_pair"] = ivcu.parse_full_symbol(
            data["full_symbol"]
        )
        data["year"] = data.index.year
        data["month"] = data.index.month
        # Add "timestamp" column to make test data with same columns as historical.
        timestamp_col = [1569888000000] * len(data)
        data.insert(0, "timestamp", timestamp_col)
        # Remove unnecessary column.
        data = data.drop(columns="full_symbol")
        # Artificially create gaps in data in order test resampling.
        data = pd.concat([data[:100], data[115:]])
        return data
