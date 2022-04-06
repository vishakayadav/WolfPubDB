"""
To handle the configuration of Data Gaps Job
"""

import json

from flask import request
from flask_restplus import Resource
from micro_kit import CustomResponse

from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.models.serializers import JOB_CONFIGURATION_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.mariadb_connector import MariaDBConnector


ns = api.namespace('distributors', description='Route admin for data-gaps configuration based actions.')

config_handler = DistributorHandler(MariaDBConnector())


@ns.route("")
class Distributor(Resource):
    """
    Focuses on fetching, setting and deleting the configuration for the Data Gaps Job to be scheduled.
    """

    def get(self):
        """
        End-point to get the existing configuration for the group by columns and scheduling.
        """
        pass

    @ns.expect(JOB_CONFIGURATION_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to set new configuration for the group by columns and scheduling.
        """
        configuration = json.loads(request.data)
        output, status_code = None, None
        return CustomResponse(output['data'] if 'data' in output else {}, status_code, output['message'])

    def delete(self):
        """
        End-point to delete execution of scheduled Azkaban job
        """
        output, status_code = None, None
        return CustomResponse(output['data'] if 'data' in output else {}, status_code, output['message'])


@ns.route("/columns")
class GroupBySuggestion(Resource):
    """
    Focuses on getting the list of columns eligible to be a part of entity
    """

    def get(self):
        """
        End-point to get the suggestion for the group by columns.
        """
        output, status_code = None, None
        if isinstance(output, dict):
            return CustomResponse(output['message'], status_code)
        return CustomResponse(list(output), status_code)
