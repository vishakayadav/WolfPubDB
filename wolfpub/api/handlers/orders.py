"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""
from wolfpub.api.utils.custom_exceptions import MariaDBException

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import ORDERS


class OrderHandler(object):
    """
    Focuses on providing functionality over Publications of WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = ORDERS['table_name']
        self.id_column = 'order_id'
        self.query_gen = QueryGenerator()

    @staticmethod
    def get_total_price(publications: list):
        total_price = 0
        for pub in publications:
            if isinstance(pub['price'], dict) or isinstance(pub['price'], list):
                raise ValueError('value of price column can not be dict or list')
            total_price += float(pub['price']) * int(pub.get('quantity', '1'))
        return total_price

    @staticmethod
    def reformat_publication_order(obj: list, order_id: int):
        return [{'order_id': order_id,
                 'publication_id': order['publication_id'],
                 'quantity': order.get('quantity', 1),
                 'price': float(order['price']) * int(order.get('quantity', 1))} for order in obj]

    def get_orders(self, account_id, select_cols: list = None):
        if select_cols is None:
            select_cols = ['*']
        select_query = self.query_gen.select(self.table_name, select_cols, {'account_id': account_id})
        orders = self.db.get_result(select_query)
        if not orders:
            raise IndexError(f"No Order Found for given Account Id")
        return orders

    def get_order(self, account_id, order_id, select_cols: list = None):
        if select_cols is None:
            select_cols = ['*']
        select_query = self.query_gen.select(self.table_name, select_cols, {'account_id': account_id,
                                                                            'order_id': order_id})
        order = self.db.get_result(select_query)
        if not order:
            raise IndexError(f"Order with id '{order_id}' Not Found for given Account Id")
        return order[0]

    def set(self, order: dict, book_orders: list[dict], periodical_orders: list[dict]):
        insert_query = self.query_gen.insert(self.table_name, [order])
        cursor = self.db.get_cursor()
        self.db.conn.autocommit = False
        try:
            _, last_row_id = self.db._execute(insert_query, cursor)
            if book_orders:
                book_orders = self.reformat_publication_order(book_orders, last_row_id)
                self.db._execute(self.query_gen.insert('book_orders_info', book_orders), cursor)
            if periodical_orders:
                periodical_orders = self.reformat_publication_order(periodical_orders, last_row_id)
                self.db._execute(self.query_gen.insert('periodical_orders_info', periodical_orders), cursor)
            self.db.conn.commit()
        except MariaDBException as e:
            self.db.conn.rollback()
            raise e
        return {'order_id': last_row_id}
