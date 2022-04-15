import mariadb

from wolfpub.api.utils.custom_exceptions import MariaDBException
from wolfpub.config import MARIADB_SETTINGS
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
        """
        Returns connection to mariadb
        """
        try:
            return mariadb.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database
            )
        except mariadb.Error as e:
            raise MariaDBException(f'Error connecting to MariaDB Platform: {e}')

    def get_cursor(self):
        """
        Get a connection and return the cursor for the active connection
        """
        try:
            self.conn = self.connect()
            return self.conn.cursor()
        except mariadb.Error as e:
            logger.error(e)
            raise MariaDBException(f'Error in getting cursor for MariaDB: {e}')

    def execute(self, queries: list):
        """
        Executes the list of queries within one transaction
        """
        cur = self.get_cursor()
        self.conn.autocommit = False
        last_row_ids = []
        try:
            for query in queries:
                _, rowid = self._execute(query, cur)
                last_row_ids.append(rowid)
            self.conn.commit()
            return cur.rowcount, last_row_ids
        except MariaDBException as e:
            self.conn.rollback()
            raise MariaDBException(e)
        finally:
            self.conn.close()

    @staticmethod
    def _execute(query: str, cursor):
        """
        Could be used by other classes only if response from one query to be used in another and
        everything is supposed to be in one transaction.
        This function does not commit after execution, so the function calling it should take care of the commit process
        """
        logger.info(f'Executing: {query}')
        try:
            cursor.execute(query)
            return cursor.rowcount, cursor.lastrowid
        except mariadb.Error as e:
            logger.error(e)
            raise MariaDBException(e)

    def get_result(self, query: str):
        """
        Get response for select queries as a list
        """
        cur = self.get_cursor()
        self._execute(query, cur)
        rows = cur.fetchall()
        desc = cur.description
        column_names = [col[0] for col in desc]
        result = [dict(zip(column_names, row)) for row in rows]
        self.conn.close()
        return result
