"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""

from wolfpub.api.utils.query_generator import QueryGenerator


class AccountHandler(object):
    """
    Focuses on providing functionality over account of Distributor with Publication House WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = 'accounts'
        self.query_gen = QueryGenerator()

    def register(self, account: dict):
        insert_query = self.query_gen.insert(self.table_name, account)
        self.db.execute([insert_query])
        condition = {'contact_email': account['contact_email']}
        select_query = self.query_gen.select(self.table_name, ['account_id'], condition)
        return self.db.get_result(select_query)[0]

    def get(self, account_id: str):
        cond = {'account_id': account_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def update(self, account_id: str = '', distributor_id: str = '', update_data: dict = {}):
        if not account_id and not distributor_id:
            raise ValueError("Provide either 'account_id' or 'distributor_id' to update Account")
        cond = {'account_id': account_id} if account_id else {'distributor_id': distributor_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        return self.db.execute([update_query])
