"""
To handle the Content writers, their payments and their work
"""

import json

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.publication import PublicationHandler
from wolfpub.api.handlers.publication import BookHandler
from wolfpub.api.handlers.publication import PeriodicalHandler

from wolfpub.api.models.serializers import PUBLICATION_ARGUMENTS
from wolfpub.api.models.serializers import CHAPTER_ARGUMENTS
from wolfpub.api.models.serializers import ARTICLE_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('publication', description='Route admin for publication actions.')

mariadb = MariaDBConnector()
publication_handler = PublicationHandler(mariadb)
book_handler = BookHandler(mariadb)
periodical_handler = PeriodicalHandler(mariadb)


@ns.route("")
class Publication(Resource):
    """
    Focuses on publication operations in WolfPubDB.
    """

    @ns.expect(PUBLICATION_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to creating new publication
        """
        try:
            publication = json.loads(request.data)
            publication_type = request.args.get('publication', None)
            publication['publication_type'] = publication_type

            book = {
                'isbn': '<>',
                'creation_date': '<>',
                'edition': '<>',
                'book_id': '<>',
                'is_available': '<>'
            }

            periodical = {
                'issn': '<>',
                'issue': '<>',
                'periodical_type': '<>',
                'periodical_id': '<>',
                'is_available': '<>'
            }
            if publication not in ['book', 'periodical']:
                raise ValueError('A publication must either be a book or a periodical')

            publication_id = publication_handler.set(publication)
            if publication_type == "book":
                book.update(publication_id)
                book_handler.set(book)
            else:
                periodical.update(publication_id)
                periodical_handler.set(periodical)

            return CustomResponse(data=publication_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>")
class Publication(Resource):
    """
    Focuses on fetching, updating and deleting publication details from WolfPubDB.
    """

    def get(self, publication_id):
        """
        End-point to get the existing publication details
        """
        try:
            output = publication_handler.get_by_id(publication_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(PUBLICATION_ARGUMENTS, validate=False, required=False)
    def put(self, publication_id):  # TODO
        """
        End-point to update the publication
        """
        try:
            return 0
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, publication_id):
        """
        End-point to delete publication
        """
        try:
            row_affected = publication_handler.remove(publication_id)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Publication with id '{publication_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Publication is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

@ns.route("/<string:publication_id>/chapter")
class Chapter(Resource):
    """
    Focuses on publication operations in WolfPubDB.
    """

    @ns.expect(PUBLICATION_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to creating new publication
        """
        try:
            chapter = json.loads(request.data)
            chapter_id = publication_handler.set(chapter)
            return CustomResponse(data=chapter_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:publication_id>/chapter/<string:chapter_id>")
class Chapter(Resource):

    """
    Focuses on fetching, updating and deleting chapter details from WolfPubDB.
    """

    def get(self, publication_id, chapter_id):
        """
        End-point to get the existing publication details
        """
        try:
            output = book_handler.get_chapter(publication_id, chapter_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={}, message=f"Chapter with id '{chapter_id}' for publication with id '{publication_id}' not found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(CHAPTER_ARGUMENTS, validate=False, required=False)
    def put(self, publication_id, chapter_id):  # TODO
        """
        End-point to update the publication
        """
        try:
            return 0
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, publication_id, chapter_id):
        """
        End-point to delete publication
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
    Focuses on publication operations in WolfPubDB.
    """

    @ns.expect(ARTICLE_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to creating new publication
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
    Focuses on fetching, updating and deleting chapter details from WolfPubDB.
    """

    def get(self, publication_id, article_id):
        """
        End-point to get the existing publication details
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
    def put(self, publication_id, article_id):  # TODO
        """
        End-point to update the publication
        """
        try:
            return 0
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, publication_id, article_id):
        """
        End-point to delete publication
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