import mariadb

from wolfpub.api.utils.custom_exceptions import MariaDBException
from wolfpub.api.utils.logger import WOLFPUB_LOGGER as logger


class MariaDBConnector(object):
    def __init__(self):
        self.user = 'spandey5',
        self.password = 'csc540@spring22',
        self.host = 'localhost',
        self.port = 3307,
        self.database = 'spandey5'
        self.conn = None

    def connect(self):
        try:
            self.conn = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=3306,
                database=self.database
            )
        except mariadb.Error as e:
            print(f'Error connecting to MariaDB Platform: {e}')
            raise MariaDBException(f'Error connecting to MariaDB Platform: {e}')

    def get_cursor(self):
        try:
            self.connect()
            return self.conn.cursor()
        except mariadb.Error as e:
            raise MariaDBException(f'Error in getting cursor for MariaDB: {e}')

    def execute(self, queries: list):
        cur = self.get_cursor()
        self.conn.autocommit = False
        try:
            for query in queries:
                logger.log(f'Executing: {query}')
                cur.execute(query)
            self.conn.commit()
            self.conn.autocommit = True
        except mariadb.Error as e:
            self.conn.rollback()
            raise MariaDBException(f'Error in executing above queries: {e}')
        finally:
            self.conn.close()
