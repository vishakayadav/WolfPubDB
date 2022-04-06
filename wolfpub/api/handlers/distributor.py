"""
Module for Handling the Configuration for execution Data Gaps Job
"""

from wolfpub.api.utils.query_generator import QueryGenerator


class DistributorHandler(object):
    """
    Focuses on providing functionality over Data Gaps Job Configuration
    """

    def __init__(self, db):
        self.db = db
        self.query_gen = QueryGenerator()

    def set(self, distributor: dict):
        table_name = 'distributors'
        insert_query = self.query_gen.insert(table_name, distributor)
        self.db.execute([insert_query])
        condition = {'phone_number': distributor['phone_number']}
        select_query = self.query_gen.select(table_name, ['distributor_id'], condition)
        return self.db.get_result(select_query)[0]

    def register(self, account: dict):
        table_name = 'accounts'
        insert_query = self.query_gen.insert(table_name, account)
        self.db.execute([insert_query])
        condition = {'contact_email': account['contact_email']}
        select_query = self.query_gen.select(table_name, ['account_id'], condition)
        return self.db.get_result(select_query)[0]

    def remove(self, distributor_id: str):
        table_name = 'distributors'
        cond = {'distributor_id': distributor_id}
        delete_query = self.query_gen.delete(table_name, cond)
        self.db.execute([delete_query])
        return {}
