import logging
import os

import pytest

import helpers.git as hgit
import helpers.hsql_test as hsqltest
import helpers.sql as hsql
import helpers.system_interaction as hsysinte
import im_v2.common.db.utils as imvcodbut

_LOG = logging.getLogger(__name__)


class TestImDbHelper(hsqltest.TestDbHelper):
    @staticmethod
    def _get_compose_file() -> str:
        return "im_v2/devops/compose/docker-compose.yml"

    # TODO(Dan): Deprecate after #585.
    @staticmethod
    def _get_db_name() -> str:
        return "im_postgres_db_local"

    @staticmethod
    def _get_service_name() -> str:
        return "im_postgres_local"


@pytest.mark.skipif(
    hgit.is_dev_tools() or hgit.is_lime(), reason="Need dind support"
)
@pytest.mark.superslow(reason="speed up in #460.")
class TestCreateDb1(TestImDbHelper):
    def test_up1(self) -> None:
        """
        Verify that the DB is up.
        """
        db_list = hsql.get_db_names(self.connection)
        _LOG.info("db_list=%s", db_list)

    def test_create_all_tables1(self) -> None:
        """
        Verify that all necessary tables are created inside the DB.
        """
        imvcodbut.create_all_tables(self.connection)
        expected = sorted(
            [
                "ccxt_ohlcv",
                "currency_pair",
                "exchange",
                "exchange_name",
                "ib_daily_data",
                "ib_minute_data",
                "ib_tick_bid_ask_data",
                "ib_tick_data",
                "kibot_daily_data",
                "kibot_minute_data",
                "kibot_tick_bid_ask_data",
                "kibot_tick_data",
                "symbol",
                "trade_symbol",
            ]
        )
        actual = sorted(hsql.get_table_names(self.connection))
        self.assertEqual(actual, expected)

    def test_create_im_database(self) -> None:
        imvcodbut.create_im_database(connection=self.connection, new_db="test_db")
        db_list = hsql.get_db_names(self.connection)
        self.assertIn("test_db", db_list)
