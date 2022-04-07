"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""

from wolfpub.api.utils.query_generator import QueryGenerator


class PublicationHandler(object):
    """
    Focuses on providing functionality over Publications of WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = 'publications'
        self.primary_key = 'publication_id'
        self.secondary_key = []
        self.columns = ['publication_id', 'title', 'topic', 'publication_date', 'price']
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
        self.table_name = 'books'
        self.secondary_key = ['book_id', 'edition']
        self.columns = ['publication_id', 'isbn', 'creation_date', 'book_id', 'edition', 'is_available']


class PeriodicalHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = 'periodicals'
        self.secondary_key = ['periodical_id', 'issue']
        self.columns = ['publication_id', 'issn', 'periodical_type', 'periodical_id', 'issue', 'is_available']
