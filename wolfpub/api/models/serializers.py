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
    "distributor_id": fields.String(min_length=1, max_length=6, required=True),
    "name": fields.String(min_length=1, max_length=200, required=True),
    "distributor_type": fields.String(min_length=1, max_length=20, required=True),
    "address": fields.String(min_length=1, max_length=100, required=True),
    "city": fields.String(min_length=1, max_length=20, required=True),
    "phone_number": fields.String(min_length=10, max_length=10, pattern='\\d{10}', required=True),
    "contact_person": fields.String(max_length=100),
    "contact_email": fields.String(max_length=100, required=False,
                                   pattern='^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$'),
    "periodicity": fields.String(max_length=20, default='monthly', required=False),
    "balance": fields.Float(required=False)
})

ACCOUNT_ARGUMENTS = api.model("Account_Model", {
    "contact_email": fields.String(max_length=100, required=True,
                                   pattern='^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$'),
    "periodicity": fields.String(max_length=20, required=True)
})

BOOK_ORDER_ARGUMENTS = api.model("Book_Order_Model", {
    "title": fields.String(min_length=1, max_length=100, required=True),
    "edition": fields.Date(required=True),
    "quantity": fields.Integer(required=False, default=1)
})

PERIODICAL_ORDER_ARGUMENTS = api.model("Periodical_Order_Model", {
    "title": fields.String(min_length=1, max_length=100, required=True),
    "issue": fields.Date(required=True),
    "quantity": fields.Integer(required=False, default=1)
})

ORDER_ARGUMENTS = api.model("Order_Model", {
    "order_id": fields.Integer(required=True),
    "delivery_date": fields.Date(required=True),
    "items": fields.Nested(api.model("Items_Model", {
        "books": fields.List(fields.Nested(BOOK_ORDER_ARGUMENTS), required=True),
        "periodicals": fields.List(fields.Nested(PERIODICAL_ORDER_ARGUMENTS), required=True)
    })),
    "shipping_cost": fields.Float(required=False)
})

PAYMENT_ARGUMENTS = api.model("Payment_Model", {
    "amount": fields.Float(required=True)
})

EMPLOYEE_ARGUMENTS = api.model("Employee_Model", {
    "personnel_id": fields.String(min_length=1, max_length=200, required=True),
    "ssn": fields.String(min_length=1, max_length=12, pattern='\\d{3}-\\d{2}-\\d{4}', required=True),
    "name": fields.String(min_length=1, max_length=200, required=True),
    "gender": fields.String(min_length=1, max_length=1, required=False),
    "age": fields.Integer(required=False, default=1),
    "phone_number": fields.String(min_length=10, max_length=10, pattern='\\d{10}', required=True),
    "job_type": fields.String(min_length=1, max_length=50, required=True),
    "email_id": fields.String(max_length=100, required=False,
                              pattern='^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$'),
    "address": fields.String(min_length=1, max_length=100, required=True)
})

AUTHOR_ARGUMENTS = api.model("Author_Model", {
    "emp_id": fields.String(min_length=1, max_length=6, required=True),
    "type": fields.String(min_length=1, max_length=20, default="staff"),
    "payment_frequency": fields.String(min_length=1, max_length=20, default="monthly"),
    "author_type": fields.String(min_length=1, max_length=20, default="writer")
})

EDITOR_ARGUMENTS = api.model("Editor_Model", {
    "emp_id": fields.String(min_length=1, max_length=6, required=True),
    "type": fields.String(min_length=1, max_length=20, required=True, default="staff")
})

PUBLICATION_ARGUMENTS = api.model("Publication_Model", {
    "publication_id": fields.String(min_length=1, max_length=6, required=False),
    "title": fields.String(min_length=1, max_length=200, required=True),
    "topic": fields.String(min_length=1, max_length=200, required=True),
    "publication_date": fields.Date(required=True),
    "price": fields.Float(required=True)
})

BOOK_ARGUMENTS = api.model("Book_Model", {
    "isbn": fields.String(min_length=1, max_length=20, pattern='\\d{3}-\\d{1}-\\d{2}-\\d{6}-\\d{1}', required=False),
    "creation_date": fields.Date(required=True),
    "is_available": fields.Boolean(default=True)
})

PERIODICAL_ARGUMENTS = api.model("Periodical_Model", {
    "issn": fields.String(min_length=1, max_length=8, pattern='\\d{4}-\\d{4}', required=False),
    "issue": fields.String(min_length=1, max_length=20, required=True),
    "periodical_type": fields.String(min_length=1, max_length=20, required=True),
    "is_available": fields.Boolean(default=True)
})

PUBLICATION_ALL_ARGUMENTS = api.model("Overall_Publication_Model", {
    "title": fields.String(min_length=1, max_length=200, required=True),
    "topic": fields.String(min_length=1, max_length=200, required=True),
    "publication_date": fields.Date(required=True),
    "price": fields.Float(required=True),
    "isbn": fields.String(min_length=1, max_length=20, pattern='\\d{3}-\\d{1}-\\d{2}-\\d{6}-\\d{1}', required=False),
    "creation_date": fields.Date(required=True),
    "issn": fields.String(min_length=1, max_length=8, pattern='\\d{4}-\\d{4}', required=False),
    "issue": fields.String(min_length=1, max_length=20, required=True),
    "periodical_type": fields.String(min_length=1, max_length=20, required=True),
})

CHAPTER_ARGUMENTS = api.model("Chapter_Model", {
    "chapter_title": fields.String(min_length=1, max_length=200, required=True),
    "chapter_text": fields.String(min_length=1, max_length=2000, required=True)
})

ARTICLE_ARGUMENTS = api.model("Article_Model", {
    "creation_date": fields.Date(required=True),
    "topic": fields.String(min_length=1, max_length=200, required=True),
    "title": fields.String(min_length=1, max_length=200, required=True),
    "text": fields.String(min_length=1, max_length=2000, required=True)
})

SALARY_PAYMENT_ARGUMENTS = api.model("Salary_Payment_Model", {
    "emp_id": fields.String(min_length=1, max_length=6, required=True),
    "house_id": fields.String(min_length=1, max_length=6, default=1),
    "amount": fields.Float(required=True),
    "send_date": fields.Date(required=True),
    "received_date": fields.Date(required=False)
})

SALARY_RECEIPT_ARGUMENTS = api.model("Salary_Receipt_Model", {
    "received_date": fields.Date(required=True)
})

BOOK_AUTHOR_ARGUMENTS = api.model("Write_Books_Model", {
    "author": fields.List(fields.String(min_length=1, max_length=6, required=True), required=True),
})

ARTICLE_AUTHOR_ARGUMENTS = api.model("Write_Articles_Model", {
    "author": fields.List(fields.String(min_length=1, max_length=6, required=True), required=True),
})

PUBLICATION_EDITOR_ARGUMENTS = api.model("Review_Publications_Model", {
    "editor": fields.List(fields.String(min_length=1, max_length=6, required=True), required=True),
})

SEARCH_ARGUMENTS = api.model("Filter_Model", {
    "filter": fields.String(min_length=1, max_length=25, required=True),
    "meta": fields.Nested(api.model("filterCriteriaModel", {
            "topic": fields.String(min_length=1, max_length=25, required=False),
            "date_range": fields.Date(required=False),
            "author": fields.String(min_length=1, max_length=25, required=False)
        }), required=True)
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
