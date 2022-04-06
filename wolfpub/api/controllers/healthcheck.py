"""
Health ckeck for Data Gaps API
"""
import traceback

from flask_restplus import Resource

from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse

ns = api.namespace('healthcheck', description='Route admin for data gaps healthcheck.')


@ns.route("")
class DataGapsStatus(Resource):
    """
    Focuses on getting the status of the Data Gaps Service
    """

    def post(self):
        """
        Endpoint to check if data gaps service is running successfully or not
        """
        try:
            return CustomResponse(data={"status": "Running"}, status_code=200)
        except Exception as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
