"""
Module for Handling Content Writers
"""

import random
from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.constants import CONTENT_WRITERS


class ContentWritersHandler(object):
    """
    Focuses on providing functionality for Content Writers
    """

    def __init__(self, db):
        self.db = db
        self.table_name = CONTENT_WRITERS['table_name']
        self.query_gen = QueryGenerator()

    @staticmethod
    def get_employee_id(content_writer: dict):
        try:
            cw_type = content_writer.pop('cw_type', 'author')
            emp_type = content_writer.pop('emp_type', 'Staff')
            emp_no = str(random.randint(1000, 9999))
            if cw_type == 'author' and emp_type == 'Staff':
                emp_id = "AS" + emp_no
            elif cw_type == 'editor' and emp_type == 'Staff':
                emp_id = "ES" + emp_no
            elif cw_type == 'author' and emp_type == 'Guest':
                emp_id = "AG" + emp_no
            elif cw_type == 'editor' and emp_type == 'Guest':
                emp_id = "EG" + emp_no
            else:
                raise ValueError('Cannot generate valid employee ID')
            return emp_id
        except ValueError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def set(self, content_writer: dict):
        emp_id = self.get_employee_id(content_writer)
        content_writer['emp_id'] = emp_id
        insert_query = self.query_gen.insert(self.table_name, [content_writer])
        _, last_row_id = self.db.execute([insert_query])
        return {'emp_id': emp_id}

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
