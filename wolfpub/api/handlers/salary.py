"""
Module for handling payments
"""

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import SALARY_PAYMENTS


class PaymentHandler(object):
    """
    Focuses on providing functionality for payments to employees
    """

    def __init__(self, db):
        self.db = db
        self.table_name = SALARY_PAYMENTS['table_name']
        self.query_gen = QueryGenerator()

    def get_payment(self, transaction_id):
        cond = {'transaction_id': transaction_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def set(self, payment: dict):
        insert_query = self.query_gen.insert(self.table_name, [payment])
        _, last_row_id = self.db.execute([insert_query])
        return {'transaction_id': last_row_id[-1]}

    def update_claim_date(self, transaction_id: str, received_date: str):
        cond = {'transaction_id': transaction_id}
        update_data = {'received_date': received_date}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def update(self, transaction_id: str, payment_data: dict):
        cond = {'transaction_id': transaction_id}
        update_query = self.query_gen.update(self.table_name, cond, payment_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected
