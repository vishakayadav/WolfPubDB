"""
Module for Handling the Account of Distributor with 'Wolf Pub' Publication House
"""
from datetime import date

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
        cond = {'account_id': account_id}
        select_query = self.query_gen.select(self.table_name, ['*'], cond)
        dist = self.db.get_result(select_query)
        if not dist:
            raise IndexError(f"Distributor with id '{account_id}' Not Found")
        return dist[0]

    def update(self, account_id: str = '', distributor_id: str = '', update_data: dict = {}):
        if not account_id and not distributor_id:
            raise ValueError("Provide either 'account_id' or 'distributor_id' to update Account")
        cond = {'account_id': account_id} if account_id else {'distributor_id': distributor_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected

    def check_balance(self, account_id: str):
        cond = {'account_id': account_id}
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

    def create_bill(self, account_id: str):
        cond = {'account_id': account_id}
        cur_date = date.today().strftime('%Y-%m-%d')
        select_query_lastest_bill_date = self.query_gen.select(self.table_name, ['max(bill_date) as latest_date'], cond)
        row = self.db.get_result(select_query_lastest_bill_date)
        latest_bill_date = row[0]['latest_date'] if row else '1000-01-01'
        cond_with_order_date = {'account_id': account_id,
                                'order_date': {'>': latest_bill_date},
                                'delivery_date': {'<=': cur_date}}
        select_query_bill_amt = self.query_gen.select(ORDERS['table_name'], ['sum(total_price + shipping_cost) as bill'],
                                                      cond_with_order_date)
        row = self.db.get_result(select_query_bill_amt)
        if not row:
            raise ValueError(f"No new Order has been placed using Account ID '{account_id}' after {latest_bill_date}")
        bill_amount = str(row[0]['bill'])
        data = {'account_id': account_id, 'amount': bill_amount, 'bill_date': cur_date}
        insert_query = self.query_gen.insert(self.table_name, [data])
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

    def update(self, account_id: str = '', distributor_id: str = '', update_data: dict = {}):
        if not account_id and not distributor_id:
            raise ValueError("Provide either 'account_id' or 'distributor_id' to update Account")
        cond = {'account_id': account_id} if account_id else {'distributor_id': distributor_id}
        update_query = self.query_gen.update(self.table_name, cond, update_data)
        row_affected, _ = self.db.execute([update_query])
        return row_affected
