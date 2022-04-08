"""
Module for Handling Content Writers
"""

from wolfpub.api.utils.query_generator import QueryGenerator


class ContentWritersHandler(object):
    """
    Focuses on providing functionality for Content Writers
    """

    def __init__(self, db):
        self.db = db
        self.table_name = 'content_writers'
        self.query_gen = QueryGenerator()

    def set(self, content_writer: dict):
        insert_query = self.query_gen.insert(self.table_name, [content_writer])
        _, last_row_id = self.db.execute([insert_query])
        return {'distributor_id': last_row_id}

    def get(self, emp_id: str):
        cond = {'emp_id': emp_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def update(self, emp_id: str, update_data: dict):
        cond = {'emp_id': emp_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, emp_id: str):
        cond = {'emp_id': emp_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected
