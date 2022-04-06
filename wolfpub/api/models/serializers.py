"""
API Request Model
"""

from flask_restplus import fields
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
    "contact_email": fields.String(max_length=100, required=True,
                                   pattern='^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$'),
    "periodicity": fields.String(max_length=20, required=True),
})

ENTITY_ARGUMENT = reqparse.RequestParser()
ENTITY_ARGUMENT.add_argument('entity', type=str, location='args', required=True)

PAGE_SETUP_ARGUMENTS = reqparse.RequestParser()
PAGE_SETUP_ARGUMENTS.add_argument('sort_by', type=str, location='args', required=False)
PAGE_SETUP_ARGUMENTS.add_argument('sort_order', type=str, location='args', required=False)
PAGE_SETUP_ARGUMENTS.add_argument('offset', type=int, location='args', required=False)
PAGE_SETUP_ARGUMENTS.add_argument('page_size', type=int, location='args', required=False)

SEARCH_ARGUMENTS = reqparse.RequestParser()
SEARCH_ARGUMENTS.add_argument('query', type=str, location='args', required=False)
SEARCH_ARGUMENTS.add_argument('input', type=str, location='args', required=False)

EXECUTION_ARGUMENT = reqparse.RequestParser()
EXECUTION_ARGUMENT.add_argument('execId', type=str, location='args', required=False)
