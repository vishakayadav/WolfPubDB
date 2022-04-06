"""
Module with pytest fixtures
"""
from pytest_mysql import factories
import pytest

mysql_in_docker = factories.mysql_noproc()
mysql = factories.mysql('mysql_in_docker')


@pytest.fixture
def table(mysql):
    """Add mariadb mock"""
    cur = mysql.cursor()
    cur.execute("CREATE TABLE sample (id int primary key auto_increment, name varchar(10), type varchar(10), "
                "address varchar(100), city varchar(20), number int(10))")
    cur.execute("insert into sample (name, type, address, city, number) "
                "values ('ABC', 'Retailer', '2801 Avent Ferry', 'Raleigh', '919513073')")
    mysql.commit()
    cur.close()
