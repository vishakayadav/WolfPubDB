"""
To handle the configuration of Data Gaps Job
"""

import json

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.models.serializers import DISTRIBUTOR_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector


ns = api.namespace('distributors', description='Route admin for distributor actions.')

distributor_handler = DistributorHandler(MariaDBConnector())


@ns.route("")
class Distributors(Resource):
    """
    Focuses on setting distributor in WolfPubDB.
    """
    @ns.expect(DISTRIBUTOR_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to set new distributor and register its account
        """
        try:
            distributor = json.loads(request.data)
            account = {'contact_email': distributor.pop('contact_email'),
                       'periodicity': distributor.pop('periodicity')}
            dist_id = distributor_handler.set(distributor)
            account.update(dist_id)
            output = distributor_handler.register(account)
            output.update(dist_id)
            return CustomResponse(data=output)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:distributor_id>")
class Distributor(Resource):
    """
    Focuses on fetching, updating and deleting distributor from WolfPubDB.
    """

    def get(self, distributor_id):
        """
        End-point to get the existing distributors details
        """
        pass

    def delete(self, distributor_id):
        """
        End-point to delete distributor
        """
        try:
            output = distributor_handler.remove(distributor_id)
            return CustomResponse(data=output, message='Distributor is deleted')
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
