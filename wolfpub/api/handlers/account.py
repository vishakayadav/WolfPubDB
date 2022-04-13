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

    def create_bill(self, account_id: str, periodicity: str = 'monthly'):
        cond = {'account_id': account_id}
        select_query_lastest_bill_date = self.query_gen.select(self.table_name, ['max(bill_date) as latest_date'], cond)
        row = self.db.get_result(select_query_lastest_bill_date)
        print(row)
        latest_bill_date = row[0]['latest_date'] if row else ''
        latest_bill_date = latest_bill_date.strftime('%Y-%m-%d') if latest_bill_date else '2021-07-01'
        intervals = self.get_intervals(latest_bill_date)[periodicity]
        start_date = latest_bill_date
        bills = []
        data = []
        bill_amount = 0.00
        for end_date in intervals:
            end_date = end_date.strftime('%Y-%m-%d')
            cond_with_order_date = {'account_id': account_id,
                                    'order_date': {'>=': start_date, '<': end_date}}
            select_query_bill_amt = self.query_gen.select(ORDERS['table_name'],
                                                          ['sum(total_price + shipping_cost) bill'],
                                                          cond_with_order_date)
            bill = self.db.get_result(select_query_bill_amt)[0]
            start_date = end_date
            if bill['bill']:
                bill['date'] = end_date
                bills.append(bill)

        if not bills:
            raise ValueError(f"No new Order placed using Account ID '{account_id}' "
                             f"for previous months after {latest_bill_date}")

        for bill in bills:
            data.append({'account_id': account_id, 'amount': float(bill['bill']), 'bill_date': str(bill['date'])})
            bill_amount += float(bill['bill'])
        insert_query = self.query_gen.insert(self.table_name, data)
        update_date = {'balance': {'+': bill_amount}}
        update_query = self.query_gen.update(ACCOUNTS['table_name'], cond, update_date)
        _, last_row_id = self.db.execute([insert_query, update_query])
        return {'bill_id': last_row_id[0]}

    def pay_bills(self, account_id: str, amount):
        data = {'account_id': account_id, 'amount': amount, 'payment_date': date.today().strftime('%Y-%m-%d')}
        insert_query = self.query_gen.insert(ACCOUNT_PAYMENTS['table_name'], [data])
        update_data = {'balance': {'-': amount}}
        update_query = self.query_gen.update(ACCOUNTS['table_name'], {'account_id': account_id}, update_data)
        _, last_row_id = self.db.execute([insert_query, update_query])
        return {'payment_id': last_row_id[0]}
