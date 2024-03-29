"""
Account Controller
"""

import copy
import json
from datetime import datetime, date

from flask import request
from flask_restplus import Resource

from build.lib.wolfpub.api.handlers.orders import OrderHandler
from wolfpub.api.handlers.account import AccountHandler, AccountBillHandler
from wolfpub.api.handlers.distributor import DistributorHandler
from wolfpub.api.handlers.publication import PublicationHandler, BookHandler, PeriodicalHandler
from wolfpub.api.models.serializers import PAYMENT_ARGUMENTS, ORDER_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('accounts', description='Route for distributor\'s account with Wolf Pub.')

# Creating handler objects
mariadb = MariaDBConnector()
distributor_handler = DistributorHandler(mariadb)
account_handler = AccountHandler(mariadb)
account_bill_handler = AccountBillHandler(mariadb)
publication_handler = PublicationHandler(mariadb)
book_handler = BookHandler(mariadb)
periodical_handler = PeriodicalHandler(mariadb)
order_handler = OrderHandler(mariadb)


@ns.route("/<string:account_id>")
class Account(Resource):
    """
    Focuses on fetching distributor details from account registered with WolfPubDB.
    """

    # Fetch account details
    def get(self, account_id):
        """
        End-point to get the existing distributors details
        """
        try:
            output = account_handler.get(account_id)
            return CustomResponse(data=output)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


# Creating new orders from an account
@ns.route("/<string:account_id>/orders")
class AccountOrders(Resource):
    """
    Focuses on managing orders for an account of WolfPubDB.
    """

    @ns.expect(ORDER_ARGUMENTS, validate=True)
    def post(self, account_id):
        """
        End-point to enable distributors place new orders via their account
        """
        try:
            account_handler.get(account_id)
            order = json.loads(request.data)
            order['account_id'] = account_id

            # removed this constraint just to enable demo data insertion. TODO: Revert after Demo date
            # if datetime.strptime(order['delivery_date'], "%Y-%m-%d").date() <= date.today():
            #     raise ValueError('Delivery Date has to be ahead of date of placing Order')

            # Read order date
            if 'order_date' not in order:
                order['order_date'] = datetime.today().strftime('%Y-%m-%d')

            # Read order items
            pub_items = order.pop('items')  # isbn, quantity
            items = copy.deepcopy(pub_items)
            books = book_handler.get_ids({'items': items['books']}) if items['books'] else []  # pub_id, isbn, price
            periodicals = periodical_handler.get_ids({'items': items['periodicals']}) if items['periodicals'] else []
            books = [{**u, **v} for u in books for v in pub_items['books']
                     if u['title'] == v['title'] and int(u['edition']) == int(v['edition'])]  # add quantity
            periodicals = [{**u, **v} for u in periodicals for v in pub_items['periodicals']
                           if u['title'] == v['title'] and u['issue'] == v['issue']]

            # Prepare order price and shipping cost
            order['total_price'] = order_handler.get_total_price(books + periodicals)
            if 'shipping_cost' not in order:
                shipping_cost = 2 * (sum([b['quantity'] for b in books]) + sum([p['quantity'] for p in periodicals]))
                order['shipping_cost'] = 100 if shipping_cost > 100 else shipping_cost

            if not books and not periodicals:
                raise ValueError("Publications to be ordered not found with WolfPub Publication House")
            order.update(order_handler.set(order, books, periodicals))
            try:
                bill = account_bill_handler.create_bill(account_id, order, bill_date=order['order_date'])
                msg = f"Order Placed! Bill Generated with Id {bill['bill_id']}"
            except Exception:
                msg = "Order Placed! Bill Generation Failed"
            return CustomResponse(data=order, message=msg)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


# Fetch an order for an account
@ns.route("/<string:account_id>/orders/<string:order_id>")
class AccountOrder(Resource):
    """
    Focuses on fetching order details placed by distributor from WolfPubDB.
    """

    def get(self, account_id, order_id):
        """
        End-point to get the existing order details
        """
        try:
            # GET request for account id and order id
            account_handler.get(account_id)
            output = order_handler.get_order(account_id, order_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={}, message=f"Order with id '{order_id}' Not Found for given Account Id",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


# Generate bill for an order of an account
@ns.route("/<string:account_id>/orders/<string:order_id>/bills")
class AccountOrderBills(Resource):
    """
    Focuses on managing the account's bill for distributors of WolfPubDB.
    """

    def post(self, account_id, order_id):
        """
        End-point to add bill to the distributor's account for the orders placed by the distributor
        """
        try:
            # Create bill for order of an account if it doesn't exist
            account_handler.get(account_id)
            order = order_handler.get_order(account_id, order_id)
            try:
                bill = account_bill_handler.get(account_id, order_id)
                return CustomResponse(data=bill, message='Bill already existed')
            except IndexError:
                bill_id = account_bill_handler.create_bill(account_id, order)
            return CustomResponse(data=bill_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


# Generate bills for an account
@ns.route("/<string:account_id>/bills")
class AccountBills(Resource):
    """
    Focuses on managing the account's bill for distributors of WolfPubDB.
    """

    def post(self, account_id):
        """
        End-point to add bill to the distributor's account for the orders placed by the distributor
        """
        try:
            # Get orders for an account
            account_handler.get(account_id)
            orders = order_handler.get_orders(account_id)
            bill_ids = []
            # Generate bill for each order
            for order in orders:
                try:
                    account_bill_handler.get(account_id, order['order_id'])
                except IndexError:
                    bill_ids.append(account_bill_handler.create_bill(account_id, order)['bill_id'])
            return CustomResponse(data={'bill_ids': bill_ids})
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)


# Create payments towards an account
@ns.route("/<string:account_id>/payments")
class AccountPayments(Resource):
    """
    Focuses on manage the payments from distributors of WolfPubDB.
    """

    @ns.expect(PAYMENT_ARGUMENTS, validate=True)
    def post(self, account_id):
        """
        End-point to add payment details and change outstanding balance of distributor’s account on receiving payment
        """
        try:
            # Create payment for an account
            account_handler.get(account_id)
            payment = json.loads(request.data)
            payment_id = account_bill_handler.pay_bills(account_id, payment['amount'],
                                                        payment.get('payment_date', ''))
            return CustomResponse(data=payment_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
        except IndexError as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=404)
