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

JOB_CONFIGURATION_ARGUMENTS = api.model("Job_Configuration_Model", {
    "user_id": fields.String(required=True),
    "group_by_keys": fields.List(fields.String(), required=True),
    "schedule": fields.Nested(api.model("andOperatorModel", {}))
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
