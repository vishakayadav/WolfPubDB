"""
API Request Model
"""
from datetime import datetime

from flask_restplus import fields, inputs
from flask_restplus import reqparse

from wolfpub.api.restplus import api


class NoModel(fields.Raw):
    """
    No Model Dictionary.
    """

    def format(self, value):
        return value


SUGGEST_FILTER_ARGUMENTS = api.model("Suggest_Filter_Model", {
    "formula": fields.Nested(api.model("andOperatorModel", {
        "and": fields.List(fields.Nested(api.model("variableInfoModel", {
            "variable": fields.String(required=True),
            "condition": NoModel(required=True)
        }), required=True), required=True)
    }), required=False)
})

DISTRIBUTOR_ARGUMENTS = api.model("Distributor_Model", {
    "name": fields.String(min_length=1, max_length=200, required=True),
    "distributor_type": fields.String(min_length=1, max_length=20, required=True),
    "address": fields.String(min_length=1, max_length=100, required=True),
    "city": fields.String(min_length=1, max_length=10, required=True),
    "phone_number": fields.String(min_length=10, max_length=10, pattern='\\d{10}', required=True),
    "contact_person": fields.String(max_length=100),
    "contact_email": fields.String(max_length=100, required=False,
                                   pattern='^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$'),
    "periodicity": fields.String(max_length=20, required=False)
})

ACCOUNT_ARGUMENTS = api.model("Account_Model", {
    "distributor_id": fields.String(min_length=1, max_length=6, pattern='\\d+', required=True),
    "contact_email": fields.String(max_length=100, required=True,
                                   pattern='^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$'),
    "periodicity": fields.String(max_length=20, required=True)
})

BOOK_ORDER_ARGUMENTS = api.model("Book_Order_Model", {
    "book_id": fields.String(min_length=1, max_length=6, pattern='\\d+', required=True),
    "edition": fields.Date(required=True),
    "quantity": fields.Integer(required=False, default=1)
})

PERIODICAL_ORDER_ARGUMENTS = api.model("Periodical_Order_Model", {
    "periodical_id": fields.String(min_length=1, max_length=6, pattern='\\d+', required=True),
    "issue": fields.Date(required=True),
    "quantity": fields.Integer(required=False, default=1)
})

ORDER_ARGUMENTS = api.model("Order_Model", {
    "account_id": fields.String(min_length=1, max_length=6, pattern='\\d+', required=True),
    "delivery_date": fields.Date(required=True),
    "items": fields.Nested(api.model("Items_Model", {
        "books": fields.List(fields.Nested(BOOK_ORDER_ARGUMENTS), required=True),
        "periodicals": fields.List(fields.Nested(PERIODICAL_ORDER_ARGUMENTS), required=True)
    }))
})

PAYMENT_ARGUMENTS = api.model("Payment_Model", {
    "amount": fields.Float(required=True)
})

CONTENT_WRITER_ARGUMENTS = api.model("Content_Writer_Model", {
    "ssn": fields.String(min_length=1, max_length=12, pattern='\\d{3}-\\d{2}-\\d{4}', required=True),
    "name": fields.String(min_length=1, max_length=200, required=True),
    "gender": fields.String(min_length=1, max_length=1, required=False),
    "age": fields.Integer(required=False, default=1),
    "phone_number": fields.String(min_length=10, max_length=10, pattern='\\d{10}', required=True),
    "job_title": fields.String(min_length=1, max_length=50, required=True)
})

AUTHOR_ARGUMENTS = api.model("Author_Model", {
    "emp_id": fields.String(min_length=1, max_length=6, required=True),
    "type": fields.String(min_length=1, max_length=10, required=True, default="staff")
})

EDITOR_ARGUMENTS = api.model("Editor_Model", {
    "emp_id": fields.String(min_length=1, max_length=6, required=True),
    "type": fields.String(min_length=1, max_length=10, required=True, default="staff")
})

REGISTER_ARGUMENT = reqparse.RequestParser()
REGISTER_ARGUMENT.add_argument('register', type=inputs.boolean, location='args', required=False)

PAGE_SETUP_ARGUMENTS = reqparse.RequestParser()
PAGE_SETUP_ARGUMENTS.add_argument('sort_by', type=str, location='args', required=False)
PAGE_SETUP_ARGUMENTS.add_argument('sort_order', type=str, location='args', required=False)
PAGE_SETUP_ARGUMENTS.add_argument('offset', type=int, location='args', required=False)
PAGE_SETUP_ARGUMENTS.add_argument('page_size', type=int, location='args', required=False)

