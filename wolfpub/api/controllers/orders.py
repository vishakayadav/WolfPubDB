"""
To handle the Orders placed by Distributors
"""
import copy
import json
from datetime import date, datetime

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.orders import OrderHandler
from wolfpub.api.handlers.publication import PublicationHandler, BookHandler, PeriodicalHandler
from wolfpub.api.models.serializers import ORDER_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('orders', description='Route admin for orders.')

mariadb = MariaDBConnector()
publication_handler = PublicationHandler(mariadb)
book_handler = BookHandler(mariadb)
periodical_handler = PeriodicalHandler(mariadb)
order_handler = OrderHandler(mariadb)


@ns.route("")
class Orders(Resource):
    """
    Focuses on managing orders of WolfPubDB.
    """

    @ns.expect(ORDER_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to enable distributors to place new orders via their account
        """
        try:
            order = json.loads(request.data)
            if datetime.strptime(order['delivery_date'], "%Y-%m-%d").date() <= date.today():
                raise ValueError('Delivery Date has to be ahead of date of placing Order')
            order['order_date'] = date.today().strftime('%Y-%m-%d')
            pub_items = order.pop('items')  # book_id, edition, quantity
            items = copy.deepcopy(pub_items)
            books = book_handler.get_ids({'items': items['books']})  # pub_id, book_id, edition
            periodicals = periodical_handler.get_ids({'items': items['periodicals']})
            books_price = publication_handler.get_by_id([pub['publication_id'] for pub in books],
                                                        ['publication_id, price'])  # pub_id, price
            periodicals_price = publication_handler.get_by_id([pub['publication_id'] for pub in periodicals],
                                                              ['publication_id, price'])  # pub_id, price
            books = [{**u, **v, **w} for u, v, w in zip(pub_items['books'], books, books_price)]  # add quantity
            periodicals = [{**u, **v, **w} for u, v, w in zip(pub_items['periodicals'], periodicals, periodicals_price)]
            order['total_price'] = order_handler.get_total_price(books + periodicals)
            shipping_cost = 2 * (len(books) + len(periodicals))
            order['shipping_cost'] = 100 if shipping_cost > 100 else shipping_cost
            order_id = order_handler.set(order, books, periodicals)
            return CustomResponse(data=order_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
