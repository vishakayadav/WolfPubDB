"""
Module for Handling Distributors
"""
from wolfpub.api.handlers.account import AccountHandler
from wolfpub.api.utils.custom_exceptions import UnauthorizedOperation

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import DISTRIBUTORS, ACCOUNTS


class DistributorHandler(object):
    """
    Focuses on providing functionality over Distributors
    """

    def __init__(self, db):
        self.db = db
        self.table_name = DISTRIBUTORS['table_name']
        self.query_gen = QueryGenerator()

    def set(self, distributor: dict, account: dict):
        insert_query = [self.query_gen.insert(self.table_name, [distributor]),
                        self.query_gen.insert(ACCOUNTS['table_name'], [account])]
        _, last_row_id = self.db.execute(insert_query)
        return {'distributor_id': last_row_id[0], 'account_id': last_row_id[1]}

    def get(self, distributor_id: str):
        cond = {'distributor_id': distributor_id, 'is_active': 1}
        select_query = self.query_gen.select(f"{self.table_name} natural join {ACCOUNTS['table_name']}", ['*'], cond)
        dist = self.db.get_result(select_query)
        if not dist:
            raise IndexError(f"Distributor with id '{distributor_id}' Not Found")
        return dist[0]

    def update(self, distributor_id: str, update_data: dict):
        cond = {'distributor_id': distributor_id, 'is_active': 1}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, distributor_id: str):
        cond = {'distributor_id': distributor_id, 'is_active': 1}
        update_data = {'is_active': 0}
        try:
            balance = AccountHandler(self.db).check_balance(distributor_id=distributor_id)
            if balance:
                raise UnauthorizedOperation("Settle the Account's balance before deleting")
        except ValueError:
            pass
        update_data = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_data])
        return row_affected
