import logging
import unittest.mock as umock

import ccxt
import pytest

import helpers.henv as henv
import helpers.hsql as hsql
import im_v2.ccxt.db.utils as imvccdbut
import im_v2.common.db.db_utils as imvcddbut

_LOG = logging.getLogger(__name__)


@pytest.mark.skipif(
    not henv.execute_repo_config_code("has_dind_support()")
    and not henv.execute_repo_config_code("use_docker_sibling_containers()"),
    not henv.execute_repo_config_code("is_CK_S3_available()"),
    reason="Need docker children / sibling support and/or Run only if CK S3 is available",
)
@pytest.mark.slow("22 seconds.")
class TestPopulateExchangeCurrencyTables(imvcddbut.TestImDbHelper):
    # Mock calls to external providers.
    ccxt_patch = umock.patch.object(imvccdbut, "ccxt", spec=ccxt)

    @classmethod
    def get_id(cls) -> int:
        return hash(cls.__name__) % 10000

    # This will be run before and after each test.
    @pytest.fixture(autouse=True)
    def setup_teardown_test(self):
        # Run before each test.
        self.set_up_test()
        yield
        # Run after each test.
        self.tear_down_test()

    def set_up_test(self) -> None:
        # Create exchange names table in the database.
        exchange_name_create_table_query = (
            imvccdbut.get_exchange_name_create_table_query()
        )
        hsql.execute_query(self.connection, exchange_name_create_table_query)
        # Create currency pairs table in the database.
        currency_pair_create_table_query = (
            imvccdbut.get_currency_pair_create_table_query()
        )
        hsql.execute_query(self.connection, currency_pair_create_table_query)
        # Activate mock for `ccxt`.
        self.ccxt_mock: umock.MagicMock = self.ccxt_patch.start()
        # Set up the mock exchanges.
        self.ccxt_mock.exchanges = ["binance"]
        # Mock the binance ccxt to return load market keys.
        self.ccxt_mock.binance.return_value.load_markets.return_value.keys.return_value = [
            "MOCKBTC/MOCKUSD"
        ]

    def tear_down_test(self) -> None:
        hsql.remove_table(self.connection, "exchange_name")
        hsql.remove_table(self.connection, "currency_pair")
        # Deactivate mock for `ccxt`.
        self.ccxt_patch.stop()

    def test1(self) -> None:
        """
        Verify that the exchange names and currency pairs tables are populated
        correctly.
        """
        # Run test.
        imvccdbut.populate_exchange_currency_tables(self.connection)
        # Verify that the exchange names table is populated correctly.
        # Check the content of the table.
        query = f"SELECT * FROM exchange_name"
        actual = hsql.execute_query_to_df(self.connection, query)
        # Define expected values.
        expected_length = 1
        expected_column_value = None
        expected_signature = r"""
        # df=
        index=[0, 0]
        columns=exchange_id,exchange_name
        shape=(1, 2)
        exchange_id exchange_name
        0            0       binance
        """
        # Check signature.
        self.check_df_output(
            actual,
            expected_length,
            expected_column_value,
            expected_column_value,
            expected_signature,
        )
        # Verify that the currency pairs table is populated correctly.
        # Check the content of the table.
        query = f"SELECT * FROM currency_pair"
        actual = hsql.execute_query_to_df(self.connection, query)
        # Define expected values.
        expected_length = 1
        expected_column_value = None
        expected_signature = r"""
        # df=
        index=[0, 0]
        columns=currency_pair_id,currency_pair
        shape=(1, 2)
        currency_pair_id    currency_pair
        0                 0  MOCKBTC/MOCKUSD
        """
        # Check signature.
        self.check_df_output(
            actual,
            expected_length,
            expected_column_value,
            expected_column_value,
            expected_signature,
        )
