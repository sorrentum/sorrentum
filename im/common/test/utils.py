import logging
import os

import pandas as pd

import helpers.sql as hsql
import helpers.unit_test as huntes
import im.common.db.create_db as imcodbcrsch
import im.common.sql_writer as imcosqwrbac

_LOG = logging.getLogger(__name__)


class SqlWriterBackendTestCase(huntes.TestCase):
    """
    Helper class to test writing data to IM PostgreSQL DB.
    """

    def setUp(self) -> None:
        super().setUp()
        # Get PostgreSQL connection parameters.
        self._conn_db = os.environ["POSTGRES_DB"]
        self._host = os.environ["POSTGRES_HOST"]
        self._port = os.environ["POSTGRES_PORT"]
        self._user = os.environ["POSTGRES_USER"]
        self._password = os.environ["POSTGRES_PASSWORD"]
        self._connection = hsql.get_connection(dbname=self._conn_db,
                                               host=self._host,
                                               port=int(self._port),
                                               user=self._user,
                                               password=self._password)
        self._new_db = self._get_test_string()
        # Create database for each test.
        imcodbcrsch.create_database(
            connection=self._connection,
            new_db=self._new_db,
            force=True,
        )
        # Define constant IDs for records across the test.
        self._symbol_id = 10
        self._exchange_id = 20
        self._trade_symbol_id = 30
        # Create a placeholder for self._writer.
        self._writer: imcosqwrbac.AbstractSqlWriter

    def tearDown(self) -> None:
        # Close connection.
        self._writer.close()
        # Remove created database.
        imcodbcrsch.remove_database(
            db_to_drop=self._new_db,
            conn_db=self._conn_db,
            host=self._host,
            user=self._user,
            port=int(self._port),
            password=self._password,
        )
        super().tearDown()

    def _prepare_tables(
        self,
        insert_symbol: bool,
        insert_exchange: bool,
        insert_trade_symbol: bool,
    ) -> None:
        """
        Insert Symbol, Exchange and TradeSymbol entries to make test work.

        See `common/db/sql` for more info.
        """
        with self._writer.conn:
            with self._writer.conn.cursor() as curs:
                # Fill Symbol table.
                if insert_symbol:
                    curs.execute(
                        "INSERT INTO Symbol (id, code, asset_class) "
                        "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [
                            self._symbol_id,
                            "ZS1M",
                            "Futures",
                        ],
                    )
                # Fill Exchange table.
                if insert_exchange:
                    curs.execute(
                        "INSERT INTO Exchange (id, name) "
                        "VALUES (%s, %s) ON CONFLICT DO NOTHING",
                        [
                            self._exchange_id,
                            "CME",
                        ],
                    )
                # Fill TradeSymbol table.
                if insert_trade_symbol:
                    curs.execute(
                        "INSERT INTO TradeSymbol (id, exchange_id, symbol_id) "
                        "VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                        [
                            self._trade_symbol_id,
                            self._exchange_id,
                            self._symbol_id,
                        ],
                    )
            _LOG.debug("tables=%s", hsql.head_tables(self._writer.conn))

    def _get_test_string(self) -> str:
        string: str = self._get_test_name().replace("/", "").replace(".", "")
        return string

    def _check_saved_data(self, table: str) -> None:
        """
        Check data saved in PostgreSQL by test.

        :param table: table name
        """
        # Construct query to retrieve the data.
        query = "SELECT * FROM %s;" % table
        # Get data in pandas format based on query.
        res = pd.read_sql(query, self._writer.conn)
        # Exclude changeable columns.
        columns_to_check = list(res.columns)
        for column_to_remove in ["id", "start_date"]:
            if column_to_remove in columns_to_check:
                columns_to_check.remove(column_to_remove)
        # Convert dataframe to string.
        txt = huntes.convert_df_to_string(res[columns_to_check])
        # Check the output against the golden.
        self.check_string(txt, fuzzy_match=True)
