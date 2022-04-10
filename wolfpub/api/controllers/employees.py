"""
To handle the Content writers, their payments and their work
"""

import json

from flask import request
from flask_restplus import Resource
from datetime import date, datetime

from wolfpub.api.handlers.employees import EmployeesHandler
from wolfpub.api.handlers.authors import AuthorsHandler
from wolfpub.api.handlers.editors import EditorsHandler
from wolfpub.api.handlers.salary import PaymentHandler

from wolfpub.api.models.serializers import EMPLOYEE_ARGUMENTS, SALARY_PAYMENT_ARGUMENTS, \
    AUTHOR_ARGUMENTS, EDITOR_ARGUMENTS
from wolfpub.api.restplus import api
from wolfpub.api.utils.custom_exceptions import QueryGenerationException, MariaDBException, UnauthorizedOperation
from wolfpub.api.utils.custom_response import CustomResponse
from wolfpub.api.utils.mariadb_connector import MariaDBConnector

ns = api.namespace('employees', description='Route admin for employee actions.')

mariadb = MariaDBConnector()
employees_handler = EmployeesHandler(mariadb)
authors_handler = AuthorsHandler(mariadb)
editors_handler = EditorsHandler(mariadb)
payment_handler = PaymentHandler(mariadb)


@ns.route("")
class Employees(Resource):
    """
    Focuses on employee operations in WolfPubDB.
    """

    @ns.expect(EMPLOYEE_ARGUMENTS, validate=True)
    def post(self):
        """
        End-point to creating new employees
        """
        try:
            employee = json.loads(request.data)
            emp_type = employee.get('job_type', 'staff author').lower()
            status = emp_type.split(' ')[0]
            cw_type = emp_type.split(' ')[1]
            if cw_type not in ['author', 'editor']:
                raise ValueError('Employee must either be an author or an editor')
            if status not in ['staff', 'guest']:
                raise ValueError('Employee must either be staff or guest')

            employee['cw_type'] = cw_type
            employee['status'] = status
            cw = {
                'type': status,
                'payment_frequency': employee.pop('payment_frequency', 'monthly').lower(),
            }
            if cw['type'] == 'guest':
                cw['payment_frequency'] = 'once'

            author_type = employee.pop('author_type', 'writer')
            if author_type not in ['writer', 'journalist']:
                raise ValueError('Author must either be an writer or an journalist')
            cw['author_type'] = author_type

            emp_id = employees_handler.set(employee, cw)
            return CustomResponse(data=emp_id)
        except (QueryGenerationException, MariaDBException, ValueError) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:emp_id>")
class Employees(Resource):
    """
    Focuses on fetching, updating and deleting employee details from WolfPubDB.
    """

    def get(self, emp_id):
        """
        End-point to get the existing employee details
        """
        try:
            output = employees_handler.get(emp_id)
            if len(output) == 0:
                return CustomResponse(data={}, message=f"Employee with id '{emp_id}' not found",
                                  status_code=404)
            return CustomResponse(data=output[0])
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    @ns.doc(EMPLOYEE_ARGUMENTS, validate=False)
    def put(self, emp_id):
        """
        End-point to update the employee
        """
        try:
            employee = json.loads(request.data)
            row_affected = employees_handler.update(emp_id, employee)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"No updates made for employee with id '{emp_id}'",
                                      status_code=404)
            return CustomResponse(data={}, message="Employee details updated")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)

    def delete(self, emp_id):
        """
        End-point to delete employee
        """
        try:
            row_affected = employees_handler.remove(emp_id)
            if row_affected < 1:
                return CustomResponse(data={}, message=f"Employee with id '{emp_id}' not found",
                                      status_code=404)
            else:
                return CustomResponse(data={}, message="Employee is deleted")
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/<string:emp_id>/publications")
class Employees(Resource):
    """
    Focuses on viewing publications from WolfPubDB.
    """

    def get(self, emp_id: str):
        """
        End-point to get the associated publication details for employee
        """
        try:
            output = employees_handler.get(emp_id)
            if len(output) == 0:
                return CustomResponse(data={}, message=f"Employee with id '{emp_id}' not found",
                                  status_code=404)
            publications = None
            if emp_id[0].lower() == 'a':
                output = authors_handler.get(emp_id)
                if len(output) == 0:
                    return CustomResponse(data={}, message=f"Employee with id '{emp_id}' is not an author",
                                          status_code=404)
                author_type = output[0].get('author_type', None)
                publications = employees_handler.get_author_publications(emp_id, author_type)
            elif emp_id[0].lower() == 'e':
                publications = employees_handler.get_editor_publications(emp_id)
            return CustomResponse(data=publications)
        except (QueryGenerationException, MariaDBException) as e:
            return CustomResponse(error=e.__class__.__name__, message=e.__str__(), status_code=400)


@ns.route("/salaries")
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


@ns.route("/salaries/<string:transaction_id>")
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

    @ns.doc(SALARY_PAYMENT_ARGUMENTS, validate=False)
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
