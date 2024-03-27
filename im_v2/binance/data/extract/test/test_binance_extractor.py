import unittest.mock as umock

import pandas as pd

import helpers.hdatetime as hdateti
import helpers.henv as henv
import helpers.hpandas as hpandas
import helpers.hunit_test as hunitest
import im_v2.binance.data.extract.extractor as ivbdexex

class TextBinanceWebsocket(hunitest.TestCase):

    def _get_mock_bids(self):
        mock_data = """{
            "s" : "BTCUSDT",
            "T" : 123456789,
            "b": [100, 101],
            "a" : [110, 111],        
        }"""
        return mock_data
    
    def test_download_websocket_bid_ask(self):
        ivbdexex.hio = umock.MagicMock()
        contract_type = "futures"
        data_type = "trades"
        try:
            binance_extractor = ivbdexex.BinanceExtractor(
                contract_type, ivbdexex.BinanceNativeTimePeriod.DAILY, data_type
            )
            binance_extractor._websocket_data_buffer = {}
            
            binance_extractor._handle_orderbook_message = umock.MagicMock(
                return_value=self._get_mock_bids()
            )

            currency_pair = "BTCUSDT"
            actual_df = binance_extractor._download_websocket_bid_ask(currency_pair)
            import pdb; pdb.set_trace() 
        except Exception as e:
            raise e
        finally:
            binance_extractor.close()
        import pdb; pdb.set_trace()
        

    def test_download_websocket_ohlcv(self):
        mock_data = {'open': 100, 'high': 120, 'low': 90, 'close': 110, 'volume': 1000}
        pass

    def test_download_websocket_trades(self):
        mock_data = [{'timestamp': 123456789, 'price': 100, 'quantity': 10, 'side': 'buy'}]
        pass

class TestBinanceExtractor(hunitest.TestCase):
    def _get_mock_trades(self) -> pd.DataFrame:
        """
        Returns a mock trades dataframe.
        """
        return pd.DataFrame(
            {
                "symbol": ["BTCUSDT", "BTCUSDT", "BTCUSDT", "BTCUSDT"],
                "time": [
                    hdateti.convert_timestamp_to_unix_epoch(
                        pd.Timestamp("2020-01-01 00:00:00")
                    ),
                    hdateti.convert_timestamp_to_unix_epoch(
                        pd.Timestamp("2020-01-02 00:00:00")
                    ),
                    hdateti.convert_timestamp_to_unix_epoch(
                        pd.Timestamp("2020-01-03 00:00:00")
                    ),
                    hdateti.convert_timestamp_to_unix_epoch(
                        pd.Timestamp("2020-01-04 10:00:00")
                    ),
                ],
                "price": [100, 200, 300, 400],
                "qty": [1, 2, 3, 4],
                "is_buyer_maker": [True, False, True, False],
                "quote_qty": [100, 400, 900, 300],
                "id": [1, 2, 3, 4], 
            }
        )

    def test_fetch_trades(self) -> None:
        """
        Tests the fetch trades method.
        """
        # Mock downloading files and extracting data from them.
        ivbdexex.hio = umock.MagicMock()
        contract_type = "futures"
        data_type = "trades"
        try:
            binance_extractor = ivbdexex.BinanceExtractor(
                contract_type, ivbdexex.BinanceNativeTimePeriod.DAILY, data_type
            )
            binance_extractor._download_binance_files = umock.MagicMock()
            binance_extractor._extract_data_from_binance_files = umock.MagicMock(
                return_value=self._get_mock_trades()
            )
            # Prepare parameters.
            currency_pair = "BTCUSDT"
            start_date = pd.Timestamp("2020-01-01 00:00:00")
            end_date = pd.Timestamp("2020-01-03 23:59:00")
            # Run.
            actual_df = binance_extractor._fetch_trades(
                currency_pair, start_date, end_date
            )
        except Exception as e:
            raise e
        finally:
            binance_extractor.close()
        # Compare results.
        actual = hpandas.df_to_str(
            actual_df.drop(columns=["end_download_timestamp"])
        )
        expected = """timestamp  price  amount  side
            0  1577836800000    100       1   buy
            1  1577923200000    200       2  sell
            2  1578009600000    300       3   buy"""
        self.assert_equal(actual, expected, fuzzy_match=True)