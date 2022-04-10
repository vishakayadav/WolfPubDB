"""
To handle the payments related to employees
"""
import json
from datetime import date, datetime

from flask import request
from flask_restplus import Resource

from wolfpub.api.handlers.salary import PaymentHandler

from wolfpub.api.models.serializers import SALARY_PAYMENT_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException, UnauthorizedOperation
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('salaries', description='Route admin for payment actions.')

mariadb = MariaDBConnector()
payment_handler = PaymentHandler(mariadb)


@ns.route("")
class Payment(Resource):
    """
    Focuses on providing functionality for payments to employees
    """

    @ns.expect(SALARY_PAYMENT_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to create new salary payments
        """
        try:
            payment = json.loads(request.data)
            send_date = payment.get('send_date', None)
            receive_date = payment.get('receive_date', None)
            if send_date is not None and receive_date is not None and \
                    datetime.strptime(receive_date, "%Y-%m-%d").date() > datetime.strptime(send_date, "%Y-%m-%d").date():
                raise ValueError('Receive date has to be after send date')
            transaction_id = payment_handler.set(payment)
            return CustomResponse(data=transaction_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:transaction_id>")
class Payment(Resource):
    """
    Focuses on providing functionality for payments to employees
    """

    def get(self, transaction_id):
        """
        End-point to get the existing transaction details
        """
        try:
            output = payment_handler.get_payment(transaction_id)
            if len(output) > 0:
                return CustomResponse(data=output[0])
            return CustomResponse(data={},
                                  message=f"Transaction with id '{transaction_id}' not found",
                                  status_code=404)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def post(self, transaction_id):
        """
        End-point to add claim date by payee
        """
        try:
            payment = json.loads(request.data)
            received_date = payment.get('received_date', None)
            row_affected = payment_handler.update_claim_date(transaction_id, received_date)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Claim date could not be updated for payment with id '{transaction_id}'",
                                      status_code=206)
            return CustomResponse(data={}, message="Payment details updated")

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.expect(SALARY_PAYMENT_ARGUMENTS, validate=False, required=False)
    def put(self, transaction_id):
        """
        End-point to update payment details
        """
        try:
            payment = json.loads(request.data)
            send_date = payment.get('send_date', None)
            receive_date = payment.get('receive_date', None)
            if send_date is not None and receive_date is not None and \
                    datetime.strptime(receive_date, "%Y-%m-%d").date() > datetime.strptime(send_date,
                                                                                           "%Y-%m-%d").date():
                raise ValueError('Receive date has to be after send date')
            row_affected = payment_handler.update(transaction_id, payment)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Details could not be updated for payment with id '{transaction_id}'",
                                      status_code=206)
            return CustomResponse(data={}, message="Payment details updated")

        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)
