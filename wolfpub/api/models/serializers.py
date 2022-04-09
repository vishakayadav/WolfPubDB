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

PUBLICATION_ARGUMENTS = api.model("Publication_Model", {
    "publication_id": fields.String(min_length=1, max_length=6, required=True),
    "title": fields.String(min_length=1, max_length=200, required=True),
    "topic": fields.String(min_length=1, max_length=200, required=True),
    "publication_date": fields.Date(required=True),
    "price": fields.Float(required=True)
})

BOOK_ARGUMENTS = api.model("Book_Model", {
    "publication_id": fields.String(min_length=1, max_length=6, required=True),
    "isbn": fields.String(min_length=1, max_length=13, pattern='\\d{*}-\\d{*}-\\d{*}-\\d{*}', required=True),
    "creation_date": fields.Date(required=True),
    "edition": fields.Integer(required=True, default=1),
    "book_id": fields.String(min_length=1, max_length=6, required=True),
    "is_available": fields.Boolean(default=True)
})

PERIODICAL_ARGUMENTS = api.model("Periodical_Model", {
    "publication_id": fields.String(min_length=1, max_length=6, required=True),
    "issn": fields.String(min_length=1, max_length=8, pattern='\\d{4}-\\d{4}', required=True),
    "issue": fields.Integer(required=True, default=1),
    "periodical_type": fields.String(min_length=1, max_length=10, required=True),
    "periodical_id": fields.String(min_length=1, max_length=6, required=True),
    "is_available": fields.Boolean(default=True)
})

CHAPTER_ARGUMENTS = api.model("Chapter_Model", {
    "publication_id": fields.String(min_length=1, max_length=6, required=True),
    "chapter_id": fields.String(min_length=1, max_length=6, required=True),
    "chapter_title": fields.String(min_length=1, max_length=200, required=True),
    "chapter_text": fields.String(min_length=1, max_length=2000, required=True)
})

ARTICLE_ARGUMENTS = api.model("Article_Model", {
    "publication_id": fields.String(min_length=1, max_length=6, required=True),
    "article_id": fields.String(min_length=1, max_length=6, required=True),
    "creation_date": fields.Date(required=True),
    "topic": fields.String(min_length=1, max_length=200, required=True),
    "title": fields.String(min_length=1, max_length=200, required=True),
    "text": fields.String(min_length=1, max_length=2000, required=True),
    "journalist_name": fields.String(min_length=1, max_length=200, required=True)
})

REGISTER_ARGUMENT = reqparse.RequestParser()
REGISTER_ARGUMENT.add_argument('register', type=inputs.boolean, location='args', required=False)

TIME_PERIOD_REPORT_ARGUMENTS = reqparse.RequestParser()
TIME_PERIOD_REPORT_ARGUMENTS.add_argument('start_date', type=str, location='args', required=False)
TIME_PERIOD_REPORT_ARGUMENTS.add_argument('end_date', type=str, location='args', required=False)

REVENUE_REPORT_ARGUMENTS = reqparse.RequestParser()
REVENUE_REPORT_ARGUMENTS.add_argument('stats', type=str, location='args',
                                      help='distributor_wise, city_wise, location_wise',
                                      required=False)

SALARY_REPORT_ARGUMENTS = reqparse.RequestParser()
SALARY_REPORT_ARGUMENTS.add_argument('stats', type=str, location='args', help='per_month, per_work_type',
                                     required=False)
