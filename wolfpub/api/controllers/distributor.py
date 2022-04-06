"""
To handle the Distributor and its account
"""

import json

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.handlers.account import AccountHandler
from wolfpub.api.models.serializers import DISTRIBUTOR_ARGUMENTS, REGISTER_ARGUMENT
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('distributors', description='Route admin for distributor actions.')

mariadb = MariaDBConnector()
distributor_handler = DistributorHandler(mariadb)
account_handler = AccountHandler(mariadb)


@ns.route("")
class Distributors(Resource):
    """
    Focuses on setting distributor in WolfPubDB.
    """

    @ns.expect(DISTRIBUTOR_ARGUMENTS, REGISTER_ARGUMENT, validate=True)
    def post(self):
        """
        End-point to set new distributor and register its account
        """
        try:
            distributor = json.loads(request.data)
            to_register = request.args.get('register', False)
            to_register = True if to_register == 'true' else False
            account = {'contact_email': distributor.pop('contact_email', None),
                       'periodicity': distributor.pop('periodicity', None)}
            if to_register and not (account['contact_email'] and account['periodicity']):
                raise ValueError(
                    'Contact Email and Periodicity are mandatory field to registry the account of distributor')
            dist_id = distributor_handler.set(distributor)
            if to_register:
                account.update(dist_id)
                dist_id.update(account_handler.register(account))
            return CustomResponse(data=dist_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
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
        try:
            output = distributor_handler.get(distributor_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={}, message=f"Distributor with id '{distributor_id}' Not Found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(DISTRIBUTOR_ARGUMENTS, validate=False, required=False)
    def put(self, distributor_id):
        """
        End-point to update the distributor
        """
        try:
            distributor = json.loads(request.data)
            contact_email = distributor.pop('contact_email', None),
            periodicity = distributor.pop('periodicity', None)
            account = {}
            if contact_email:
                account['contact_email'] = contact_email
            if periodicity:
                account['periodicity'] = periodicity
            row_affected = distributor_handler.update(distributor_id, distributor)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Distributor with id '{distributor_id}' Not Found",
                                      status_code=404)
            if account:
                row_affected = account_handler.update(distributor_id=distributor_id, update_data=account)
                if row_affected < 1:
                    return CustomResponse(data={},
                                          message=f"Contact Email and Periodicity not updated - Account not registered with WolfPub",
                                          status_code=206)
            return CustomResponse(data={}, message="Distributor details Updated")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, distributor_id):
        """
        End-point to delete distributor
        """
        try:
            row_affected = distributor_handler.remove(distributor_id)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Distributor with id '{distributor_id}' Not Found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Distributor is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
