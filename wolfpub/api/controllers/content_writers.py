"""
To handle the Content writers, their payments and their work
"""

import json

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.content_writers import ContentWritersHandler
from wolfpub.api.handlers.authors import AuthorsHandler
from wolfpub.api.handlers.editors import EditorsHandler

from wolfpub.api.models.serializers import CONTENT_WRITER_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('contentWriters', description='Route admin for content writer actions.')

mariadb = MariaDBConnector()
content_writers_handler = ContentWritersHandler(mariadb)
authors_handler = AuthorsHandler(mariadb)
editors_handler = EditorsHandler(mariadb)


@ns.route("")
class ContentWriters(Resource):
    """
    Focuses on content writer operations in WolfPubDB.
    """

    @ns.expect(CONTENT_WRITER_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to creating new content writers
        """
        try:
            content_writer = json.loads(request.data)
            cw_type = request.args.get('employee', None)
            content_writer['cw_type'] = cw_type
            employee = {
                'type': content_writer.get('emp_type', 'Staff')
            }
            if cw_type not in ['author', 'editor']:
                raise ValueError('Employee must either be an author or an editor')
            emp_id = content_writers_handler.set(content_writer)
            employee.update(emp_id)
            if cw_type == "author":
                authors_handler.set(employee)
            else:
                editors_handler.set(employee)
            return CustomResponse(data=emp_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:emp_id>")
class ContentWriters(Resource):
    """
    Focuses on fetching, updating and deleting employee details from WolfPubDB.
    """

    def get(self, emp_id):
        """
        End-point to get the existing content writer details
        """
        try:
            output = content_writers_handler.get(emp_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={}, message=f"Employee with id '{emp_id}' not found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(CONTENT_WRITER_ARGUMENTS, validate=False, required=False)
    def put(self, emp_id):
        """
        End-point to update the content writer
        """
        try:
            content_writer = json.loads(request.data)
            emp_type = content_writer.pop('emp_type', None)
            row_affected = content_writers_handler.update(emp_id, content_writer)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"No updates made for employee with id '{emp_id}'",
                                      status_code=404)
            employee = {}
            if emp_type:
                employee['type'] = emp_type
                row_affected = authors_handler.update(emp_id, employee)
                if row_affected < 1:
                    return CustomResponse(data={},
                                          message=f"Employee type could not be updated for employee with id '{emp_id}'",
                                          status_code=206)
            return CustomResponse(data={}, message="Employee details updated")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, emp_id):
        """
        End-point to delete content writer
        """
        try:
            row_affected = content_writers_handler.remove(emp_id)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Employee with id '{emp_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Employee is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
