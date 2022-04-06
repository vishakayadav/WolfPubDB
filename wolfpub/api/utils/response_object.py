"""
Response Object: json formatter
"""
import json


class DateTimeEncoder(json.JSONEncoder):
    """
    Serialize datetime object to string
    """

    def default(self, obj):
        try:
            return super(DateTimeEncoder, obj).default(obj)
        except TypeError:
            return str(obj)


def to_json(data):
    """
    To encode the date type values
    """
    return DateTimeEncoder().encode(data)
