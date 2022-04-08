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
        self.columns = PUBLICATIONS['columns']
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

    def get_by_id(self, publication_ids: list, select_cols: list = None):
        if select_cols is None:
            select_cols = ['*']
        if isinstance(publication_ids, str) or isinstance(publication_ids, int):
            publication_ids = [publication_ids]
        select_query = self.query_gen.select(self.table_name, select_cols, {'publication_id': publication_ids})
        return self.db.get_result(select_query)

    def get_ids(self, condition):
        self.secondary_key.append(self.primary_key)
        self.reformat(condition)
        select_query = self.query_gen.select(self.table_name, self.secondary_key, condition)
        return self.db.get_result(select_query)


class BookHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = BOOKS['table_name']
        self.secondary_key = ['book_id', 'edition']
        self.columns = BOOKS['columns']


class PeriodicalHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = PERIODICALS['table_name']
        self.secondary_key = ['periodical_id', 'issue']
        self.columns = PERIODICALS['columns']
