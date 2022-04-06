"""
Test Cases for Mongo Connector
"""
import pytest

from wolfpub.api.utils.custom_exceptions import MariaDBException

from wolfpub import config
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

mariadb = MariaDBConnector()


class TestExecute(object):
    """
    Test Cases for executing DML queries on MariaDB
    """

    @staticmethod
    def test_execute(mysql):
        """
        Positive Test Case
        """
        queries = ["create table test1 (id int, name varchar(10))", "insert into test1 values (1, 'ABC')"]
        mariadb.execute(queries, conn=mysql)

    @staticmethod
    def test_execute_negative(mysql):
        """
        Negative Test Case: invalid query
        """
        queries = ["create table test1 (id int, name varchar(2))", "insert into test1 values (1, 'ABC')"]
        with pytest.raises(MariaDBException):
            mariadb.execute(queries, conn=mysql)


class TestGetResult(object):
    """
    Test Cases for getting data from MariaDB
    """

    @staticmethod
    def test_get_result(mysql, table):
        """
        Positive Test Case
        """
        query = "select id from sample where number='919513073'"
        result = mariadb.get_result(query, mysql)
        assert len(result) == 1
        assert result[0] == {'id': 1}

    @staticmethod
    def test_get_result_zero_rows(mysql, table):
        """
        Positive Test Case
        """
        query = "select id from sample where number='91951307'"
        result = mariadb.get_result(query, mysql)
        assert len(result) == 0
