"""
To handle the Distributor and its account
"""
import copy
import json
from datetime import datetime, date

from flask import request
from flask_restplus import Resource

from build.lib.wolfpub.api.handlers.orders import OrderHandler
from wolfpub.api.handlers.publication import PublicationHandler, BookHandler, PeriodicalHandler

from wolfpub.api.handlers.account import AccountHandler, AccountBillHandler
from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.models.serializers import DISTRIBUTOR_ARGUMENTS, REGISTER_ARGUMENT, PAYMENT_ARGUMENTS, ORDER_ARGUMENTS
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
            return CustomResponse(data=output)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)

    @ns.expect(DISTRIBUTOR_ARGUMENTS, validate=False, required=False)
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
            row_affected = distributor_handler.update(distributor_id, distributor)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"No Updates made for Distributor with id '{distributor_id}'",
                                      status_code=404)
            if account:
                row_affected = account_handler.update(distributor_id=distributor_id, update_data=account)
                if row_affected < 1:
                    return CustomResponse(data={},
                                          message=f"Contact Email and Periodicity not updated - Account not registered with WolfPub",
                                          status_code=206)
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


@ns.route("/<string:distributor_id>/accounts/<string:account_id>/orders")
class Orders(Resource):
    """
    Focuses on managing orders of WolfPubDB.
    """

    @ns.expect(ORDER_ARGUMENTS, validate=True)
    def post(self, distributor_id, account_id):
        """
        End-point to enable distributors place new orders via their account
        """
        try:
            distributor_handler.get(distributor_id)
            order = json.loads(request.data)
            order['account_id'] = account_id
            if datetime.strptime(order['delivery_date'], "%Y-%m-%d").date() <= date.today():
                raise ValueError('Delivery Date has to be ahead of date of placing Order')
            order['order_date'] = datetime.today().strftime('%Y-%m-%d')
            pub_items = order.pop('items')  # book_id, edition, quantity
            items = copy.deepcopy(pub_items)
            books = book_handler.get_ids({'items': items['books']})  # pub_id, book_id, edition
            periodicals = periodical_handler.get_ids({'items': items['periodicals']})
            if books:
                books_price = publication_handler.get_by_id([pub['publication_id'] for pub in books],
                                                            ['publication_id, price'])  # pub_id, price
                books = [{**u, **v, **w} for u, v, w in zip(pub_items['books'], books, books_price)]  # add quantity
            if periodicals:
                periodicals_price = publication_handler.get_by_id([pub['publication_id'] for pub in periodicals],
                                                                  ['publication_id, price'])  # pub_id, price
                periodicals = [{**u, **v, **w} for u, v, w in zip(pub_items['periodicals'], periodicals,
                                                                  periodicals_price)]
            order['total_price'] = order_handler.get_total_price(books + periodicals)
            shipping_cost = 2 * (len(books) + len(periodicals))
            order['shipping_cost'] = 100 if shipping_cost > 100 else shipping_cost
            order_id = order_handler.set(order, books, periodicals)
            return CustomResponse(data=order_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


@ns.route("/<string:distributor_id>/accounts/<string:account_id>/orders/<string:order_id>")
class Order(Resource):
    """
    Focuses on fetching order details placed by distributor from WolfPubDB.
    """

    def get(self, distributor_id, account_id, order_id):
        """
        End-point to get the existing distributors details
        """
        try:
            distributor_handler.get(distributor_id)
            output = order_handler.get(order_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={}, message=f"Order with id '{order_id}' Not Found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


@ns.route("/<string:distributor_id>/accounts/<string:account_id>/bills")
class AccountBills(Resource):
    """
    Focuses on managing the account's bill for distributors of WolfPubDB.
    """

    def post(self, distributor_id, account_id):
        """
        End-point to add bill to the distributor's account for the orders placed by the distributor
        """
        try:
            distributor_handler.get(distributor_id)
            bill_id = account_bill_handler.create_bill(account_id)
            return CustomResponse(data=bill_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


@ns.route("/<string:distributor_id>/accounts/<string:account_id>/payments")
class AccountBills(Resource):
    """
    Focuses on manage the payments from distributors of WolfPubDB.
    """

    @ns.expect(PAYMENT_ARGUMENTS, validate=True)
    def post(self, distributor_id, account_id):
        """
        End-point to add payment details and change outstanding balance of distributor’s account on receiving payment
        """
        try:
            distributor_handler.get(distributor_id)
            payment = json.loads(request.data)
            payment_id = account_bill_handler.pay_bills(account_id, payment['amount'])
            return CustomResponse(data=payment_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)
