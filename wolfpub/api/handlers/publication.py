"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import PUBLICATIONS, BOOKS, PERIODICALS


class PublicationHandler(object):
    """
    Focuses on providing functionality over Publications of WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = PUBLICATIONS['table_name']
        self.primary_key = 'publication_id'
        self.secondary_key = []
        self.columns = PUBLICATIONS['columns'].keys()
        self.query_gen = QueryGenerator()

    def reformat(self, obj):
        if isinstance(obj, list):
            for row in obj:
                for col in set(row.keys()) - set(self.columns):
                    row.pop(col)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, list):
                    self.reformat(value)

    def get_by_id(self, publication_ids, select_cols: list = None):
        if select_cols is None:
            select_cols = ['*']
        if isinstance(publication_ids, list) and len(publication_ids) == 1:
            publication_ids = publication_ids[0]
        select_query = self.query_gen.select(self.table_name, select_cols, {'publication_id': publication_ids})
        return self.db.get_result(select_query)

    def get_ids(self, condition):
        self.secondary_key.append(self.primary_key)
        self.reformat(condition)
        table = self.table_name
        if table != PUBLICATIONS['table_name']:
            table = f"{table} natural join {PUBLICATIONS['table_name']}"
        select_query = self.query_gen.select(table, ['*'], condition)
        return self.db.get_result(select_query)

    def set(self, publication: dict):
        insert_query = self.query_gen.insert(self.table_name, [publication])
        _, last_row_id = self.db.execute([insert_query])
        return {'publication_id': last_row_id}

    def update(self, publication_id: str, update_data: dict):
        cond = {'publication_id': publication_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, publication_id: str):
        cond = {'publication_id': publication_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected


class BookHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = BOOKS['table_name']
        self.secondary_key = ['book_id', 'edition']
        self.columns = list(PUBLICATIONS['columns'].keys()) + list(BOOKS['columns'].keys())

    def get(self, publication_id: str):
        cond = {'emp_id': publication_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def set(self, publication: dict):
        insert_query = self.query_gen.insert(self.table_name, [publication])
        _, last_row_id = self.db.execute([insert_query])
        return {'publication_id': last_row_id}

    def update(self, publication_id: str, update_data: dict):
        cond = {'publication_id': publication_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, publication_id: str):
        cond = {'publication_id': publication_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

    def get_chapter(self, publication_id, chapter_id):
        cond = {'publication_id': publication_id, 'chapter_id': chapter_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def remove_chapter(self, publication_id, chapter_id):
        cond = {'publication_id': publication_id, 'chapter_id': chapter_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected


class PeriodicalHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = PERIODICALS['table_name']
        self.secondary_key = ['periodical_id', 'issue']
        self.columns = list(PUBLICATIONS['columns'].keys()) + list(PERIODICALS['columns'].keys())

    def get(self, publication_id: str):
        cond = {'emp_id': publication_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def set(self, publication: dict):
        insert_query = self.query_gen.insert(self.table_name, [publication])
        _, last_row_id = self.db.execute([insert_query])
        return {'publication_id': last_row_id}

    def update(self, publication_id: str, update_data: dict):
        cond = {'publication_id': publication_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, publication_id: str):
        cond = {'publication_id': publication_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

    def get_article(self, publication_id, article_id):
        cond = {'publication_id': publication_id, 'chapter_id': article_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def remove_article(self, publication_id, article_id):
        cond = {'publication_id': publication_id, 'chapter_id': article_id}
        delete_query = self.query_gen.delete(self.table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected