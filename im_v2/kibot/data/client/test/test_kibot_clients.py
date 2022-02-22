import os

import pandas as pd

import helpers.hdbg as hdbg
import helpers.hgit as hgit
import im_v2.common.data.client.test.im_client_test_case as icdctictc
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


# #############################################################################
# TestKibotEquitiesCsvParquetByAssetClient
# #############################################################################

# TODO(Dan): @Max CmTask1245.
class TestKibotEquitiesCsvParquetByAssetClient(icdctictc.ImClientTestCase):

    def test_read_csv_data5(self) -> None:
        root_dir = get_test_data_dir()
        extension = "csv.gz"
        asset_class = "stocks"
        unadjusted = False
        full_symbols = ["kibot::HD"]
        start_ts = pd.Timestamp("2015-09-29T09:23:00+00:00")
        end_ts = pd.Timestamp("2015-09-29T09:35:00+00:00")
        #
        client = imvkdckicl.KibotEquitiesCsvParquetByAssetClient(
            root_dir,
            extension,
            asset_class,
            unadjusted,
        )
        #
        expected_length = 13
        expected_column_names = [
            "full_symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        expected_column_unique_values = {"full_symbol": ["kibot::HD"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2015-09-29 09:23:00+00:00, 2015-09-29 09:35:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(13, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp
        2015-09-29 09:23:00+00:00  kibot::HD  102.36  102.36  102.36  102.36   447.0
        2015-09-29 09:24:00+00:00  kibot::HD     NaN     NaN     NaN     NaN     NaN
        2015-09-29 09:25:00+00:00  kibot::HD     NaN     NaN     NaN     NaN     NaN
        ...
        2015-09-29 09:33:00+00:00  kibot::HD  102.17  102.21  102.08  102.17  15277.0
        2015-09-29 09:34:00+00:00  kibot::HD  102.17  102.33  102.16  102.33   6145.0
        2015-09-29 09:35:00+00:00  kibot::HD  102.39  102.49  102.12  102.15  19620.0
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_parquet_data5(self) -> None:
        root_dir = get_test_data_dir()
        extension = "pq"
        asset_class = "stocks"
        unadjusted = False
        full_symbols = ["kibot::HD"]
        start_ts = pd.Timestamp("2015-09-29T09:23:00+00:00")
        end_ts = pd.Timestamp("2015-09-29T09:35:00+00:00")
        #
        client = imvkdckicl.KibotEquitiesCsvParquetByAssetClient(
            root_dir,
            extension,
            asset_class,
            unadjusted,
        )
        #
        expected_length = 13
        expected_column_names = [
            "full_symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        expected_column_unique_values = {"full_symbol": ["kibot::HD"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2015-09-29 09:23:00+00:00, 2015-09-29 09:35:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(13, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp
        2015-09-29 09:23:00+00:00  kibot::HD  102.36  102.36  102.36  102.36   447.0
        2015-09-29 09:24:00+00:00  kibot::HD     NaN     NaN     NaN     NaN     NaN
        2015-09-29 09:25:00+00:00  kibot::HD     NaN     NaN     NaN     NaN     NaN
        ...
        2015-09-29 09:33:00+00:00  kibot::HD  102.17  102.21  102.08  102.17  15277.0
        2015-09-29 09:34:00+00:00  kibot::HD  102.17  102.33  102.16  102.33   6145.0
        2015-09-29 09:35:00+00:00  kibot::HD  102.39  102.49  102.12  102.15  19620.0
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    # ////////////////////////////////////////////////////////////////////////

    def test_get_metadata1(self) -> None:
        root_dir = get_test_data_dir()
        extension = "csv.gz"
        asset_class = "stocks"
        unadjusted = False
        #
        client = imvkdckicl.KibotEquitiesCsvParquetByAssetClient(
            root_dir,
            extension,
            asset_class,
            unadjusted,
        )
        #
        expected_length = 252
        expected_column_names = [
            "Kibot_symbol",
            "Description",
            "StartDate",
            "Exchange",
            "Exchange_group",
            "Exchange_abbreviation",
            "Exchange_symbol",
            "num_contracts",
            "min_contract",
            "max_contract",
            "num_expiries",
            "expiries",
        ]
        expected_column_unique_values = None
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[0, 251]
        columns=Kibot_symbol,Description,StartDate,Exchange,Exchange_group,Exchange_abbreviation,Exchange_symbol,num_contracts,min_contract,max_contract,num_expiries,expiries
        shape=(252, 12)
          Kibot_symbol                                    Description  StartDate                                  Exchange Exchange_group Exchange_abbreviation Exchange_symbol  num_contracts min_contract max_contract  num_expiries                                 expiries
        0           AC                    CONTINUOUS ETHANOL CONTRACT 2009-09-28      Chicago Board Of Trade (CBOT GLOBEX)            CME                  CBOT              EH            122   2009-10-01   2019-12-01            12  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        1           AD          CONTINUOUS AUSTRALIAN DOLLAR CONTRACT 2009-09-27  Chicago Mercantile Exchange (CME GLOBEX)            NaN                   NaN             NaN             65   2009-12-01   2020-12-01            12  [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        2           AE  CONTINUOUS BLOOMBERG COMMODITY INDEX CONTRACT        NaT                                       NaN            CME                  CBOT              AW             38   2010-06-01   2019-09-01             4                            [3, 6, 9, 12]
        ...
        249          ZLT   CONTINUOUS SOYBEAN OIL TAS CONTRACT       NaT      NaN            CME                  CBOT             ZLT             36   2015-07-01   2019-12-01             8  [1, 3, 5, 7, 8, 9, 10, 12]
        250          ZMT  CONTINUOUS SOYBEAN MEAL TAS CONTRACT       NaT      NaN            CME                  CBOT             ZMT             37   2015-07-01   2019-12-01             8  [1, 3, 5, 7, 8, 9, 10, 12]
        251          ZWT         CONTINUOUS WHEAT TAS CONTRACT       NaT      NaN            CME                  CBOT             ZWT             25   2015-07-01   2020-07-01             5            [3, 5, 7, 9, 12]
        """
        # pylint: enable=line-too-long
        self._test_get_metadata1(
            client,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )


# #############################################################################
# TestKibotEquitiesCsvParquetByAssetClient
# #############################################################################


class TestKibotFuturesCsvParquetByAssetClient(icdctictc.ImClientTestCase):

    def test_read_csv_data5(self) -> None:
        root_dir = get_test_data_dir()
        extension = "csv.gz"
        contract_type = "continuous"
        full_symbols = ["kibot::ZI"]
        start_ts = pd.Timestamp("2009-09-29T03:38:00+00:00")
        end_ts = pd.Timestamp("2009-09-29T03:55:00+00:00")
        #
        client = imvkdckicl.KibotFuturesCsvParquetByAssetClient(
            root_dir,
            extension,
            contract_type,
        )
        #
        expected_length = 18
        expected_column_names = [
            "full_symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        expected_column_unique_values = {"full_symbol": ["kibot::ZI"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2009-09-29 03:38:00+00:00, 2009-09-29 03:55:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(18, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp
        2009-09-29 03:38:00+00:00  kibot::ZI  16.224  16.224  16.204  16.204     4.0
        2009-09-29 03:39:00+00:00  kibot::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:40:00+00:00  kibot::ZI  16.210   16.21   16.21   16.21     1.0
        ...
        2009-09-29 03:53:00+00:00  kibot::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:54:00+00:00  kibot::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:55:00+00:00  kibot::ZI  16.134  16.134  16.134  16.134     1.0
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )

    def test_read_parquet_data5(self) -> None:
        root_dir = get_test_data_dir()
        extension = "pq"
        contract_type = "continuous"
        full_symbols = ["kibot::ZI"]
        start_ts = pd.Timestamp("2009-09-29T03:38:00+00:00")
        end_ts = pd.Timestamp("2009-09-29T03:55:00+00:00")
        #
        client = imvkdckicl.KibotFuturesCsvParquetByAssetClient(
            root_dir,
            extension,
            contract_type,
        )
        #
        expected_length = 18
        expected_column_names = [
            "full_symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]
        expected_column_unique_values = {"full_symbol": ["kibot::ZI"]}
        # pylint: disable=line-too-long
        expected_signature = r"""
        # df=
        index=[2009-09-29 03:38:00+00:00, 2009-09-29 03:55:00+00:00]
        columns=full_symbol,open,high,low,close,volume
        shape=(18, 6)
                                   full_symbol    open    high     low   close  volume
        timestamp
        2009-09-29 03:38:00+00:00  kibot::ZI  16.224  16.224  16.204  16.204     4.0
        2009-09-29 03:39:00+00:00  kibot::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:40:00+00:00  kibot::ZI  16.210  16.210  16.210  16.210     1.0
        ...
        2009-09-29 03:53:00+00:00  kibot::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:54:00+00:00  kibot::ZI     NaN     NaN     NaN     NaN     NaN
        2009-09-29 03:55:00+00:00  kibot::ZI  16.134  16.134  16.134  16.134     1.0
        """
        # pylint: enable=line-too-long
        self._test_read_data5(
            client,
            full_symbols,
            start_ts,
            end_ts,
            expected_length,
            expected_column_names,
            expected_column_unique_values,
            expected_signature,
        )