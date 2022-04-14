"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""
from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from wolfpub.api.utils.query_generator import QueryGenerator
from wolfpub.constants import ORDERS, ACCOUNTS, ACCOUNT_BILLS, ACCOUNT_PAYMENTS


class AccountHandler(object):
    """
    Focuses on providing functionality over account of Distributor with Publication House WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = ACCOUNTS['table_name']
        self.query_gen = QueryGenerator()

    def register(self, account: dict):
        insert_query = self.query_gen.insert(self.table_name, [account])
        _, last_row_id = self.db.execute([insert_query])
        return {'account_id': last_row_id[-1]}

    def get(self, account_id: str):
        cond = {'account_id': account_id, 'is_active': 1}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        account = self.db.get_result(select_query)
        if not account:
            raise IndexError(f"Account with id '{account_id}' Not Registered")
        return account[0]

    def update(self, account_id: str = '', distributor_id: str = '', update_data: dict = {}):
        if not account_id and not distributor_id:
            raise ValueError("Provide either 'account_id' or 'distributor_id' to update Account")
        cond = {'account_id': account_id} if account_id else {'distributor_id': distributor_id}
        cond['is_active'] = '1'
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def check_balance(self, account_id: str = None, distributor_id: str = None):
        cond = {'account_id': account_id} if account_id else {'distributor_id': distributor_id}
        cond['is_active'] = '1'
        select_query = self.query_gen.select(self.table_name, ['balance'], cond)
        balance = self.db.get_result(select_query)
        if not balance:
            raise ValueError('Account not registered with Wolf Publication House')
        return float(balance[0]['balance']) if balance else 0.00


class AccountBillHandler(object):
    """
    Focuses on providing functionality over account's bill of Distributor of WolfPub
    """

    def __init__(self, db):
        self.db = db
        self.table_name = ACCOUNT_BILLS['table_name']
        self.query_gen = QueryGenerator()

    @staticmethod
    def get_intervals(last_bill_date: str):
        bill_date = datetime.strptime(last_bill_date, "%Y-%m-%d").date()
        today = date.today()
        bill_month = bill_date.replace(day=1)
        this_month = today.replace(day=1)
        bill_week = bill_date - relativedelta(days=bill_date.day - bill_date.weekday())  # date.weekday() => Monday is 0
        this_week = today - relativedelta(day=today.day - today.weekday())
        days_diff = (this_week - bill_week).days
        month_diff = ((this_month.year - bill_month.year) * 12) + this_month.month - bill_month.month
        return {'monthly': [bill_date + relativedelta(months=m) for m in range(1, month_diff+1, 1)],
                'quarterly': [bill_date + relativedelta(months=m) for m in range(3, month_diff+1, 3)],
                'biweekly': [bill_date + relativedelta(days=day) for day in range(14, days_diff+1, 14)],
                'weekly': [bill_date + relativedelta(days=day) for day in range(7, days_diff+1, 7)]}

    def get(self, account_id: str, order_id: str, select_cols: list = None):
        if select_cols is None:
            select_cols = ['*']
        select_query = self.query_gen.select(self.table_name, select_cols, {'account_id': account_id,
                                                                            'order_id': order_id})
        account_bill = self.db.get_result(select_query)
        if not account_bill:
            raise IndexError(f"No Billed Order with id '{order_id}' Found")
        return account_bill[0]

    def create_bill(self, account_id: str, order: dict):
        today = date.today().strftime('%Y-%m-%d')
        bill_amount = float(order['total_price']) + float(order['shipping_cost'])
        data = {'account_id': account_id, 'order_id': order['order_id'], 'amount': bill_amount, 'bill_date': today}
        insert_query = self.query_gen.insert(self.table_name, [data])
        update_date = {'balance': {'+': bill_amount}}
        update_query = self.query_gen.update(ACCOUNTS['table_name'], {'account_id': account_id}, update_date)
        _, last_row_id = self.db.execute([insert_query, update_query])
        return {'bill_id': last_row_id[0]}

    def pay_bills(self, account_id: str, amount):
        data = {'account_id': account_id, 'amount': amount, 'payment_date': date.today().strftime('%Y-%m-%d')}
        insert_query = self.query_gen.insert(ACCOUNT_PAYMENTS['table_name'], [data])
        update_data = {'balance': {'-': amount}}
        update_query = self.query_gen.update(ACCOUNTS['table_name'], {'account_id': account_id}, update_data)
        _, last_row_id = self.db.execute([insert_query, update_query])
        return {'payment_id': last_row_id[0]}
