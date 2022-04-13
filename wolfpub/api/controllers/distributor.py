"""
To handle the Distributor
"""
import json

from flask import request
from flask_restplus import Resource

from build.lib.wolfpub.api.handlers.orders import OrderHandler
from wolfpub.api.handlers.account import AccountHandler, AccountBillHandler
from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.handlers.publication import PublicationHandler, BookHandler, PeriodicalHandler
from wolfpub.api.models.serializers import DISTRIBUTOR_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException, UnauthorizedOperation
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('distributors', description='Route admin for distributor actions.')

mariadb = MariaDBConnector()
distributor_handler = DistributorHandler(mariadb)
account_handler = AccountHandler(mariadb)
account_bill_handler = AccountBillHandler(mariadb)
publication_handler = PublicationHandler(mariadb)
book_handler = BookHandler(mariadb)
periodical_handler = PeriodicalHandler(mariadb)
order_handler = OrderHandler(mariadb)


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
            default_email = f"{distributor['name'].replace(' ', '_').lower()}@wolfpub.com"
            account = {'distributor_id': distributor.get('distributor_id'),
                       'contact_email': distributor.pop('contact_email', default_email),
                       'periodicity': distributor.pop('periodicity', 'Monthly'),
                       'balance': distributor.pop('balance', 0.00)}
            dist_id = distributor_handler.set(distributor, account)
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
            return CustomResponse(data=output)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)

    @ns.doc(DISTRIBUTOR_ARGUMENTS, validate=False)
    def put(self, distributor_id):
        """
        End-point to update the distributor
        """
        try:
            distributor_handler.get(distributor_id)
            distributor = json.loads(request.data)
            contact_email = distributor.pop('contact_email', None)
            periodicity = distributor.pop('periodicity', None)
            account = {}
            if contact_email:
                account['contact_email'] = contact_email
            if periodicity:
                account['periodicity'] = periodicity
            row_affected = 0
            if distributor:
                row_affected = distributor_handler.update(distributor_id, distributor)
            if account:
                row_affected += account_handler.update(distributor_id=distributor_id, update_data=account)
                if row_affected < 1:
                    raise ValueError(f"No Updates made for Distributor with id '{distributor_id}'")
            return CustomResponse(data={}, message="Distributor details Updated")
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)

    def delete(self, distributor_id):
        """
        End-point to delete distributor
        """
        try:
            distributor_handler.get(distributor_id)
            row_affected = distributor_handler.remove(distributor_id)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Distributor with id '{distributor_id}' Not Found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Distributor is deleted")
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except UnauthorizedOperation as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=403)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)
