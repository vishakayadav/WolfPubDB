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
        self.where_operators = ['>', '<', '>=', '<=', 'like', 'ilike']
        self.set_operators = ['+', '-', '/', '*']

    @staticmethod
    def is_list(value: dict):
        if any(isinstance(i, list) for i in value.values()):
            error_msg = 'Value of a column can not be list'
            logger.error(error_msg)
            raise QueryGenerationException(error_msg)

    @staticmethod
    def is_dict(value: dict):
        if any(isinstance(i, dict) for i in value.values()):
            error_msg = 'Value of a column can not be dict'
            logger.error(error_msg)
            raise QueryGenerationException(error_msg)

    def handling_where_operator(self, key: str, value: dict):
        clause = []
        for operator in self.where_operators:
            if operator in value:
                clause.append(f"{key} {operator} '{value[operator]}'")
        return ' and '.join(clause)

    def handling_set_operator(self, key: str, value: dict):
        clause = []
        for operator in self.set_operators:
            if operator in value:
                clause.append(f"{key} = {key} {operator} '{value[operator]}'")
        return ', '.join(clause)

    def get_where_cond(self, cond: dict):
        where_cond = []
        for key, value in cond.items():
            if not value:
                where_cond.append(f'{key} IS NULL')
            elif isinstance(value, list):
                if value and (isinstance(value[0], str) or isinstance(value[0], int) or isinstance(value[0], float)):
                    where_cond.append(f'{key} IN {tuple(value)}')
                else:
                    where_cond.append(f"(({') or ('.join([self.get_where_cond(v) for v in value])}))")
            elif isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                where_cond.append(f"{key}='{value}'")
            elif isinstance(value, dict):
                if any(k in self.where_operators for k in value):
                    where_cond.append(self.handling_where_operator(key, value))
                else:
                    where_cond.append(self.get_where_cond(value))
            else:
                error_msg = 'Value for a column not in correct format, expected format: list or string'
                logger.error(error_msg)
                raise QueryGenerationException(error_msg)
        return ' and '.join(where_cond)

    def insert(self, table_name: str, rows: list[dict]):
        self.is_list(rows[0])
        self.is_dict(rows[0])
        query = f"insert into {table_name} ({', '.join(rows[0].keys())}) values " \
                f"{', '.join([f'{tuple(row.values())}' for row in rows])}"
        return query

    def select(self, table_name: str, columns: list, condition: dict = None, group_by: list = None):
        query = f"""select {', '.join(columns)} from {table_name}"""
        if condition:
            where_cond = self.get_where_cond(condition)
            query += f" where {where_cond}"
        if group_by:
            query += f" group by {', '.join(group_by)}"
        return query

    def update(self, table_name: str, condition: dict, update_data: dict):
        self.is_list(update_data)
        where_cond = self.get_where_cond(condition)
        set_values = []
        for key, value in update_data.items():
            if isinstance(value, dict) and any(k in self.set_operators for k in value):
                set_values.append(self.handling_set_operator(key, value))
            elif isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                set_values.append(f"{key}='{value}'")
            else:
                error_msg = 'Update Query Generator does not support list or dictionary values'
                logger.error(error_msg)
                raise QueryGenerationException(error_msg)
        query = f"""update {table_name} set {', '.join(set_values)} where {where_cond}"""
        return query

    def delete(self, table_name: str, condition: dict):
        where_cond = self.get_where_cond(condition)
        query = f"""delete from {table_name} where {where_cond}"""
        return query

