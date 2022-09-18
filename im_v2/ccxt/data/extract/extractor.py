"""
Import as:

import im_v2.ccxt.data.extract.extractor as ivcdexex
"""

import logging
import time
from typing import Any, Dict, List, Optional

import ccxt
import pandas as pd
import tqdm

import helpers.hdatetime as hdateti
import helpers.hdbg as hdbg
import helpers.hsecrets as hsecret
import im_v2.common.data.extract.extractor as imvcdexex

_LOG = logging.getLogger(__name__)


class CcxtExtractor(imvcdexex.Extractor):
    """
    A class for accessing CCXT exchange data.

    This class implements an access layer that:
    - logs into an exchange using the proper credentials
    - retrieves data in multiple chunks to avoid throttling
    """

    def __init__(self, exchange_id: str, contract_type: str) -> None:
        """
        Construct CCXT extractor.

        :param exchange_id: CCXT exchange id to log into (e.g., 'binance')
        :param contract_type: spot or futures contracts to extract
        """
        super().__init__()
        hdbg.dassert_in(
            contract_type,
            ["futures", "spot"],
            msg="Supported contract types: spot, futures",
        )
        self.contract_type = contract_type
        self.exchange_id = exchange_id
        self._exchange = self.log_into_exchange()
        self.currency_pairs = self.get_exchange_currency_pairs()
        self.vendor = "CCXT"

    @staticmethod
    def convert_currency_pair(currency_pair: str) -> str:
        """
        Convert currency pair used for getting data from exchange.
        """
        return currency_pair.replace("_", "/")

    def log_into_exchange(self) -> ccxt.Exchange:
        """
        Log into an exchange via CCXT and return the corresponding
        `ccxt.Exchange` object.
        """
        exchange_params: Dict[str, Any] = {}
        secret_id = f"{self.exchange_id}.preprod.trading.1"
        # Select credentials for provided exchange.
        credentials = hsecret.get_secret(secret_id)
        exchange_params.update(credentials)
        # Enable rate limit.
        exchange_params["rateLimit"] = True
        if self.contract_type == "futures":
            exchange_params["options"] = {"defaultType": "future"}
        exchange_class = getattr(ccxt, self.exchange_id)
        exchange = exchange_class(exchange_params)
        hdbg.dassert(
            exchange.checkRequiredCredentials(),
            msg="Required credentials not passed",
        )
        return exchange

    def get_exchange_currency_pairs(self) -> List[str]:
        """
        Get all the currency pairs available for the exchange.
        """
        return list(self._exchange.load_markets().keys())

    def _download_ohlcv(
        self,
        exchange_id: str,
        currency_pair: str,
        *,
        start_timestamp: Optional[pd.Timestamp] = None,
        end_timestamp: Optional[pd.Timestamp] = None,
        bar_per_iteration: Optional[int] = 500,
        sleep_time_in_secs: float = 0.5,
        **kwargs: Any,
    ) -> pd.DataFrame:
        """
        Download minute OHLCV bars.

        :param currency_pair: a currency pair, e.g. "BTC_USDT"
        :param start_timestamp: starting point for data
        :param end_timestamp: end point for data (included)
        :param bar_per_iteration: number of bars per iteration
        :param sleep_time_in_secs: time in seconds between iterations
        :return: OHLCV data from CCXT
        """
        # Assign exchange_id to make it symmetrical to other vendors.
        _ = exchange_id
        hdbg.dassert(
            self._exchange.has["fetchOHLCV"],
            "Exchange %s doesn't has fetch_ohlcv method",
            self._exchange,
        )
        hdbg.dassert_in(
            currency_pair,
            self.currency_pairs,
            "Currency pair is not present in exchange",
        )
        # Get the latest bars if no timestamp is provided.
        if end_timestamp is None and start_timestamp is None:
            return self._fetch_ohlcv(
                currency_pair, bar_per_iteration=bar_per_iteration
            )
        # Verify that date parameters are of correct format.
        hdbg.dassert_isinstance(
            end_timestamp,
            pd.Timestamp,
        )
        hdbg.dassert_isinstance(
            start_timestamp,
            pd.Timestamp,
        )
        hdbg.dassert_lte(
            start_timestamp,
            end_timestamp,
        )
        # Convert datetime into ms.
        start_timestamp = start_timestamp.asm8.astype(int) // 1000000
        end_timestamp = end_timestamp.asm8.astype(int) // 1000000
        duration = self._exchange.parse_timeframe("1m") * 1000
        all_bars = []
        # Iterate over the time period.
        # Note: the iteration goes from start date to end date in milliseconds,
        # with the step defined by `bar_per_iteration` parameter.
        # Because of this, the output can go slightly over the end date.
        for t in tqdm.tqdm(
            range(
                start_timestamp,
                end_timestamp + duration,
                duration * bar_per_iteration,
            )
        ):
            bars = self._fetch_ohlcv(
                currency_pair, since=t, bar_per_iteration=bar_per_iteration
            )
            all_bars.append(bars)
            time.sleep(sleep_time_in_secs)
        all_bars_df = pd.concat(all_bars)
        # Remove bars which are not part of the requested timerange to
        #  avoid confusion of receiving unsolicited data.
        all_bars_df = all_bars_df[
            (all_bars_df["timestamp"] >= start_timestamp)
            & (all_bars_df["timestamp"] <= end_timestamp)
        ]
        hdbg.dassert(all_bars_df.timestamp.is_monotonic)
        # TODO(gp): Double check if dataframes are properly concatenated.
        return all_bars_df

    def _download_bid_ask(
        self, exchange_id: str, currency_pair: str, depth: int, **kwargs: Any
    ) -> pd.DataFrame:
        """
        Download bid-ask data from CCXT.

        :param exchange_id: exchange to download from
         (not used, kept for compatibility with parent class).
        :param currency_pair: currency pair to download, i.e. BTC_USDT.
        :param depth: depth of the order book to download.
        """
        # TODO(Juraj): can we get rid of this duplication of information?
        # exchange_id is set in constructor.
        # Assign exchange_id to make it symmetrical to other vendors.
        _ = exchange_id
        hdbg.dassert(
            self._exchange.has["fetchOrderBook"],
            "Exchange %s doesn't has fetchOrderBook method",
            self._exchange,
        )
        # Convert symbol to CCXT format, e.g. "BTC_USDT" -> "BTC/USDT".
        currency_pair = self.convert_currency_pair(
            currency_pair,
        )
        hdbg.dassert_in(
            currency_pair,
            self.currency_pairs,
            "Currency pair is not present in exchange",
        )
        # Download order book data.
        order_book = self._exchange.fetch_order_book(currency_pair, depth)
        order_book["end_download_timestamp"] = str(
            hdateti.get_current_time("UTC")
        )
        order_book = pd.DataFrame.from_dict(order_book)
        # Separate price and size into columns.
        order_book[["bid_price", "bid_size"]] = pd.DataFrame(
            order_book.bids.to_list(), index=order_book.index
        )
        order_book[["ask_price", "ask_size"]] = pd.DataFrame(
            order_book.asks.to_list(), index=order_book.index
        )
        order_book["level"] = order_book.index + 1
        # Select bid/ask columns.
        bid_ask_columns = [
            "timestamp",
            "bid_price",
            "bid_size",
            "ask_price",
            "ask_size",
            "end_download_timestamp",
            "level",
        ]
        bid_ask = order_book[bid_ask_columns]
        return bid_ask

    def _download_trades(self, **kwargs: Any) -> pd.DataFrame:
        raise NotImplementedError("Trades data is not available for CCXT vendor")

    def _fetch_ohlcv(
        self,
        currency_pair: str,
        *,
        timeframe: str = "1m",
        since: Optional[int] = None,
        bar_per_iteration: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Wrapper for fetching one minute OHLCV bars.

        :param currency_pair: currency pair, e.g. "BTC_USDT"
        :param timeframe: fetch data for certain timeframe
        :param since: from when is data fetched in milliseconds
        :param bar_per_iteration: number of bars per iteration

        :return: OHLCV data from CCXT that looks like:
            ```
                 timestamp      open      high       low     close    volume            end_download_timestamp
        0    1631145600000  46048.31  46050.00  46002.02  46005.10  55.12298  2022-02-22 18:00:06.091652+00:00
        1    1631145660000  46008.34  46037.70  45975.59  46037.70  70.45695  2022-02-22 18:00:06.091652+00:00
            ```
        """
        # Change currency pair to CCXT format.
        currency_pair = currency_pair.replace("_", "/")
        # Fetch the data through CCXT.
        bars = self._exchange.fetch_ohlcv(
            currency_pair,
            timeframe=timeframe,
            since=since,
            limit=bar_per_iteration,
        )
        # Package the data.
        columns = ["timestamp", "open", "high", "low", "close", "volume"]
        bars = pd.DataFrame(bars, columns=columns)
        bars["end_download_timestamp"] = str(hdateti.get_current_time("UTC"))
        return bars