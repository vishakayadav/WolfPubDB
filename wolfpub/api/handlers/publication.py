"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""
import random

from wolfpub.api.utils.custom_exceptions import MariaDBException
from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import PUBLICATIONS, BOOKS, PERIODICALS, CHAPTERS, ARTICLES, \
    WRITE_BOOKS, REVIEW_PUBLICATION, EMPLOYEES, WRITE_ARTICLES


class PublicationHandler(object):
    """
    Focuses on providing functionality over Publications of WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = PUBLICATIONS['table_name']
        self.editor_table_name = REVIEW_PUBLICATION['table_name']

        self.primary_key = 'publication_id'
        self.secondary_key = set()
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

    def get_by_id(self, publication_id: str, select_cols: list = None):
        cond = {'publication_id': publication_id}
        if select_cols is None:
            select_cols = ['*']
        select_query = self.query_gen.select(self.table_name, select_cols, cond)
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
        return {'publication_id': last_row_id[-1]}

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

    def set_editor(self, association):
        insert_query = self.query_gen.insert(self.editor_table_name, [association])
        row_affected, _ = self.db.execute([insert_query])
        return row_affected

    def remove_editor(self, publication_id: str, employee_id: str):
        cond = {'publication_id': publication_id, 'emp_id': employee_id}
        delete_query = self.query_gen.delete(self.editor_table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected


class BookHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = BOOKS['table_name']
        self.parent_table_name = PUBLICATIONS['table_name']
        self.chapter_table_name = CHAPTERS['table_name']
        self.secondary_key = set()
        self.secondary_key.update(['book_id', 'edition'])
        self.columns = list(PUBLICATIONS['columns'].keys()) + list(BOOKS['columns'].keys())
        self.book_filter_table_name = f"{PUBLICATIONS['table_name']} natural join " \
                                 f"{WRITE_BOOKS['table_name']} natural join " \
                                 f"{EMPLOYEES['table_name']}"
        self.book_author_table_name = WRITE_BOOKS['table_name']

    def get(self, publication_id: str):
        cond = {'publication_id': publication_id, 'is_available': 1}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def set(self, book: dict):
        insert_query = self.query_gen.insert(self.table_name, [book])
        _, last_row_id = self.db.execute([insert_query])
        return {'publication_id': last_row_id}

    def update(self, publication_id: str, update_data: dict):
        cond = {'publication_id': publication_id, 'is_available': 1}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, publication_id: str):
        cond = {'publication_id': publication_id, 'is_available': 1}
        update_data = {'is_available': 0}
        delete_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

    def set_chapter(self, chapter: dict):
        insert_query = self.query_gen.insert(self.chapter_table_name, [chapter])
        _, last_row_id = self.db.execute([insert_query])
        return {'chapter_id': last_row_id[-1]}

    def get_chapter(self, publication_id, chapter_id):
        cond = {'publication_id': publication_id, 'chapter_id': chapter_id}
        select_query = self.query_gen.select(self.chapter_table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def update_chapter(self, publication_id, chapter_id, update_data):
        cond = {'publication_id': publication_id, 'chapter_id': chapter_id}
        update_query = self.query_gen.update(self.chapter_table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove_chapter(self, publication_id, chapter_id):
        cond = {'publication_id': publication_id, 'chapter_id': chapter_id}
        delete_query = self.query_gen.delete(self.chapter_table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

    @staticmethod
    def generate_random_isbn():
        randnum = str(random.randrange(10 ** 12, 10 ** 13))
        isbn = randnum[0:3] + "-" + randnum[3] + "-" + randnum[4:6] + "-" + randnum[6:12] + "-" + randnum[12]
        return isbn

    def get_id_from_title(self, title):
        try:
            cond1 = {'title': title.lower()}
            select_query = self.query_gen.select(self.parent_table_name, ['*'], cond1)
            response = self.db.get_result(select_query)
            if len(response) == 0:
                return None
            publication_id = response[0]['publication_id']
            cond2 = {'publication_id': publication_id, 'is_available': 1}
            select_query = self.query_gen.select(self.table_name, ['*'], cond2)
            response = self.db.get_result(select_query)
            if len(response) == 0:
                return None
            book_id = response[0]['book_id']
            return book_id
        except MariaDBException as e:
            raise e

    def get_edition(self, book_id):
        cond = {'book_id': book_id, 'is_available': 1}
        select_query = self.query_gen.select(self.table_name, ['max(edition) as latest_edition'], cond)
        response = self.db.get_result(select_query)
        if len(response) == 0:
            return 1
        return response[0]['latest_edition']

    def new_book_id(self):
        select_query = self.query_gen.select(self.table_name, ['max(book_id) as book_count'], None)
        response = self.db.get_result(select_query)
        if len(response) == 0:
            return 1
        book_count = response[0]['book_count']
        if book_count is None:
            return 1
        return int(book_count) + 1

    def get_filter_result(self, condition, select_cols: list = None):
        self.secondary_key.add(self.primary_key)
        self.reformat(condition)
        if select_cols is None:
            select_cols = list(self.secondary_key)
        select_query = self.query_gen.select(self.book_filter_table_name, select_cols, condition)
        return self.db.get_result(select_query)

    def set_author(self, association):
        insert_query = self.query_gen.insert(self.book_author_table_name, [association])
        row_affected, _ = self.db.execute([insert_query])
        return row_affected

    def remove_author(self, publication_id: str, employee_id: str):
        cond = {'publication_id': publication_id, 'emp_id': employee_id}
        delete_query = self.query_gen.delete(self.book_author_table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected


class PeriodicalHandler(PublicationHandler):
    """
    Focuses on providing functionality over Books of WolfPub
    """

    def __init__(self, db):
        super().__init__(db)
        self.table_name = PERIODICALS['table_name']
        self.parent_table_name = PUBLICATIONS['table_name']
        self.article_table_name = ARTICLES['table_name']
        self.secondary_key = set()
        self.secondary_key.update(['periodical_id', 'issue'])
        self.columns = list(PUBLICATIONS['columns'].keys()) + list(PERIODICALS['columns'].keys())
        self.article_filter_table_name = f"{PUBLICATIONS['table_name']} natural join " \
                                      f"{WRITE_BOOKS['table_name']} natural join " \
                                      f"{EMPLOYEES['table_name']}"
        self.article_author_table_name = WRITE_ARTICLES['table_name']

    def get(self, publication_id: str):
        cond = {'publication_id': publication_id, 'is_available': 1}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def set(self, periodical: dict):
        insert_query = self.query_gen.insert(self.table_name, [periodical])
        _, last_row_id = self.db.execute([insert_query])
        return {'publication_id': last_row_id}

    def update(self, publication_id: str, update_data: dict):
        cond = {'publication_id': publication_id, 'is_available': 1}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove(self, publication_id: str):
        cond = {'publication_id': publication_id, 'is_available': 1}
        update_data = {'is_available': 0}
        delete_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

    def set_article(self, article: dict):
        insert_query = self.query_gen.insert(self.article_table_name, [article])
        _, last_row_id = self.db.execute([insert_query])
        return {'article_id': last_row_id[-1]}

    def get_article(self, publication_id, article_id):
        cond = {'publication_id': publication_id, 'article_id': article_id}
        select_query = self.query_gen.select(self.article_table_name, ['*'], cond)
        return self.db.get_result(select_query)

    def update_article(self, publication_id, article_id, update_data):
        cond = {'publication_id': publication_id, 'article_id': article_id}
        update_query = self.query_gen.update(self.article_table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def remove_article(self, publication_id, article_id):
        cond = {'publication_id': publication_id, 'article_id': article_id}
        delete_query = self.query_gen.delete(self.article_table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

    @staticmethod
    def generate_random_issn():
        randnum = str(random.randrange(10 ** 7, 10 ** 8))
        issn = randnum[0:4] + "-" + randnum[4:8]
        return issn

    def get_id_from_title(self, title):
        try:
            cond1 = {'title': title.lower()}
            select_query = self.query_gen.select(self.parent_table_name, ['*'], cond1)
            response = self.db.get_result(select_query)
            if len(response) == 0:
                return None
            publication_id = response[0]['publication_id']
            cond2 = {'publication_id': publication_id, 'is_available': 1}
            select_query = self.query_gen.select(self.table_name, ['*'], cond2)
            response = self.db.get_result(select_query)
            if len(response) == 0:
                return None
            periodical_id = response[0]['periodical_id']
            return periodical_id
        except MariaDBException as e:
            raise e

    def new_periodical_id(self):
        select_query = self.query_gen.select(self.table_name, ['max(periodical_id) as periodical_count'], None)
        response = self.db.get_result(select_query)
        if len(response) == 0:
            return 1
        periodical_count = response[0]['periodical_count']
        if periodical_count is None:
            return 1
        return int(periodical_count) + 1

    def get_filter_result(self, condition, select_cols: list = None):
        self.secondary_key.add(self.primary_key)
        self.reformat(condition)
        if select_cols is None:
            select_cols = list(self.secondary_key)
        select_query = self.query_gen.select(self.article_filter_table_name, select_cols, condition)
        return self.db.get_result(select_query)

    def set_author(self, association):
        insert_query = self.query_gen.insert(self.article_author_table_name, [association])
        row_affected, _ = self.db.execute([insert_query])
        return row_affected

    def remove_author(self, publication_id: str, employee_id: str):
        cond = {'publication_id': publication_id, 'emp_id': employee_id}
        delete_query = self.query_gen.delete(self.article_author_table_name, cond)
        row_affected, _ = self.db.execute([delete_query])
        return row_affected

