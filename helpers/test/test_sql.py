import os
import logging

from psycopg2.errors import InvalidCatalogName

import helpers.sql as hsql
import helpers.system_interaction as hsyint
import helpers.unit_test as huntes
import im.common.db.create_db as imcodbcrdb

_LOG = logging.getLogger(__name__)


class Test_sql(huntes.TestCase):
    def setUp(self):
        """
        Initialize the test database inside test container 
        """
        super().setUp()
        cmd = "sudo docker-compose --file im/devops/compose/docker-compose.yml up -d im_postgres_local"
        hsyint.system(cmd, suppress_output=False)
        
    def tearDown(self):
        """
        Kill the DB.
        """
        cmd = "sudo docker-compose --file im/devops/compose/docker-compose.yml down -v"
        hsyint.system(cmd, suppress_output=False)
        super().tearDown()

    def test_checkdb(self):
        """
        Smoke test.
        """
        #TODO(Dan3): change to env
        dbname = "im_postgres_db_local"
        host = "localhost"
        port = 5432
        hsql.check_db_connection(dbname, port, host)

    def test_db_connection_to_str(self):
        """
        Verify connection details from connection.
        """
        dbname = "im_postgres_db_local"
        host = "localhost"
        port = 5432
        password = "alsdkqoen"
        user = "aljsdalsd"
        hsql.check_db_connection(dbname, port, host)
        #TODO(Dan3): self.connection, _ = get_connection_from_env_vars()
        self.connection, _ = hsql.get_connection(
            dbname,
            host,
            user,
            port,
            password,
            autocommit=True,
        )
        details_from_conn = hsql.db_connection_to_str(self.connection)
        #TODO(Dan3): change to env variables
        expected = (f"dbname={dbname}\n"
               f"host={host}\n"
               f"port={port}\n"
               f"user={user}\n"
               f"password={password}")
        self.assertEqual(details_from_conn, expected) 
