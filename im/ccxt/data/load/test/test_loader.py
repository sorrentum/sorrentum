import im.ccxt.data.load.loader as icdloloa
import helpers.unit_test as hut


_AM_S3_ROOT_DIR = os.path.join(hs3.get_path(), "data")


class TestGetFilePath(hunitest.TestCase):
    def test1(self) -> None:
        """
        Test supported exchange id and currency pair.
        """
        exchange = "binance"
        currency = "ETH/USDT"
        actual = icdloloa.get_file_name(exchange, currency)
        expected = "binance_ETH_USDT.csv.gz"
        self.assert_equal(actual, expected)

    def test2(self) -> None:
        """
        Test supported exchange id and currency pair.
        """
        exchange = "kucoin"
        currency = "ADA/USDT"
        actual = icdloloa.get_file_name(exchange, currency)
        expected = "kucoin_ADA_USDT.csv.gz"
        self.assert_equal(actual, expected)

    def test3(self) -> None:
        """
        Test unsupported exchange id.
        """
        exchange_id = "unsupported exchange"
        currency_pair = "ADA/USDT"
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        # TODO(gp): We should throw a different exception, like
        # `UnsupportedExchange`.
        # TODO(gp): Same change also for CDD test_loader.py
        with self.assertRaises(AssertionError):
            icdloloa.get_file_name(exchange, currency)

    def test3(self) -> None:
        """
        Test unsupported currency pair.
        """
        exchange_id = "binance"
        currency_pair = "unsupported_currency"
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        # TODO(gp): Same change also for CDD test_loader.py
        with self.assertRaises(AssertionError):
            icdloloa.get_file_name(exchange, currency)


class TestReadUniverseDataFromFilesystem(huntes.TestCase):
    @pytest.mark.slow("About 3.5 minutes.")
    def test1(self) -> None:
        """
        Test that all files from universe version are being read correctly.
        """
        # Initialize loader and get actual result.
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        actual = ccxt_loader.read_universe_data_from_filesystem(
            universe="v0_3", data_type="OHLCV"
        )
        # Check output.
        expected_length = 28209782
        expected_exchange_ids = ["binance", "ftx", "gateio", "kucoin"]
        expected_currency_pairs = [
            "ADA/USDT",
            "AVAX/USDT",
            "BNB/USDT",
            "BTC/USDT",
            "DOGE/USDT",
            "EOS/USDT",
            "ETH/USDT",
            "FIL/USDT",
            "LINK/USDT",
            "SOL/USDT",
            "XRP/USDT",
        ]
        self._check_output(
            actual,
            expected_length,
            expected_exchange_ids,
            expected_currency_pairs,
        )

    @pytest.mark.slow("About 40 seconds.")
    def test2(self) -> None:
        """
        Test that data for provided list of tuples is being read correctly.
        """
        # Set input universe.
        input_universe = [
            imdauni.ExchangeCurrencyTuple("binance", "BTC/USDT"),
            imdauni.ExchangeCurrencyTuple("binance", "ETH/USDT"),
            imdauni.ExchangeCurrencyTuple("kucoin", "BTC/USDT"),
            imdauni.ExchangeCurrencyTuple("kucoin", "ETH/USDT"),
            imdauni.ExchangeCurrencyTuple("kucoin", "FIL/USDT"),
        ]
        # Initialize loader and get actual result.
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        actual = ccxt_loader.read_universe_data(
            universe=input_universe, data_type="OHLCV"
        )
        # Check output.
        expected_length = 6961481
        expected_exchange_ids = ["binance", "kucoin"]
        expected_currency_pairs = ["BTC/USDT", "ETH/USDT", "FIL/USDT"]
        self._check_output(
            actual,
            expected_length,
            expected_exchange_ids,
            expected_currency_pairs,
        )

    def test3(self) -> None:
        """
        Test that all files from small test universe are being read correctly.
        """
        # Initialize loader and get actual result.
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        actual = ccxt_loader.read_universe_data(
            universe="small", data_type="OHLCV"
        )
        # Check output.
        expected_length = 190046
        expected_exchange_ids = ["gateio", "kucoin"]
        expected_currency_pairs = ["SOL/USDT", "XRP/USDT"]
        self._check_output(
            actual,
            expected_length,
            expected_exchange_ids,
            expected_currency_pairs,
        )

    def _check_output(
        self,
        actual: pd.DataFrame,
        expected_length: int,
        expected_exchange_ids: List[str],
        expected_currency_pairs: List[str],
    ) -> None:
        """
        Verify that actual outcome dataframe matches the expected one.

        :param actual: actual outcome dataframe
        :param expected_length: expected outcome dataframe length
        :param expected_exchange_ids: list of expected exchange ids
        :param expected_currency_pairs: list of expected currency pairs
        """
        # Check output df length.
        self.assert_equal(str(expected_length), str(actual.shape[0]))
        # Check unique exchange ids in the output df.
        actual_exchange_ids = sorted(list(actual["exchange_id"].unique()))
        self.assert_equal(str(actual_exchange_ids), str(expected_exchange_ids))
        # Check unique currency pairs in the output df.
        actual_currency_pairs = sorted(list(actual["currency_pair"].unique()))
        self.assert_equal(
            str(actual_currency_pairs), str(expected_currency_pairs)
        )
        # Check the output values.
        actual_string = hunitest.convert_df_to_json_string(actual)
        self.check_string(actual_string)


# TODO(*): Consider to factor out the class calling in a `def _get_loader()`.
class TestCcxtLoaderFromFileReadData(hunitest.TestCase):
    @pytest.mark.slow("12 seconds.")
    def test1(self) -> None:
        """
        Test that files on S3 are being read correctly.
        """
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        actual = ccxt_loader.read_data("binance", "BTC/USDT", "OHLCV")
        # Check the output values.
        actual_string = hunitest.convert_df_to_json_string(actual)
        self.check_string(actual_string)

    def test2(self) -> None:
        """
        Test unsupported exchange id.
        """
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        with self.assertRaises(AssertionError):
            ccxt_loader.read_data("unsupported_exchange_id", "BTC/USDT", "OHLCV")

    def test3(self) -> None:
        """
        Test unsupported currency pair.
        """
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        with self.assertRaises(AssertionError):
            ccxt_loader.read_data("binance", "unsupported_currency_pair", "OHLCV")

    def test4(self) -> None:
        """
        Test unsupported data type.
        """
        ccxt_loader = imcdalolo.CcxtLoaderFromFile(
            root_dir=_AM_S3_ROOT_DIR, aws_profile="am"
        )
        with self.assertRaises(AssertionError):
            ccxt_loader.read_data("binance", "BTC/USDT", "unsupported_data_type")
