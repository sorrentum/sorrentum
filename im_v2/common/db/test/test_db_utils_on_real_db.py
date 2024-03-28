import datetime

import logging
import pandas as pd
import psycopg2 as psycop
import pytest

import helpers.hdatetime as hdateti
import helpers.hsql as hsql
import helpers.hunit_test as hunitest
import im_v2.common.db.db_utils as imvcddbut

_LOG = logging.getLogger(__name__)

TIME_ZONE = "UTC"
TABLE_NAME = "sample"
SAMPLE_DATA = pd.DataFrame({"timestamp": [10000, 20000, 30000],
                            "close": [1, 1, 1],
                            "open": [2, 2, 2],
                            "low": [1, 1, 1],
                            "high": [10, 10, 10],
                            "volume": [2, 2, 2],
                            "currency_pair": ["abc", "efg", "klm"],
                            "level": [1, 1, 1],
                            "exchange_id": ["someid1", "someid2", "someid3"]})


def initialize_database() -> psycop._psycopg.connection:
    db = psycop.connect(
        database="postgres", user='postgres', password='superuser', host='127.0.0.1', port='5432'
    )
    cursor = db.cursor()

    cursor.execute(f"""DROP TABLE IF EXISTS {TABLE_NAME}""")
    create_table_query = f"""
            CREATE TABLE {TABLE_NAME}(
                id BIGSERIAL PRIMARY KEY,
                timestamp BIGINT NOT NULL,
                open NUMERIC,
                high NUMERIC,
                low NUMERIC,
                close NUMERIC,
                volume NUMERIC,
                currency_pair VARCHAR(255) NOT NULL,
                level INTEGER NOT NULL,
                exchange_id VARCHAR(255) NOT NULL,
                end_download_timestamp TIMESTAMP WITH TIME ZONE,
                knowledge_timestamp TIMESTAMP WITH TIME ZONE,
                UNIQUE(timestamp, exchange_id,
                currency_pair, open, high, low, close, volume)
                )
            """
    cursor.execute(create_table_query)
    db.commit()

    return db


class TestSaveDataToDb(imvcddbut.TestImDbHelper, hunitest.TestCase):
    """
    This class tests im_v2.common.db.db_utils.save_data_to_db on real database, not a mock.
    """
    @classmethod
    def get_id(cls) -> int:
        return hash(cls.__name__) % 10000

    def test_save_data_to_db_ohlcv(self) -> None:
        """
        Test the `save_data_to_db` method for the case when inserting data for 'ohlcv' data type.
        """
        imvcddbut.save_data_to_db(SAMPLE_DATA, "ohlcv", self.connection, TABLE_NAME, TIME_ZONE)
        num_rows = hsql.get_num_rows(self.connection, TABLE_NAME)
        self.assertEqual(num_rows, 3)

    def test_save_data_to_db_bid_ask(self) -> None:
        """
        Test the `save_data_to_db` method for the case when inserting data for 'bid_ask' data type.
        """
        imvcddbut.save_data_to_db(SAMPLE_DATA, "bid_ask", self.connection, TABLE_NAME, TIME_ZONE)
        num_rows = hsql.get_num_rows(self.connection, TABLE_NAME)
        self.assertEqual(num_rows, 3)

    def test_save_data_to_db_trades(self) -> None:
        """
        Test the `save_data_to_db` method for the case when inserting data for 'trades' data type.
        """
        imvcddbut.save_data_to_db(SAMPLE_DATA, "trades", self.connection, TABLE_NAME, TIME_ZONE)
        num_rows = hsql.get_num_rows(self.connection, TABLE_NAME)
        self.assertEqual(num_rows, 3)

    def test_save_data_to_db_unknown_data_type(self) -> None:
        """
        Test the `save_data_to_db` method for the case when inserting data for unknown data type.
        """
        with self.assertRaises(ValueError):
            imvcddbut.save_data_to_db(SAMPLE_DATA, "unknown", self.connection, TABLE_NAME, TIME_ZONE)


