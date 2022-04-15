"""
Module for handling distributors
"""

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import DISTRIBUTORS, ACCOUNT_PAYMENTS, SALARY_PAYMENTS, ORDERS, ACCOUNTS, AUTHORS, \
    BOOK_ORDERS_INFO, PERIODICAL_ORDERS_INFO, REPORTS


class ReportHandler(object):
    """
    Focuses on providing functionality over Distributors
    """

    def __init__(self, db):
        self.db = db
        self.query_gen = QueryGenerator()
        self.table_name = REPORTS['table_name']
        self.revenue_table = f"{ACCOUNT_PAYMENTS['table_name']} natural join " \
                             f"{ACCOUNTS['table_name']} natural join " \
                             f"{DISTRIBUTORS['table_name']}"

    # Util date validation
    @staticmethod
    def date_cond(date_col: str, start_date: str, end_date: str):
        cond = {'>=': start_date} if start_date else {}
        cond.update({'<': end_date} if end_date else {})
        return {date_col: cond} if cond else cond

    # insert or update report in the reports table
    def set_monthly_report(self, report, month, year):
        data = {'month': month,
                'year': year}
        select_report = self.db.get_result(self.query_gen.select(self.table_name, ['report_id'], data))
        data.update({'total_revenue': report['total_revenue'],
                     'total_expense': report['total_expense']['salary_expense'] +
                                      report['total_expense']['shipping_cost']})
        if select_report:
            self.db.execute([self.query_gen.update(self.table_name, condition={}, update_data=data)])
        else:
            self.db.execute([self.query_gen.insert(self.table_name, [data])])

    # Get Number of publications and total price of publication for each publication for each distributor
    def get_number_price_per_publication_per_distributor(self, start_date: str, end_date: str):
        cond = self.date_cond('order_date', start_date, end_date)
        group_by = ['account_id', 'publication_id']
        inner_select_query1 = self.query_gen.select(BOOK_ORDERS_INFO['table_name'], ['*'])
        inner_select_query2 = self.query_gen.select(PERIODICAL_ORDERS_INFO['table_name'], ['*'])
        union_query = f"({inner_select_query1} union {inner_select_query2}) as t natural join {ORDERS['table_name']}"
        select_query = self.query_gen.select(union_query,
                                             group_by + ['sum(quantity) total_quantity', 'sum(price) total_price'],
                                             cond, group_by)
        return self.db.get_result(select_query)

    # Fetch count of active distributors
    def get_active_distributor_count(self, cond: dict = None):
        if cond:
            cond.update({'is_active': 1})
        else:
            cond = {'is_active': 1}
        select_query = self.query_gen.select(ACCOUNTS['table_name'], ['count(account_id) as total_distributors'], cond)
        count = self.db.get_result(select_query)
        if not count:
            raise ValueError('No Distributor linked with the Publication House')
        return count[0]

    # Generate revenue
    def get_revenue(self, start_date: str = None, end_date: str = None):
        cond = self.date_cond('payment_date', start_date, end_date)
        select_query = self.query_gen.select(ACCOUNT_PAYMENTS['table_name'], ['sum(amount) as total_revenue'], cond)
        revenue = self.db.get_result(select_query)[0]['total_revenue']
        return float(revenue) if revenue else 0.00

    # Generate revenue for each distributor
    def get_revenue_per_distributor(self, start_date: str = None, end_date: str = None):
        group_by = ['account_id']
        cond = self.date_cond('payment_date', start_date, end_date)
        select_query = self.query_gen.select(self.revenue_table,
                                             ['distributor_id', 'name', 'sum(amount) as revenue'], cond, group_by)
        revenue = self.db.get_result(select_query)
        if not revenue:
            raise ValueError('No revenue collected from Distributors for given parameters')
        return revenue

    # Generate revenue for each city
    def get_revenue_per_city(self, start_date: str = None, end_date: str = None):
        group_by = ['city']
        cond = self.date_cond('payment_date', start_date, end_date)
        select_query = self.query_gen.select(self.revenue_table, ['city', 'sum(amount) as revenue'], cond, group_by)
        revenue = self.db.get_result(select_query)
        if not revenue:
            raise ValueError('No revenue collected from any City for given parameters')
        return revenue

    # Generate revenue for each location
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

    # Generate total expenses
    def _get_expense(self, table, date_col, expense_col, start_date: str, end_date: str):
        cond = self.date_cond(date_col, start_date, end_date)
        select_query = self.query_gen.select(table, [f'sum({expense_col}) as expense'], cond)
        expense = self.db.get_result(select_query)[0]['expense']
        return float(expense) if expense else 0.00

    # Generate shipping cost expense
    def get_shipping_cost_expense(self, start_date: str = None, end_date: str = None):
        table = ORDERS['table_name']
        return {'shipping_cost': self._get_expense(table, 'delivery_date', 'shipping_cost', start_date, end_date)}

    # Generate salary expenses
    def get_salary_expense(self, start_date: str = None, end_date: str = None):
        table = SALARY_PAYMENTS['table_name']
        return {'salary_expense': self._get_expense(table, 'send_date', 'amount', start_date, end_date)}

    # Generate salary expenses per month
    def get_salary_expense_per_month(self):
        table = SALARY_PAYMENTS['table_name']
        columns = ['year(send_date) as year',
                   'month(send_date) as month',
                   'sum(amount) as salary_expense']
        group_by = ['YEAR(send_date)', 'MONTH(send_date)']
        select_query = self.query_gen.select(table, columns, condition={}, group_by=group_by)
        return self.db.get_result(select_query)

    # Generate salary expenses per worktype
    def get_salary_expense_per_worktype(self, start_date: str = None, end_date: str = None):
        table = f"{SALARY_PAYMENTS['table_name']} as s left join {AUTHORS['table_name']} as a on a.emp_id = s.emp_id"
        columns = ["CASE WHEN author_type = 'writer' THEN 'book authorship' "
                   "WHEN author_type = 'journalist' THEN 'article authorship' "
                   "ELSE 'editorial work' END AS work_type",
                   "sum(amount) as salary_expense"]
        cond = self.date_cond('send_date', start_date, end_date)
        group_by = ['work_type']
        select_query = self.query_gen.select(table, columns, condition=cond, group_by=group_by)
        return self.db.get_result(select_query)

    # Generate salary expenses per month per worktype
    def get_salary_expense_per_month_per_worktype(self):
        table = f"{SALARY_PAYMENTS['table_name']} as s left join {AUTHORS['table_name']} as a on a.emp_id = s.emp_id"
        columns = ["year(send_date) as year",
                   "month(send_date) as month",
                   "CASE WHEN author_type = 'writer' THEN 'book authorship' "
                   "WHEN author_type = 'journalist' THEN 'article authorship' "
                   "ELSE 'editorial work' END AS work_type",
                   "sum(amount) as salary_expense"]
        group_by = ['YEAR(send_date)', 'MONTH(send_date)', 'work_type']
        select_query = self.query_gen.select(table, columns, condition={}, group_by=group_by)
        return self.db.get_result(select_query)
