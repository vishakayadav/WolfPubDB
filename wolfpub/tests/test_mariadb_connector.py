"""
Test Cases for Mongo Connector
"""
import pytest
from MySQLdb import DataError

from wolfpub.api.utils.mariadb_connector import MariaDBConnector
from wolfpub.constants import DISTRIBUTORS

mariadb = MariaDBConnector()
table_dict = DISTRIBUTORS


class TestExecute(object):
    """
    Test Cases for executing DML queries on MariaDB
    """

    @staticmethod
    def test_execute(mocker, mock_mysql):
        """
        Positive Test Case
        """
        queries = ["create table test1 (id int primary key auto_increment, name varchar(10))",
                   "insert into test1 (name) values ('ABC')"]
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        row_affected, last_row_id = mariadb.execute(queries)
        assert row_affected == 1
        assert last_row_id[-1] == 1

    @staticmethod
    def test_execute_negative(mocker, mock_mysql):
        """
        Negative Test Case: invalid query
        """
        queries = ["create table test1 (id int, name varchar(2))", "insert into test1 values (1, 'ABC')"]
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        with pytest.raises(DataError):
            mariadb.execute(queries)


class TestGetResult(object):
    """
    Test Cases for getting data from MariaDB
    """

    @staticmethod
    def test_get_result(mocker, mock_mysql, mock_table, add_record):
        """
        Positive Test Case
        """
        first_col = list(table_dict['columns'].keys())[0]
        query = f"select {first_col} from {table_dict['table_name']}"
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        result = mariadb.get_result(query)
        assert len(result) == 1
        assert result[0] == {first_col: 1}

    @staticmethod
    def test_get_result_zero_rows(mocker, mock_mysql, mock_table):
        """
        Positive Test Case
        """
        first_col = list(table_dict['columns'].keys())[0]
        query = f"select {first_col} from {table_dict['table_name']}"
        mocker.patch('wolfpub.api.utils.mariadb_connector.MariaDBConnector.connect', return_value=mock_mysql)
        result = mariadb.get_result(query)
        assert len(result) == 0