class TestLoadDbData(imvcddbut.TestImDbHelper, hunitest.TestCase):
    """
    This class tests im_v2.common.db.db_utils.load_db_data from a real database, not a mock.
    """
    @classmethod
    def get_id(cls) -> int:
        return hash(cls.__name__) % 10000

    def test_load_db_data_select_all(self) -> None:
        """
        Test the `load_db_data` method when selecting no timestamps.
        """
        data = imvcddbut.load_db_data(self.connection, TABLE_NAME, None, None)
        self.assertEqual(data.shape[0], 3)

    def test_load_db_data_select_time_interval_open(self) -> None:
        """
        Test the `load_db_data` method when selecting open timestamp interval with border values.
        """
        start_ts = pd.Timestamp(10000, unit="ms")
        end_ts = pd.Timestamp(20000, unit="ms")
        data = imvcddbut.load_db_data(self.connection, TABLE_NAME, start_ts, end_ts, time_interval_closed=False)
        self.assertEqual(data.shape[0], 0)

    def test_load_db_data_select_time_interval_closed(self) -> None:
        """
        Test the `load_db_data` method when selecting closed timestamp interval with border values.
        """
        start_ts = pd.Timestamp(10000, unit="ms")
        end_ts = pd.Timestamp(20000, unit="ms")
        data = imvcddbut.load_db_data(self.connection, TABLE_NAME, start_ts, end_ts)
        self.assertEqual(data.shape[0], 2)

    def test_load_db_data_select_none(self) -> None:
        """
        Test the `load_db_data` method when selecting timestamp interval with no valid entries in DB.
        """
        start_ts = pd.Timestamp(500000, unit="ms")
        end_ts = pd.Timestamp(500001, unit="ms")
        data = imvcddbut.load_db_data(self.connection, TABLE_NAME, start_ts, end_ts)
        self.assertEqual(data.shape[0], 0)

    def test_load_db_data_select_currency_pairs(self) -> None:
        """
        Test the `load_db_data` method when selecting specific currency pairs.
        """
        currency_pairs = ["abc"]
        data = imvcddbut.load_db_data(self.connection, TABLE_NAME, None, None, currency_pairs=currency_pairs)
        self.assertEqual(data.shape[0], 1)


class TestFetchLastMinuteBidAskRtDbData(imvcddbut.TestImDbHelper, hunitest.TestCase):
    """
        This class tests im_v2.common.db.db_utils.load_db_data from a real database, not a mock.
        """

    @classmethod
    def get_id(cls) -> int:
        return hash(cls.__name__) % 10000

    def test_load_db_data_select_all(self) -> None:
        """
        Test the `load_db_data` method when selecting no timestamps.
        """
        data = imvcddbut.load_db_data(self.connection, TABLE_NAME, None, None)
        self.assertEqual(data.shape[0], 3)

    def _save_last_and_current_minute_data_to_db(self):
        """
        Save some additional (last minute and current minute) data to database.
        """
        current_minute_floored_ts = hdateti.get_current_time(TIME_ZONE).floor("min")
        last_minute_floored_ts = current_minute_floored_ts - datetime.timedelta(minutes=1)

        ts1 = hdateti.convert_timestamp_to_unix_epoch(last_minute_floored_ts)
        ts2 = hdateti.convert_timestamp_to_unix_epoch(last_minute_floored_ts + datetime.timedelta(seconds=10))
        ts3 = hdateti.convert_timestamp_to_unix_epoch(current_minute_floored_ts)

        data = pd.DataFrame({"timestamp": [ts1, ts2, ts3],
                             "close": [1, 1, 1],
                             "open": [2, 2, 2],
                             "low": [1, 1, 1],
                             "high": [10, 10, 10],
                             "volume": [2, 2, 2],
                             "currency_pair": ["abc", "efg", "klm"],
                             "level": [1, 1, 1],
                             "exchange_id": ["someid1", "someid2", "someid3"]})

        imvcddbut.save_data_to_db(data, "ohlcv", self.connection, TABLE_NAME, TIME_ZONE)

    def test_fetch_last_minute_bid_ask_rt_db_data(self):
        """
        Test the `fetch_last_minute_bid_ask_rt_db_data` method when there are some last minute data in database.
        """
        self._save_last_and_current_minute_data_to_db()
        data = imvcddbut.fetch_last_minute_bid_ask_rt_db_data(self.connection, TABLE_NAME, TIME_ZONE, "")
        self.assertEqual(data.shape[0], 2)

    def test_fetch_last_minute_bid_ask_rt_db_data_no_results(self):
        """
        Test the `fetch_last_minute_bid_ask_rt_db_data` method when no last minute data are in database.
        """
        data = imvcddbut.fetch_last_minute_bid_ask_rt_db_data(self.connection, TABLE_NAME, TIME_ZONE, "")
        self.assertEqual(data.shape[0], 0)
