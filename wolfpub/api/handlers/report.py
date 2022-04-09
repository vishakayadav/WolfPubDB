"""
Module for Handling Distributors
"""

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import DISTRIBUTORS, ACCOUNT_PAYMENTS, SALARY_PAYMENTS, ORDERS, ACCOUNTS


class ReportHandler(object):
    """
    Focuses on providing functionality over Distributors
    """

    def __init__(self, db):
        self.db = db
        self.query_gen = QueryGenerator()
        self.revenue_table = f"{ACCOUNT_PAYMENTS['table_name']} natural join " \
                             f"{ACCOUNTS['table_name']} natural join " \
                             f"{DISTRIBUTORS['table_name']}"

    @staticmethod
    def date_cond(date_col: str, start_date: str, end_date: str):
        cond = {'>=': start_date} if start_date else {}
        cond.update({'<': end_date} if end_date else {})
        return {date_col: cond} if cond else cond

    def get_active_distributor_count(self, cond=None):
        select_query = self.query_gen.select(ACCOUNTS['table_name'], ['count(account_id) as total_distributors'], cond)
        count = self.db.get_result(select_query)
        if not count:
            raise ValueError('No Distributor linked with the Publication House')
        return count[0]

    def get_revenue(self, start_date: str = None, end_date: str = None):
        cond = self.date_cond('payment_date', start_date, end_date)
        select_query = self.query_gen.select(ACCOUNT_PAYMENTS['table_name'], ['sum(amount) as total_revenue'], cond)
        revenue = self.db.get_result(select_query)[0]['total_revenue']
        return float(revenue) if revenue else 0.00

    def get_revenue_per_distributor(self, start_date: str = None, end_date: str = None):
        group_by = ['account_id']
        cond = self.date_cond('payment_date', start_date, end_date)
        select_query = self.query_gen.select(self.revenue_table,
                                             ['distributor_id', 'name', 'sum(amount) as revenue'], cond, group_by)
        revenue = self.db.get_result(select_query)
        if not revenue:
            raise ValueError('No revenue collected from Distributors for given parameters')
        return revenue

    def get_revenue_per_city(self, start_date: str = None, end_date: str = None):
        group_by = ['city']
        cond = self.date_cond('payment_date', start_date, end_date)
        select_query = self.query_gen.select(self.revenue_table, ['city', 'sum(amount) as revenue'], cond, group_by)
        revenue = self.db.get_result(select_query)
        if not revenue:
            raise ValueError('No revenue collected from any City for given parameters')
        return revenue

    def get_revenue_per_location(self, start_date: str = None, end_date: str = None):
        group_by = ['location', 'city']
        cond = self.date_cond('payment_date', start_date, end_date)
        columns = ['substr(address, instr(address, \' \'), length(address) -1) as location',
                   'city',
                   'sum(amount) as revenue']
        select_query = self.query_gen.select(self.revenue_table, columns, cond, group_by)
        revenue = self.db.get_result(select_query)
        if not revenue:
            raise ValueError('No revenue collected from any Location for given parameters')
        return revenue

    def _get_expense(self, table, date_col, expense_col, start_date: str, end_date: str):
        cond = self.date_cond(date_col, start_date, end_date)
        select_query = self.query_gen.select(table, [f'sum({expense_col}) as expense'], cond)
        expense = self.db.get_result(select_query)[0]['expense']
        return float(expense) if expense else 0.00

    def get_shipping_cost_expense(self, start_date: str = None, end_date: str = None):
        table = ORDERS['table_name']
        return {'shipping_cost': self._get_expense(table, 'delivery_date', 'shipping_cost', start_date, end_date)}

    def get_salary_expense(self, start_date: str = None, end_date: str = None):
        table = SALARY_PAYMENTS['table_name']
        return {'salary_expense': self._get_expense(table, 'send_date', 'amount', start_date, end_date)}

    def get_salary_expense_per_month(self):
        table = SALARY_PAYMENTS['table_name']
        columns = ['year(send_date) as year',
                   'month(send_date) as month',
                   'sum(amount) as salary_expense']
        group_by = ['YEAR(send_date)', 'MONTH(send_date)']
        select_query = self.query_gen.select(table, columns, condition={}, group_by=group_by)
        return self.db.get_result(select_query)

    def get_salary_expense_per_worktype(self, start_date: str = None, end_date: str = None):
        table = SALARY_PAYMENTS['table_name']
        columns = ["CASE WHEN emp_id like 'a%' THEN 'authorship' ELSE 'editorial work' END AS work_type",
                   "sum(amount) as salary_expense"]
        group_by = ['work_type']
        select_query = self.query_gen.select(table, columns, condition={}, group_by=group_by)
        return self.db.get_result(select_query)

    def get_salary_expense_per_month_per_worktype(self):
        table = SALARY_PAYMENTS['table_name']
        columns = ["year(send_date) as year",
                   "month(send_date) as month",
                   "CASE WHEN emp_id like 'a%' THEN 'authorship' ELSE 'editorial work' END AS work_type",
                   "sum(amount) as salary_expense"]
        group_by = ['YEAR(send_date)', 'MONTH(send_date)', 'work_type']
        select_query = self.query_gen.select(table, columns, condition={}, group_by=group_by)
        return self.db.get_result(select_query)
