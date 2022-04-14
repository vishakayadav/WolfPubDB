"""
Module for handling employees
"""

import random

from wolfpub.api.utils.custom_exceptions import MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import EMPLOYEES, WRITE_BOOKS, WRITE_ARTICLES, REVIEW_PUBLICATION, AUTHORS, EDITORS


class EmployeesHandler(object):
    """
    Focuses on providing functionality for employees
    """

    def __init__(self, db):
        self.db = db
        self.table_name = EMPLOYEES['table_name']
        self.author_table_name = AUTHORS['table_name']
        self.editor_table_name = EDITORS['table_name']
        self.book_author_table_name = f"{EMPLOYEES['table_name']} natural join " \
                                      f"{WRITE_BOOKS['table_name']}"
        self.article_author_table_name = f"{EMPLOYEES['table_name']} natural join " \
                                         f"{WRITE_ARTICLES['table_name']}"

        self.editor_publication_table_name = REVIEW_PUBLICATION['table_name']
        self.query_gen = QueryGenerator()

    # Generate employee ID based on job type
    @staticmethod
    def get_employee_id(employee: dict):
        try:
            cw_type = employee.pop('cw_type', 'author').lower()
            status = employee.pop('status', 'staff').lower()
            emp_no = str(random.randint(1000, 9999))
            if cw_type == 'author' and status == 'staff':
                emp_id = "AS" + emp_no
            elif cw_type == 'editor' and status == 'staff':
                emp_id = "ES" + emp_no
            elif cw_type == 'author' and status == 'invited':
                emp_id = "AG" + emp_no
            elif cw_type == 'editor' and status == 'invited':
                emp_id = "EG" + emp_no
            else:
                raise ValueError('Cannot generate valid employee ID')
            return emp_id
        except ValueError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    # Create new employee
    def set(self, employee: dict, content_writer: dict):
        cw_type = employee['cw_type']
        emp_id = self.get_employee_id(employee)
        employee['emp_id'] = emp_id
        content_writer['emp_id'] = emp_id

        cursor = self.db.get_cursor()
        self.db.conn.autocommit = False
        try:
            insert_query = self.query_gen.insert(self.table_name, [employee])
            _, last_row_id = self.db._execute(insert_query, cursor)
            if cw_type == "author":
                insert_query = self.query_gen.insert(self.author_table_name, [content_writer])
                _, last_row_id = self.db._execute(insert_query, cursor)
            else:
                content_writer.pop('author_type')
                insert_query = self.query_gen.insert(self.editor_table_name, [content_writer])
                _, last_row_id = self.db._execute(insert_query, cursor)

            self.db.conn.commit()
        except (MariaDBException, Exception) as e:
            self.db.conn.rollback()
            raise e

        return {'emp_id': emp_id}

    # Fetch existing employee
    def get(self, emp_id: str):
        cond = {'emp_id': emp_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    # Update employee
    def update(self, emp_id: str, update_data: dict):
        cond = {'emp_id': emp_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    # Remove employee
    def remove(self, emp_id: str):
        cond = {'emp_id': emp_id}
        cursor = self.db.get_cursor()
        self.db.conn.autocommit = False
        try:
            delete_query = self.query_gen.delete(self.author_table_name, cond)
            row_affected, _ = self.db._execute(delete_query, cursor)
            if row_affected < 1:
                delete_query = self.query_gen.delete(self.editor_table_name, cond)
                row_affected, _ = self.db._execute(delete_query, cursor)

            delete_query = self.query_gen.delete(self.table_name, cond)
            row_affected, _ = self.db._execute(delete_query, cursor)

            self.db.conn.commit()
        except (MariaDBException, Exception) as e:
            self.db.conn.rollback()
            raise e

        return row_affected

    # Fetch publications for an author based on writer or journalist
    def get_author_publications(self, emp_id: str, author_type: str):
        cond = {'emp_id': emp_id}
        if author_type == "writer":
            select_cols = ['emp_id', 'publication_id']
            select_query = self.query_gen.select(self.book_author_table_name, select_cols, cond)
            author_books = self.db.get_result(select_query)
            return author_books
        elif author_type == "journalist":
            select_cols = ['emp_id', 'publication_id', 'article_id']
            select_query = self.query_gen.select(self.article_author_table_name, select_cols, cond)
            author_articles = self.db.get_result(select_query)
            return author_articles

    # Fetch publications for an editor
    def get_editor_publications(self, emp_id: str):
        cond = {'emp_id': emp_id}
        select_cols = ['emp_id', 'publication_id']
        select_query = self.query_gen.select(self.editor_publication_table_name, select_cols, cond)
        return self.db.get_result(select_query)
