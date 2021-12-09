import logging
import os

import pandas as pd
import psycopg2.errors as perrors
import pytest

import helpers.git as hgit
import helpers.sql as hsql
import helpers.unit_test as hunitest
import im_v2.common.db.utils as imcodbuti

_LOG = logging.getLogger(__name__)


# TODO(gp): helpers can't depend from im.
@pytest.mark.skipif(
    hgit.is_dev_tools() or hgit.is_lime(), reason="Need dind support"
)
class TestSql1(imcodbuti.TestImDbHelper):
    def test_db_connection_to_tuple(self) -> None:
        """
        Verify that connection string is correct.
        """
        actual_details = hsql.db_connection_to_tuple(self.connection)
        expected = {
            "host": "localhost",
            "dbname": "im_postgres_db_local",
            "port": 5432,
            "user": "aljsdalsd",
            "password": "alsdkqoen",
        }
        self.assertEqual(actual_details._asdict(), expected)

    @pytest.mark.slow("17 seconds.")
    def test_create_database(self) -> None:
        """
        Verify that db is creating.
        """
        hsql.create_database(self.connection, dbname="test_db")
        self.assertIn("test_db", hsql.get_db_names(self.connection))

    @pytest.mark.slow("10 seconds.")
    def test_create_insert_query(self) -> None:
        """
        Verify that query is correct.
        """
        self._create_test_table()
        test_data = self._get_test_data()
        actual_query = hsql._create_insert_query(test_data, "test_table")
        self.check_string(actual_query)

    @pytest.mark.slow("11 seconds.")
    def test_remove_database1(self) -> None:
        """
        Create database 'test_db_to_remove' and remove it.
        """
        hsql.create_database(
            self.connection,
            dbname="test_db_to_remove",
        )
        hsql.remove_database(self.connection, "test_db_to_remove")
        db_list = hsql.get_db_names(self.connection)
        self.assertNotIn("test_db_to_remove", db_list)

    @pytest.mark.slow("8 seconds.")
    def test_remove_database_invalid(self) -> None:
        """
        Test failed assertion for passing db name that does not exist.
        """
        with self.assertRaises(perrors.InvalidCatalogName):
            hsql.remove_database(self.connection, "db does not exist")

    @pytest.mark.slow("16 seconds.")
    def test_execute_insert_query1(self) -> None:
        """
        Verify that dataframe insertion is correct.
        """
        self._create_test_table()
        test_data = self._get_test_data()
        # Try uploading test data.
        hsql.execute_insert_query(self.connection, test_data, "test_table")
        # Load data.
        df = hsql.execute_query_to_df(self.connection, "SELECT * FROM test_table")
        actual = hunitest.convert_df_to_json_string(df, n_tail=None)
        self.check_string(actual)

    @pytest.mark.slow("16 seconds.")
    def test_copy_rows_with_copy_from1(self) -> None:
        """
        Verify that dataframe insertion via buffer is correct.
        """
        self._create_test_table()
        test_data = self._get_test_data()
        # Try uploading test data.
        hsql.copy_rows_with_copy_from(self.connection, test_data, "test_table")
        # Load data.
        df = hsql.execute_query_to_df(self.connection, "SELECT * FROM test_table")
        actual = hunitest.convert_df_to_json_string(df, n_tail=None)
        self.check_string(actual)

    @pytest.mark.slow("9 seconds.")
    def test_duplicate_removal1(self) -> None:
        """
        Verify that duplicate entries are removed correctly.
        """
        self._create_test_table()
        test_data = self._get_duplicated_data()
        # Try uploading test data.
        hsql.execute_insert_query(self.connection, test_data, "test_table")
        # Create a query to remove duplicates.
        dup_query = hsql.get_remove_duplicates_query(
            "test_table", "id", ["column_1", "column_2"]
        )
        self.connection.cursor().execute(dup_query)
        df = hsql.execute_query_to_df(self.connection, "SELECT * FROM test_table")
        actual = hunitest.convert_df_to_json_string(df, n_tail=None)
        self.check_string(actual)

    @pytest.mark.slow("9 seconds.")
    def test_duplicate_removal2(self) -> None:
        """
        Verify that no rows are removed as duplicates.
        """
        self._create_test_table()
        test_data = self._get_test_data()
        # Try uploading test data.
        hsql.execute_insert_query(self.connection, test_data, "test_table")
        # Create a query to remove duplicates.
        dup_query = hsql.get_remove_duplicates_query(
            "test_table", "id", ["column_1", "column_2"]
        )
        self.connection.cursor().execute(dup_query)
        df = hsql.execute_query_to_df(self.connection, "SELECT * FROM test_table")
        actual = hunitest.convert_df_to_json_string(df, n_tail=None)
        self.check_string(actual)

    def _create_test_table(self) -> None:
        """
        Create a test table.
        """
        query = """CREATE TABLE IF NOT EXISTS test_table(
                    id SERIAL PRIMARY KEY,
                    column_1 NUMERIC,
                    column_2 VARCHAR(255)
                    )
                    """
        self.connection.cursor().execute(query)

    @staticmethod
    def _get_test_data() -> pd.DataFrame:
        """
        Get test data.
        """
        test_data = pd.DataFrame(
            columns=["id", "column_1", "column_2"],
            data=[
                [
                    1,
                    1000,
                    "test_string_1",
                ],
                [
                    2,
                    1001,
                    "test_string_2",
                ],
                [
                    3,
                    1002,
                    "test_string_3",
                ],
                [
                    4,
                    1003,
                    "test_string_4",
                ],
                [
                    5,
                    1004,
                    "test_string_5",
                ],
            ],
        )
        return test_data

    @staticmethod
    def _get_duplicated_data() -> pd.DataFrame:
        """
        Get test data with duplicates.
        """
        test_data = pd.DataFrame(
            columns=["id", "column_1", "column_2"],
            data=[
                [
                    1,
                    1000,
                    "test_string_1",
                ],
                [
                    2,
                    1001,
                    "test_string_2",
                ],
                [
                    3,
                    1002,
                    "test_string_3",
                ],
                [
                    4,
                    1002,
                    "test_string_3",
                ],
                [
                    5,
                    1001,
                    "test_string_2",
                ],
            ],
        )
        return test_data
