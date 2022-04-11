"""
To handle the Content writers, their payments and their work
"""

import json

from flask import request
from flask_restplus import Resource
from datetime import date, datetime

from wolfpub.api.handlers.publication import PublicationHandler
from wolfpub.api.handlers.publication import BookHandler
from wolfpub.api.handlers.publication import PeriodicalHandler

from wolfpub.api.models.serializers import PUBLICATION_ARGUMENTS
from wolfpub.api.models.serializers import BOOK_ARGUMENTS
from wolfpub.api.models.serializers import PERIODICAL_ARGUMENTS
from wolfpub.api.models.serializers import CHAPTER_ARGUMENTS
from wolfpub.api.models.serializers import ARTICLE_ARGUMENTS
from wolfpub.api.models.serializers import PUBLICATION_AUTHOR_ARGUMENTS
from wolfpub.api.models.serializers import PUBLICATION_EDITOR_ARGUMENTS

from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('publication', description='Route admin for publication actions.')

mariadb = MariaDBConnector()
publication_handler = PublicationHandler(mariadb)
book_handler = BookHandler(mariadb)
periodical_handler = PeriodicalHandler(mariadb)


@ns.route("/book")
class Book(Resource):
    """
    Focuses on book operations in WolfPubDB.
    """

    @ns.expect(PUBLICATION_ARGUMENTS, BOOK_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to create new book
        """
        try:
            publication = json.loads(request.data)
            isbn = publication.pop('isbn', None)
            if isbn is None:
                isbn = book_handler.generate_random_isbn()
            creation_date = publication.pop('creation_date')
            publication_date = publication.get('publication_date')
            if datetime.strptime(creation_date, "%Y-%m-%d").date() > datetime.strptime(publication_date, "%Y-%m-%d").date():
                raise ValueError('Creation date has to be before publication date')
            is_available = int(publication.pop('is_available', 1))
            book = {
                'isbn': isbn,
                'edition': 1,
                'creation_date': creation_date,
                'is_available': is_available
            }
            book_id = book_handler.get_id(publication.get('Title', None))
            print(book_id)
            if book_id is not None:
                book['book_id'] = book_id
                edition = book_handler.get_edition(book_id)
                book['edition'] = edition
            else:
                book['book_id'] = book_handler.new_book_id()
            print(publication)
            print(book)
            publication_id = publication_handler.set(publication)
            book.update(publication_id)
            book_handler.set(book)
            return CustomResponse(data=publication_id)
        except (QueryGenerationException, MariaDBException, ValueError, KeyError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except Exception as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/periodical")
class Periodical(Resource):
    """
    Focuses on periodical operations in WolfPubDB.
    """

    @ns.expect(PUBLICATION_ARGUMENTS, PERIODICAL_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to create new periodical
        """
        try:
            publication = json.loads(request.data)
            issn = publication.pop('issn', None)
            if issn is None:
                issn = periodical_handler.generate_random_issn()
            issue = publication.pop('issue')
            periodical_type = publication.pop('periodical_type')
            if periodical_type == "Magazine" and not issue.startswith('Week'):
                raise ValueError("Magazines must be published weekly. Expected input format - `Week<num>`")
            elif periodical_type == "Journal" and not issue.startswith('Month'):
                raise ValueError("Journals must be published monthly. Expected input format - `Month<num>`")
            elif periodical_type not in ["Magazine", "Journal"]:
                raise ValueError("Periodicals must either be a magazine or a journal")
            is_available = int(publication.pop('is_available', 1))
            periodical = {
                'issn': issn,
                'issue': issue,
                'publication_type': periodical_type,
                'is_available': is_available
            }
            periodical_id = periodical_handler.get_id(publication.get('Title', None))
            print(periodical_id)
            if periodical_id is not None:
                periodical['periodical_id'] = periodical_id
            else:
                periodical['periodical_id'] = periodical_handler.new_periodical_id()
            print(publication)
            print(periodical)
            publication_id = publication_handler.set(publication)
            periodical.update(publication_id)
            periodical_handler.set(periodical)
            return CustomResponse(data=publication_id)
        except (QueryGenerationException, MariaDBException, ValueError, KeyError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except Exception as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>")
class Publication(Resource):
    """
    Focuses on publication operations in WolfPubDB.
    """

    def get(self, publication_id):
        """
        End-point to get the existing publication details
        """
        try:
            output = publication_handler.get_by_id(publication_id)
            if len(output) == 0:
                return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                      status_code=404)
            publication = output[0]
            book_output = book_handler.get(publication_id)
            if len(book_output) > 0:
                publication.update(book_output[0])
            else:
                periodical_output = periodical_handler.get(publication_id)
                if len(periodical_output) > 0:
                    publication.update(periodical_output[0])
                else:
                    return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                          status_code=404)

            return CustomResponse(data=publication)

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(PUBLICATION_ARGUMENTS, BOOK_ARGUMENTS, PERIODICAL_ARGUMENTS, validate=False, required=False)
    def put(self, publication_id):
        """
        End-point to update the publication
        """
        try:
            publication = json.loads(request.data)
            row_affected = publication_handler.update(publication_id, publication)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"No updates made for publication with id '{publication}'",
                                      status_code=404)
            return CustomResponse(data={}, message="Publication details updated")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, publication_id):
        """
        End-point to delete publication
        """
        try:
            output = publication_handler.get_by_id(publication_id)
            if len(output) == 0:
                return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                      status_code=404)
            else:
                book_row_affected = book_handler.remove(publication_id)
                if book_row_affected < 1:
                    periodical_row_affected = periodical_handler.remove(publication_id)
                    if periodical_row_affected < 1:
                        return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                              status_code=404)
                return CustomResponse(data={}, message="Publication is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/chapter")
