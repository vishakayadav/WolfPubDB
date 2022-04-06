import mariadb
from wolfpub.config import MARIADB_SETTINGS

from wolfpub.api.utils.custom_exceptions import MariaDBException
from wolfpub.logger import WOLFPUB_LOGGER as logger


class MariaDBConnector(object):
    def __init__(self):
        self.user = MARIADB_SETTINGS['USERNAME']
        self.password = MARIADB_SETTINGS['PASSWORD']
        self.host = MARIADB_SETTINGS['HOST']
        self.port = int(MARIADB_SETTINGS['PORT'])
        self.database = MARIADB_SETTINGS['DB']
        self.conn = None

    def connect(self):
        try:
            self.conn = mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
        except mariadb.Error as e:
            raise MariaDBException(f'Error connecting to MariaDB Platform: {e}')

    def get_cursor(self):
        try:
            self.connect()
            return self.conn.cursor()
        except mariadb.Error as e:
            raise MariaDBException(f'Error in getting cursor for MariaDB: {e}')

    def execute(self, queries: list, conn=None):
        if conn:
            cur = conn.cursor()
            self.conn = conn
        else:
            cur = self.get_cursor()
        self.conn.autocommit = False
        try:
            for query in queries:
                logger.info(f'Executing: {query}')
                cur.execute(query)
            self.conn.commit()
            self.conn.autocommit = True
            return cur.rowcount
        except mariadb.Error as e:
            self.conn.rollback()
            raise MariaDBException(e)
        finally:
            self.conn.close()

    def get_result(self, query: str, conn=None):
        if conn:
            cur = conn.cursor()
            self.conn = conn
        else:
            cur = self.get_cursor()
        try:
            logger.info(f'Executing: {query}')
            cur.execute(query)
            rows = cur.fetchall()
            desc = cur.description
            column_names = [col[0] for col in desc]
            result = [dict(zip(column_names, row)) for row in rows]
            return result
        except Exception as e:
            raise MariaDBException(e)
        finally:
            self.conn.close()
