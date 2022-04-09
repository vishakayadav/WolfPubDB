"""
Test Cases for Query Generator Module
"""
import pytest

from wolfpub.api.utils.custom_exceptions import QueryGenerationException
from wolfpub.api.utils.query_generator import QueryGenerator


class TestQueryGeneratorUtility(object):
    """
    Test Cases for utility function of query generator
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
        query_generator.is_list(row)
        with pytest.raises(QueryGenerationException):
            query_generator.is_dict(row)

    def test_is_nested_list(self):
        """
        Negative Test Case: Nested Dict
        """
        row = {'name': 'ABC',
               'type': 'Retailer',
               'address': ['2801 Avent Ferry', 'Raleigh'],
               'number': '9195130732'}
        query_generator = QueryGenerator()
        query_generator.is_dict(row)
        with pytest.raises(QueryGenerationException):
            query_generator.is_list(row)

    def test_handling_where_operator(self):
        """
        Positive Test Case:
        """
        data = {'order_date': {'>': '2022-01-01', '<': '2022-03-03'}}
        query_generator = QueryGenerator()
        query_formed = query_generator.handling_where_operator('order_date', data['order_date'])
        assert query_formed == "order_date > '2022-01-01' and order_date < '2022-03-03'"

    def test_handling_set_operator(self):
        """
        Positive Test Case:
        """
        data = {'balance': {'+': '420', '-': '100'}}
        query_generator = QueryGenerator()
        query_formed = query_generator.handling_set_operator('balance', data['balance'])
        assert query_formed == "balance = balance + '420', balance = balance - '100'"

    def test_get_where_cond(self):
        """
        Positive Test Case:
        """
        cond = {'name': 'ABC',
                'type': ['Retailer', 'Whole Seller'],
                'books': [{'book_id': 1, 'edition': 2},
                          {'book_id': 2, 'edition': 6}],
                'order_date': {'>': '2022-01-01'},
                'address': None,
                'number': 9195130732}
        query_generator = QueryGenerator()
        query_formed = query_generator.get_where_cond(cond)
        assert query_formed == "name='ABC' and type IN ('Retailer', 'Whole Seller') and " \
                               "((book_id='1' and edition='2') or (book_id='2' and edition='6')) and " \
                               "order_date > '2022-01-01' and address IS NULL and number='9195130732'"

    def test_get_where_cond_invalid_value(self):
        """
        Positive Test Case:
        """
        cond = {'name': 'ABC',
                'type': b'\xff',
                'number': '9195130732'}
        query_generator = QueryGenerator()
        with pytest.raises(QueryGenerationException):
            query_generator.get_where_cond(cond)


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
            query_generator.insert('sample', [row])

    def test_insert_query(self):
        """
        Positive Test Case
        """
        rows = [{'name': 'ABC', 'type': 'Retailer'}, {'name': 'DEF', 'type': 'Whole Seller'}]
        query_generator = QueryGenerator()
        query_formed = query_generator.insert('sample', rows)
        assert query_formed.strip() == "insert into sample (name, type) " \
                                       "values ('ABC', 'Retailer'), ('DEF', 'Whole Seller')"


class TestSelectQuery(object):
    """
    Test Cases for Select Query
    """

    def test_select_query_no_cond(self):
        """
        Positive Test Case: with no where clause
        """
        cond = {}
        query_generator = QueryGenerator()
        query_formed = query_generator.select('sample', ['id', 'name'], cond)
        assert query_formed.strip() == "select id, name from sample"

    def test_select_query(self):
        """
        Positive Test Case
        """
        cond = {'number': '9195130732'}
        query_generator = QueryGenerator()
        query_formed = query_generator.select('sample', ['id', 'name'], cond)
        assert query_formed.strip() == "select id, name from sample where number='9195130732'"

    def test_select_query_with_group_by(self):
        """
        Positive Test Case: With Group by keys
        """
        cond = {'number': '9195130'}
        group_by = ['id']
        query_generator = QueryGenerator()
        query_formed = query_generator.select('sample', ['id', 'name'], cond, group_by)
        assert query_formed.strip() == "select id, name from sample where number='9195130' group by id"


    def test_select_query_nested_cond(self):
        """
        Positive Test Case: condition is nested dict
        """
        cond = {'id': {'value': 1}}
        query_generator = QueryGenerator()
        query_formed = query_generator.select('sample', ['id', 'name'], cond)
        assert query_formed.strip() == "select id, name from sample where value='1'"


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
               'city': {'+': 'Raleigh'},
               'number': 9195130732}
        cond = {'id': '1'}
        query_generator = QueryGenerator()
        query_formed = query_generator.update('sample', cond, row)
        assert query_formed.strip() == "update sample set name='ABC', type='Whole Seller', " \
                                       "address='2802 Avent Ferry', city = city + 'Raleigh', number='9195130732' where id='1'"

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