class Chapter(Resource):
    """
    Focuses on chapter operations in WolfPubDB.
    """

    @ns.expect(CHAPTER_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to create new chapter
        """
        try:
            chapter = json.loads(request.data)
            chapter_id = book_handler.set_chapter(chapter)
            return CustomResponse(data=chapter_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/chapter/<string:chapter_id>")
class Chapter(Resource):
    """
    Focuses on chapter operations in WolfPubDB.
    """

    def get(self, publication_id, chapter_id):
        """
        End-point to get the existing chapter details
        """
        try:
            output = book_handler.get_chapter(publication_id, chapter_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={},
                                  message=f"Chapter with id '{chapter_id}' for publication with id '{publication_id}' not found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(CHAPTER_ARGUMENTS, validate=False, required=False)
    def put(self, publication_id, chapter_id):
        """
        End-point to update the chapter
        """
        try:
            chapter = json.loads(request.data)
            row_affected = book_handler.update_chapter(publication_id, chapter_id, chapter)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"No updates made for chapter with id '{chapter_id}' for publication with id '{publication_id}'",
                                      status_code=404)
            return CustomResponse(data={}, message="Chapter details updated")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, publication_id, chapter_id):
        """
        End-point to delete chapter
        """
        try:
            row_affected = book_handler.remove_chapter(publication_id, chapter_id)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Chapter with id '{chapter_id}' for publication with id '{publication_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Chapter is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/article")
class Article(Resource):
    """
    Focuses on article operations in WolfPubDB.
    """

    @ns.expect(ARTICLE_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to create new article
        """
        try:
            article = json.loads(request.data)
            article_id = publication_handler.set(article)
            return CustomResponse(data=article_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/article/<string:article_id>")
class Article(Resource):
    """
    Focuses on article operations in WolfPubDB.
    """

    def get(self, publication_id, article_id):
        """
        End-point to get the existing article details
        """
        try:
            output = periodical_handler.get_article(publication_id, article_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={},
                                  message=f"Article with id '{article_id}' for publication with id '{publication_id}' not found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(ARTICLE_ARGUMENTS, validate=False, required=False)
    def put(self, publication_id, article_id):
        """
        End-point to update the article
        """
        try:
            article = json.loads(request.data)
            row_affected = periodical_handler.update_article(publication_id, article_id, article)
            if row_affected < 1:
                return CustomResponse(data={},
                                      message=f"No updates made for article with id '{article_id}' for publication with id '{publication_id}'",
                                      status_code=404)
            return CustomResponse(data={}, message="Article details updated")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, publication_id, article_id):
        """
        End-point to delete article
        """
        try:
            row_affected = periodical_handler.remove_article(publication_id, article_id)
            if row_affected < 1:
                return CustomResponse(data={},
                                      message=f"Article with id '{article_id}' for publication with id '{publication_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Article is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/author")
class Publication(Resource):
    """
    Focuses on publication associations in WolfPubDB.
    """

    @ns.expect(PUBLICATION_AUTHOR_ARGUMENTS, validate=True)
    def post(self, publication_id):
        """
        End-point to associate authors with a publication
        """
        try:
            output = publication_handler.get_by_id(publication_id)
            if len(output) == 0:
                return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                      status_code=404)
            authors = json.loads(request.data).pop("author", None)
            if authors is None or len(authors) == 0:
                raise ValueError('Must provide author IDs to associate with publication')
            if len(authors) > 5:
                raise ValueError('Can associate only 5 authors with a publication at a time')

            authors_associated = 0
            for author in authors:
                association = {
                    'emp_id': author,
                    'publication_id': publication_id
                }
                publication_handler.set_author(association)
                authors_associated += 1
            return CustomResponse(data={}, message=f"'{authors_associated} authors added to publication with id '{publication_id}")

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/editor")
class Publication(Resource):
    """
    Focuses on publication associations in WolfPubDB.
    """

    @ns.expect(PUBLICATION_EDITOR_ARGUMENTS, validate=True)
    def post(self, publication_id):
        """
        End-point to associate editors with a publication
        """
        try:
            output = publication_handler.get_by_id(publication_id)
            if len(output) == 0:
                return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                      status_code=404)
            editors = json.loads(request.data).pop("editor", None)
            if editors is None or len(editors) == 0:
                raise ValueError('Must provide editor IDs to associate with publication')
            if len(editors) > 5:
                raise ValueError('Can associate only 5 editors with a publication at a time')

            editors_associated = 0
            for editor in editors:
                association = {
                    'emp_id': editor,
                    'publication_id': publication_id
                }
                publication_handler.set_editor(association)
                editors_associated += 1
            return CustomResponse(data={}, message=f"'{editors_associated} editors added to publication with id '{publication_id}")

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/author/<string:employee_id>")
class Publication(Resource):
    """
    Focuses on publication associations in WolfPubDB.
    """

    def delete(self, publication_id, employee_id):
        """
        End-point to remove an author from a publication
        """
        try:
            row_affected = publication_handler.remove_author(publication_id, employee_id)
            if row_affected < 1:
                return CustomResponse(data={},
                                      message=f"Author with id '{employee_id}' for publication with id '{publication_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message=f"Author is removed for publication with id '{publication_id}'")

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/editor/<string:employee_id>")
class Publication(Resource):
    """
    Focuses on publication associations in WolfPubDB.
    """

    def delete(self, publication_id, employee_id):
        """
        End-point to remove an author from a publication
        """
        try:
            row_affected = publication_handler.remove_editor(publication_id, employee_id)
            if row_affected < 1:
                return CustomResponse(data={},
                                      message=f"Editor with id '{employee_id}' for publication with id '{publication_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message=f"Editor is removed for publication with id '{publication_id}'")

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

