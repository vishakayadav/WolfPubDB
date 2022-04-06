"""
Test Cases for Query Generator Module
"""
import pytest

from wolfpub.api.utils.custom_exceptions import QueryGenerationException
from wolfpub.api.utils.query_generator import QueryGenerator


class TestQueryGeneratorUtility(object):
    """
    Test Cases for checking the if dict is nested or not
    """
    def test_is_nested_dict(self):
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


class TestInsertQuery(object):
    """
    Test Cases for Insert Query
    """
    def test_insert_query_nested_dict(self):
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

    def test_insert_query(self):
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


class TestSelectQuery(object):
    """
    Test Cases for Select Query
    """
    def test_select_query(self):
        """
        Positive Test Case
        """
        cond = {'number': '9195130732'}
        query_generator = QueryGenerator()
        query_formed = query_generator.select('sample', ['id', 'name'], cond)
        assert query_formed.strip() == "select id, name from sample where number='9195130732'"

    def test_select_query_nested_cond(self):
        """
        Negative Test Case: condition is nested dict
        """
        cond = {'id': {'value': 1}}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.select('sample', ['id', 'name'], cond)


class TestUpdateQuery(object):
    """
    Test Cases for Update Query
    """
    def test_update_query(self):
        """
        Positive Test Case
        """
        row = {'name': 'ABC',
               'type': 'Whole Seller',
               'address': '2802 Avent Ferry',
               'city': 'Raleigh',
               'number': '9195130732'}
        cond = {'id': '1'}
        query_generator = QueryGenerator()
        query_formed = query_generator.update('sample', cond, row)
        assert query_formed.strip() == "update sample set name='ABC', type='Whole Seller', address='2802 Avent Ferry', " \
                                       "city='Raleigh', number='9195130732' where id='1'"

    def test_update_query_nested_cond(self):
        """
        Negative Test Case: condition is nested dict
        """
        row = {'name': 'ABC',
               'type': 'Whole Seller',
               'address': '2802 Avent Ferry',
               'city': 'Raleigh',
               'number': '9195130732'}
        cond = {'id': {'value': 1}}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.update('sample', cond, row)

    def test_update_query_nested_update_values(self):
        """
        Negative Test Case: update_data is nested dict
        """
        row = {'name': 'ABC',
               'type': 'Whole Seller',
               'address': {'street': '2802 Avent Ferry', 'city': 'Raleigh'},
               'number': '9195130732'}
        cond = {'id': 1}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.update('sample', cond, row)


class TestDeleteQuery(object):
    """
    Test Cases for Delete Query
    """
    def test_delete_query(self):
        """
        Positive Test Case
        """
        cond = {'id': '1'}
        query_generator = QueryGenerator()
        query_formed = query_generator.delete('sample', cond)
        assert query_formed.strip() == "delete from sample where id='1'"

    def test_delete_query_nested_cond(self):
        """
        Negative Test Case: condtion is nested dict
        """
        cond = {'id': {'value': 1}}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.delete('sample', cond)
