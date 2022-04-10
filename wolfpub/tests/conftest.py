"""
Module with pytest fixtures
"""
import pytest
from pytest_mysql import factories

from wolfpub.constants import DISTRIBUTORS, ACCOUNTS, ORDERS, BOOK_ORDERS_INFO, PERIODICAL_ORDERS_INFO

mysql_in_docker = factories.mysql_noproc()
mock_mysql = factories.mysql('mysql_in_docker')
value_switcher = {
    'int': 1,
    'big': 1231231231,
    'var': 'F',
    'tex': 'asdsf',
    'dec': '12.01',
    'dat': '2022-01-01',
    'boo': 1
}

tables = []


@pytest.fixture
def distributors_table():
    global tables
    if DISTRIBUTORS not in tables:
        tables.append(DISTRIBUTORS)


@pytest.fixture
def accounts_table():
    global tables
    if ACCOUNTS not in tables:
        tables.append(ACCOUNTS)


@pytest.fixture
def orders_table():
    global tables
    if ORDERS not in tables:
        tables.append(ORDERS)


@pytest.fixture
def book_orders_info_table():
    global tables
    if BOOK_ORDERS_INFO not in tables:
        tables.append(BOOK_ORDERS_INFO)


@pytest.fixture
def periodical_orders_info_table():
    global tables
    if PERIODICAL_ORDERS_INFO not in tables:
        tables.append(PERIODICAL_ORDERS_INFO)


@pytest.fixture
def mock_table(mock_mysql):
    """Add mariadb mock"""
    cur = mock_mysql.cursor()
    for table in tables:
        col_list = [f"{k} {v['type']} {v['constraint']}" for k, v in table['columns'].items()]
        create_query = f"CREATE TABLE {table['table_name']} ({', '.join(col_list)})"
        cur.execute(create_query)
        print("\n", create_query)
    mock_mysql.commit()
    cur.close()


@pytest.fixture
def add_record(mock_mysql):
    """Add mariadb mock"""
    cur = mock_mysql.cursor()
    for table in tables:
        insert_col_list = []
        insert_values = []
        for key, value in table['columns'].items():
            if 'auto_increment' not in value['constraint']:
                insert_col_list.append(key)
                insert_values.append(value_switcher[value['type'][:3]])
        insert_query = f"INSERT INTO {table['table_name']} ({', '.join(insert_col_list)}) values " \
                       f"{tuple(insert_values)}"
        cur.execute(insert_query)
    mock_mysql.commit()
    cur.close()
