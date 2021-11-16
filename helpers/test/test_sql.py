import logging
import os

import pytest

import helpers.git as hgit
import helpers.sql as hsql
import helpers.system_interaction as hsyint
import helpers.unit_test as huntes

_LOG = logging.getLogger(__name__)


@pytest.mark.skipif(not hgit.is_amp(), reason="Only run in amp")
class TestSql(huntes.TestCase):
    def _create_test_table(self) -> None:
        """
        Create a test table.
        """
        query = """CREATE TABLE IF NOT EXISTS test_table(
                    id SERIAL PRIMARY KEY,
                    column_1 NUMERIC,
                    column_2 VARCHAR(255) NOT NULL,
                    )
                    """
        self.connection.cursor.execute(query)

    def setUp(self) -> None:
        """
        Initialize the test container.
        """
        super().setUp()
        self.docker_compose_file_path = os.path.join(
            hgit.get_amp_abs_path(), "im/devops/compose/docker-compose.yml"
        )
        cmd = (
            "sudo docker-compose "
            f"--file {self.docker_compose_file_path} "
            "up -d im_postgres_local"
        )
        hsyint.system(cmd, suppress_output=False)
        # Set DB credentials.
        self.dbname = "im_postgres_db_local"
        self.host = "localhost"
        self.port = 5432
        self.password = "alsdkqoen"
        self.user = "aljsdalsd"

    def tearDown(self) -> None:
        """
        Bring down the test container.
        """
        cmd = (
            "sudo docker-compose "
            f"--file {self.docker_compose_file_path} down -v"
        )
        hsyint.system(cmd, suppress_output=False)

        super().tearDown()

    @pytest.mark.slow()
    def test_waitdb(self) -> None:
        """
        Smoke test.
        """
        # TODO(Dan3): change to env
        hsql.wait_db_connection(self.dbname, self.port, self.host)

    @pytest.mark.slow()
    def test_db_connection_to_tuple(self) -> None:
        """
        Verify that connection string is correct.
        """
        hsql.wait_db_connection(self.dbname, self.port, self.host)
        self.connection, _ = hsql.get_connection(
            self.dbname,
            self.host,
            self.user,
            self.port,
            self.password,
            autocommit=True,
        )
        actual_details = hsql.db_connection_to_tuple(self.connection)
        expected = {
            "dbname": self.dbname,
            "host": self.host,
            "port": self.port,
            "user": self.user,
            "password": self.password,
        }
        self.assertEqual(actual_details._asdict(), expected)

    @pytest.mark.slow()
    def test_create_database(self) -> None:
        """
        Verify that db is creating.
        """
        hsql.wait_db_connection(self.dbname, self.port, self.host)
        self.connection, _ = hsql.get_connection(
            self.dbname,
            self.host,
            self.user,
            self.port,
            self.password,
            autocommit=True,
        )
        hsql.create_database(self.connection, dbname="test_db")
        self.assertIn("test_db", hsql.get_db_names(self.connection))
