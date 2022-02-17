import os

import pandas as pd

import helpers.hdbg as hdbg
import helpers.hgit as hgit
import helpers.hunit_test as hunitest
import im_v2.kibot.data.client.kibot_clients as imvkdckicl


def get_test_data_dir() -> str:
    """
    Get dir with data files for the tests.

    The files in the dir are copies of some Kibot data files from S3
    that were loaded for our research purposes. These copies are checked
    out locally in order to test functions without dependencies on S3.
    """
    test_data_dir = os.path.join(
        hgit.get_amp_abs_path(),
        "im_v2/kibot/data/client/test/test_data",
    )
    hdbg.dassert_dir_exists(test_data_dir)
    return test_data_dir


class TestKibotEquitiesCsvParquetByAssetClient(hunitest.TestCase):
    def test_read_data1(self) -> None:
        root_dir = get_test_data_dir()
        extension = "csv.gz"
        asset_class = "stocks"
        unadjusted = False
        full_symbols = ["Unknown::HD"]
        start_ts = pd.Timestamp("2015-09-29T09:23:00+00:00")
        end_ts = pd.Timestamp("2015-09-29T09:35:00+00:00")
        #
        client = imvkdckicl.KibotEquitiesCsvParquetByAssetClient(
            root_dir,
            extension,
            asset_class,
            unadjusted,
        )
        actual_df = client.read_data(full_symbols, start_ts, end_ts)
        #
        expected_length = 13
        expected_column_names = [
            "full_symbol", "open", "high", "low", "close", "volume"
        ]
        expected_column_unique_values = {"full_symbol": ["Unknown::HD"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2015-09-29 09:23:00+00:00, 2015-09-29 09:35:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(13, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp                                                                     
        2015-09-29 09:23:00+00:00  Unknown::HD  102.36  102.36  102.36  102.36   447.0
        2015-09-29 09:24:00+00:00  Unknown::HD     NaN     NaN     NaN     NaN     NaN
        2015-09-29 09:25:00+00:00  Unknown::HD     NaN     NaN     NaN     NaN     NaN
        ...
        2015-09-29 09:33:00+00:00  Unknown::HD  102.17  102.21  102.08  102.17  15277.0
        2015-09-29 09:34:00+00:00  Unknown::HD  102.17  102.33  102.16  102.33   6145.0
        2015-09-29 09:35:00+00:00  Unknown::HD  102.39  102.49  102.12  102.15  19620.0
        """
        # pylint: enable=line-too-long
        self.check_df_output(
            actual_df,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature
        )

    def test_read_data2(self) -> None:
        root_dir = get_test_data_dir()
        extension = "pq"
        asset_class = "stocks"
        unadjusted = False
        full_symbols = ["Unknown::HD"]
        start_ts = pd.Timestamp("2015-09-29T09:23:00+00:00")
        end_ts = pd.Timestamp("2015-09-29T09:35:00+00:00")
        #
        client = imvkdckicl.KibotEquitiesCsvParquetByAssetClient(
            root_dir,
            extension,
            asset_class,
            unadjusted,
        )
        actual_df = client.read_data(full_symbols, start_ts, end_ts)
        #
        expected_length = 13
        expected_column_names = [
            "full_symbol", "open", "high", "low", "close", "volume"
        ]
        expected_column_unique_values = {"full_symbol": ["Unknown::HD"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2015-09-29 09:23:00+00:00, 2015-09-29 09:35:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(13, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp                                                                     
        2015-09-29 09:23:00+00:00  Unknown::HD  102.36  102.36  102.36  102.36   447.0
        2015-09-29 09:24:00+00:00  Unknown::HD     NaN     NaN     NaN     NaN     NaN
        2015-09-29 09:25:00+00:00  Unknown::HD     NaN     NaN     NaN     NaN     NaN
        ...
        2015-09-29 09:33:00+00:00  Unknown::HD  102.17  102.21  102.08  102.17  15277.0
        2015-09-29 09:34:00+00:00  Unknown::HD  102.17  102.33  102.16  102.33   6145.0
        2015-09-29 09:35:00+00:00  Unknown::HD  102.39  102.49  102.12  102.15  19620.0
        """
        # pylint: enable=line-too-long
        self.check_df_output(
            actual_df,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature
        )


class TestKibotFuturesCsvParquetByAssetClient(hunitest.TestCase):
    def test_read_data1(self) -> None:
        root_dir = get_test_data_dir()
        extension = "csv.gz"
        contract_type = "continuous"
        full_symbols = ["Unknown::ZI"]
        start_ts = pd.Timestamp("2009-09-29T03:38:00+00:00")
        end_ts = pd.Timestamp("2009-09-29T03:55:00+00:00")
        #
        client = imvkdckicl.KibotFuturesCsvParquetByAssetClient(
            root_dir,
            extension,
            contract_type,
        )
        actual_df = client.read_data(full_symbols, start_ts, end_ts)
        #
        expected_length = 18
        expected_column_names = [
            "full_symbol", "open", "high", "low", "close", "volume"
        ]
        expected_column_unique_values = {"full_symbol": ["Unknown::ZI"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2009-09-29 03:38:00+00:00, 2009-09-29 03:55:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(18, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp                                                                     
        2009-09-29 03:38:00+00:00  Unknown::ZI  16.224  16.224  16.204  16.204     4.0
        2009-09-29 03:39:00+00:00  Unknown::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:40:00+00:00  Unknown::ZI  16.210   16.21   16.21   16.21     1.0
        ...
        2009-09-29 03:53:00+00:00  Unknown::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:54:00+00:00  Unknown::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:55:00+00:00  Unknown::ZI  16.134  16.134  16.134  16.134     1.0
        """
        # pylint: enable=line-too-long
        self.check_df_output(
            actual_df,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature
        )

    def test_read_data2(self) -> None:
        root_dir = get_test_data_dir()
        extension = "pq"
        contract_type = "continuous"
        full_symbols = ["Unknown::ZI"]
        start_ts = pd.Timestamp("2009-09-29T03:38:00+00:00")
        end_ts = pd.Timestamp("2009-09-29T03:55:00+00:00")
        #
        client = imvkdckicl.KibotFuturesCsvParquetByAssetClient(
            root_dir,
            extension,
            contract_type,
        )
        actual_df = client.read_data(full_symbols, start_ts, end_ts)
        #
        expected_length = 18
        expected_column_names = [
            "full_symbol", "open", "high", "low", "close", "volume"
        ]
        expected_column_unique_values = {"full_symbol": ["Unknown::ZI"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2009-09-29 03:38:00+00:00, 2009-09-29 03:55:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(18, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp                                                                     
        2009-09-29 03:38:00+00:00  Unknown::ZI  16.224  16.224  16.204  16.204     4.0
        2009-09-29 03:39:00+00:00  Unknown::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:40:00+00:00  Unknown::ZI  16.210  16.210  16.210  16.210     1.0
        ...
        2009-09-29 03:53:00+00:00  Unknown::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:54:00+00:00  Unknown::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:55:00+00:00  Unknown::ZI  16.134  16.134  16.134  16.134     1.0
        """
        # pylint: enable=line-too-long
        self.check_df_output(
            actual_df,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature
        )
