"""
Module with pytest fixtures
"""
import pytest
from pytest_mysql import factories

from wolfpub.tests.test_mariadb_connector import table_dict

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


@pytest.fixture
def mock_table(mock_mysql):
    """Add mariadb mock"""
    cur = mock_mysql.cursor()
    col_list = [f"{k} {v['type']} {v['constraint']}" for k, v in table_dict['columns'].items()]
    create_query = f"CREATE TABLE {table_dict['table_name']} ({', '.join(col_list)})"
    print('\nExecuting:', create_query)
    cur.execute(create_query)
    mock_mysql.commit()
    cur.close()


@pytest.fixture
def add_record(mock_mysql):
    """Add mariadb mock"""
    cur = mock_mysql.cursor()
    insert_col_list = []
    insert_values = []
    for key, value in table_dict['columns'].items():
        if 'auto_increment' not in value['constraint']:
            insert_col_list.append(key)
            insert_values.append(value_switcher[value['type'][:3]])
    insert_query = f"INSERT INTO {table_dict['table_name']} ({', '.join(insert_col_list)}) values " \
                   f"{tuple(insert_values)}"
    cur.execute(insert_query)
    mock_mysql.commit()
    cur.close()
