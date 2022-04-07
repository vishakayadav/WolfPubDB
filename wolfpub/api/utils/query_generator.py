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
            error_msg = 'Value of a column can not be list or dict'
            logger.error(error_msg)
            raise QueryGenerationException(error_msg)

    def get_where_cond(self, cond: dict):
        where_cond = []
        for key, value in cond.items():
            if isinstance(value, list):
                if isinstance(value[0], str) or isinstance(value[0], int) or isinstance(value[0], float):
                    where_cond.append(f'{key} IN {tuple(value)}')
                else:
                    where_cond.append(f"(({') or ('.join([self.get_where_cond(v) for v in value])}))")
            elif isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                where_cond.append(f"{key}='{value}'")
            elif isinstance(value, dict):
                where_cond.append(self.get_where_cond(value))
            elif not value:
                where_cond.append(f'{key} IS NULL')
            else:
                error_msg = 'Value for a column not in correct format, expected format: list or string'
                logger.error(error_msg)
                raise QueryGenerationException(error_msg)
        return ' and '.join(where_cond)

    def insert(self, table_name: str, rows: list[dict]):
        self.is_nested(rows[0])
        query = f"insert into {table_name} ({', '.join(rows[0].keys())}) values " \
                f"{', '.join([f'{tuple(row.values())}' for row in rows])}"
        return query

    def select(self, table_name: str, columns: list, condition: dict):
        where_cond = self.get_where_cond(condition)
        query = f"""select {', '.join(columns)} from {table_name} where {where_cond}"""
        return query

    def update(self, table_name: str, condition: dict, update_data: dict):
        self.is_nested(update_data)
        where_cond = self.get_where_cond(condition)
        set_values = ', '.join([f"{key}='{value}'" for key, value in update_data.items()])
        query = f"""update {table_name} set {set_values} where {where_cond}"""
        return query

    def delete(self, table_name: str, condition: dict):
        self.is_nested(condition)
        where_cond = ' and '.join([f"{key}='{value}'" for key, value in condition.items()])
        query = f"""delete from {table_name} where {where_cond}"""
        return query

