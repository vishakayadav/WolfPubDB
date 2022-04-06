"""
Test Cases for Query Generator Module
"""
import pytest

from wolfpub import config
from wolfpub.api.utils.custom_exceptions import QueryGenerationException
from wolfpub.api.utils.query_generator import QueryGenerator


class TestInsertQuery(object):
    """
    Test Cases for getting query string from filter formula dict
    """

    @staticmethod
    def test_is_nested_dict():
        """
        Negative Test Case: Nested Dict
        """
        row = {'name': 'ABC',
               'type': 'Retailer',
               'address': {'street': '2801 Avent Ferry', 'city': 'Raleigh'},
               'number': '9195130732'}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.is_nested(row)

    @staticmethod
    def test_insert_query_nested_dict():
        """
        Negative Test Case: Nested Dict
        """
        row = {'name': 'ABC',
               'type': 'Retailer',
               'address': {'street': '2801 Avent Ferry', 'city': 'Raleigh'},
               'number': '9195130732'}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.insert('sample', row)

    @staticmethod
    def test_insert_query():
        """
        Positive Test Case
        """
        row = {'name': 'ABC',
               'type': 'Retailer',
               'address': '2801 Avent Ferry',
               'city': 'Raleigh',
               'number': '9195130732'}
        query_generator = QueryGenerator()
        query_formed = query_generator.insert('sample', row)
        assert query_formed.strip() == "insert into sample (name, type, address, city, number) values ('ABC', 'Retailer', '2801 Avent Ferry', 'Raleigh', '9195130732')"

    @staticmethod
    def test_select_query():
        """
        Positive Test Case
        """
        cond = {'number': '9195130732'}
        query_generator = QueryGenerator()
        query_formed = query_generator.select('sample', ['id', 'name'], cond)
        assert query_formed.strip() == "select id, name from sample where number='9195130732'"
