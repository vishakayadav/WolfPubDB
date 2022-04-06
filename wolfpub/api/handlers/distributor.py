"""
Module for Handling Distributors
"""

from wolfpub.api.utils.query_generator import QueryGenerator


class DistributorHandler(object):
    """
    Focuses on providing functionality over Distributors
    """

    def __init__(self, db):
        self.db = db
        self.table_name = 'distributors'
        self.query_gen = QueryGenerator()

    def set(self, distributor: dict):
        insert_query = self.query_gen.insert(self.table_name, distributor)
        self.db.execute([insert_query])
        condition = {'phone_number': distributor['phone_number']}
        select_query = self.query_gen.select(self.table_name, ['distributor_id'], condition)
        return self.db.get_result(select_query)[0]

    def get(self, distributor_id: str):
        cond = {'distributor_id': distributor_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def update(self, distributor_id: str, update_data: dict):
        cond = {'distributor_id': distributor_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        return self.db.execute([update_query])

    def remove(self, distributor_id: str):
        cond = {'distributor_id': distributor_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        return self.db.execute([delete_query])
