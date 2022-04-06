"""
Query Generator: To create complex queries for AuroraPg
"""

from wolfpub.api.utils.custom_exceptions import QueryGenerationException
from wolfpub.logger import WOLFPUB_LOGGER as logger


class QueryGenerator(object):
    """
    Focuses on providing the functionality to create AuroraPg sub-queries for the arguments provided
    """
    def __init__(self):
        pass

    @staticmethod
    def is_nested(value: dict):
        if any(isinstance(i, dict) or isinstance(i, list) for i in value.values()):
            error_msg = 'Query can not be generated: Value of a column is either list or dict'
            logger.error(error_msg)
            raise QueryGenerationException(error_msg)

    def insert(self, table_name: str, row: dict):
        self.is_nested(row)
        query = f"""insert into {table_name} ({', '.join(row.keys())}) values {tuple(row.values())}"""
        return query

    def select(self, table_name: str, columns: list, condition: dict):
        self.is_nested(condition)
        where_cond = ' and '.join([f"{key}='{value}'" for key, value in condition.items()])
        query = f"""select {', '.join(columns)} from {table_name} where {where_cond}"""
        return query

    def delete(self, table_name: str, condition: dict):
        self.is_nested(condition)
        where_cond = ' and '.join([f"{key}='{value}'" for key, value in condition.items()])
        query = f"""delete from {table_name} where {where_cond}"""
        return query

