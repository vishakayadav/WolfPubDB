"""
Defining constants for all DB tables
"""

DISTRIBUTORS = {
    'table_name': 'distributors',
    'columns': {
        'distributor_id': {'type': 'int(6) unsigned', 'constraint': 'primary key auto_increment'},
        'name': {'type': 'varchar(200)', 'constraint': 'not null'},
        'distributor_type': {'type': 'varchar(20)', 'constraint': ''},
        'address': {'type': 'varchar(100)', 'constraint': 'not null'},
        'city': {'type': 'varchar(20)', 'constraint': 'not null'},
        'phone_number': {'type': 'bigint(10)', 'constraint': ''},
        'contact_person': {'type': 'varchar(100)', 'constraint': ''},
        'is_active': {'type': 'bool', 'constraint': 'default 1'}
    }
}

ACCOUNTS = {
    'table_name': 'accounts',
    'columns': {
        'account_id': {'type': 'int(6) unsigned', 'constraint': 'primary key auto_increment'},
        'distributor_id': {'type': 'int(6) unsigned', 'constraint': ''},
        'house_id': {'type': 'int(1)', 'constraint': 'default 1'},
        'balance': {'type': 'decimal(8, 2)', 'constraint': 'not null'},
        'contact_email': {'type': 'varchar(100)', 'constraint': 'not null'},
        'periodicity': {'type': 'varchar(20)', 'constraint': 'not null'},
        'is_active': {'type': 'bool', 'constraint': 'default 1'}
    }
}

EMPLOYEES = {
    'table_name': 'employees',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'ssn': {'type': 'varchar(12)', 'constraint': 'not null unique'},
        'name': {'type': 'varchar(100)', 'constraint': 'not null'},
        'gender': {'type': 'varchar(1)', 'constraint': ''},
        'age': {'type': 'int(2) unsigned', 'constraint': ''},
        'phone_number': {'type': 'int(10) unsigned', 'constraint': 'not null'},
        'job_title': {'type': 'varchar(20)', 'constraint': 'not null'}
    }
}

EDITORS = {
    'table_name': 'editors',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'type': {'type': 'varchar(20)', 'constraint': 'default \'staff\''}
    }
}

AUTHORS = {
    'table_name': 'authors',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'type': {'type': 'varchar(20)', 'constraint': 'default \'staff\''}
    }
}

MANAGEMENT = {
    'table_name': 'management',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'ssn': {'type': 'varchar(12)', 'constraint': 'not null unique'},
        'name': {'type': 'varchar(100)', 'constraint': 'not null'},
        'gender': {'type': 'varchar(1)', 'constraint': ''},
        'age': {'type': 'int(2) unsigned', 'constraint': ''},
        'phone_number': {'type': 'int(10) unsigned', 'constraint': 'not null'}
    }
}

STAFF_PAYMENTS = {
    'table_name': 'staff_payments',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'payment_freq': {'type': 'varchar(25)', 'constraint': 'not null'}
    }
}

SALARY_PAYMENTS = {
    'table_name': 'salary_payments',
    'columns': {
        'transaction_id': {'type': 'int(8) unsigned', 'constraint': 'primary key auto_increment'},
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'house_id': {'type': 'int(1)', 'constraint': 'default 1'},
        'amount': {'type': 'decimal(8, 2) unsigned', 'constraint': 'not null'},
        'send_date': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'received_date': {'type': 'int(6) unsigned', 'constraint': ''}
    }
}

PUBLICATIONS = {
    'table_name': 'publications',
    'columns': {
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'primary key auto_increment'},
        'title': {'type': 'varchar(100)', 'constraint': 'not null'},
        'topic': {'type': 'varchar(20)', 'constraint': ''},
        'price': {'type': 'decimal(3, 2)', 'constraint': 'not null'},
        'publication_date': {'type': 'date', 'constraint': 'not null'}}
}

BOOKS = {
    'table_name': 'books',
    'columns': {
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'isbn': {'type': 'varchar(17)', 'constraint': 'not null unique'},
        'creation_date': {'type': 'date', 'constraint': 'not null'},
        'edition': {'type': 'int(2)', 'constraint': 'not null'},
        'book_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'is_available': {'type': 'bool', 'constraint': 'default 1'}
    }
}

CHAPTERS = {
    'table_name': 'chapters',
    'columns': {
        'chapter_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'chapter_title': {'type': 'varchar(255)', 'constraint': 'not null'},
        'chapter_text': {'type': 'text', 'constraint': 'not null'}
    }
}

PERIODICALS = {
    'table_name': 'periodicals',
    'columns': {
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'issn': {'type': 'varchar(17)', 'constraint': 'not null unique'},
        'issue': {'type': 'varchar(10)', 'constraint': 'not null'},
        'periodical_type': {'type': 'varchar(20)', 'constraint': 'not null'},
        'periodical_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'is_available': {'type': 'bool', 'constraint': 'default 1'}
    }
}

ARTICLES = {
    'table_name': 'articles',
    'columns': {
        'article_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'creation_date': {'type': 'date', 'constraint': 'not null'},
        'topic': {'type': 'varchar(20)', 'constraint': 'not null'},
        'title': {'type': 'varchar(100)', 'constraint': 'not null'},
        'text': {'type': 'text', 'constraint': 'not null'},
        'journalist_name': {'type': 'varchar(100)', 'constraint': 'not null'}
    }
}

REVIEW_PUBLICATION = {
    'table_name': 'review_publications',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'}
    }
}

WRITE_BOOKS = {
    'table_name': 'write_books',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'}
    }
}

WRITE_ARTICLES = {
    'table_name': 'write_articles',
    'columns': {
        'emp_id': {'type': 'varchar(6)', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'article_id': {'type': 'int(6) unsigned', 'constraint': 'not null'}
    }
}

ORDERS = {
    'table_name': 'orders',
    'columns': {
        'order_id': {'type': 'int(6) unsigned', 'constraint': 'primary key auto_increment'},
        'account_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'order_date': {'type': 'date', 'constraint': 'not null'},
        'shipping_cost': {'type': 'decimal(8, 2) unsigned', 'constraint': 'not null'},
        'delivery_date': {'type': 'date', 'constraint': 'not null'},
        'total_price': {'type': 'decimal(8, 2) unsigned', 'constraint': 'not null'}
    }
}

BOOK_ORDERS_INFO = {
    'table_name': 'book_orders_info',
    'columns': {
        'order_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'quantity': {'type': 'int(4) unsigned', 'constraint': 'default 1'},
        'price': {'type': 'decimal(6, 2) unsigned', 'constraint': 'not null'}
    }
}

PERIODICAL_ORDERS_INFO = {
    'table_name': 'periodical_orders_info',
    'columns': {
        'order_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'publication_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'quantity': {'type': 'int(4) unsigned', 'constraint': 'default 1'},
        'price': {'type': 'decimal(6, 2) unsigned', 'constraint': 'not null'}
    }
}

ACCOUNT_BILLS = {
    'table_name': 'account_bills',
    'columns': {
        'bill_id': {'type': 'int(6) unsigned', 'constraint': 'primary key auto_increment'},
        'account_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'amount': {'type': 'decimal(8, 2)', 'constraint': 'not null'},
        'bill_date': {'type': 'date', 'constraint': 'not null'}
    }
}

ACCOUNT_HOUSES_INFO = {
    'table_name': 'account_houses_info',
    'columns': {
        'account_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'house_id': {'type': 'int(1)', 'constraint': 'default 1'}
    }
}

ACCOUNT_PAYMENTS = {
    'table_name': 'account_payments',
    'columns': {
        'payment_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'account_id': {'type': 'int(6) unsigned', 'constraint': 'not null'},
        'amount': {'type': 'decimal(5, 2)', 'constraint': 'not null'},
        'payment_date': {'type': 'date', 'constraint': 'not null'}
    }
}

REPORTS = {
    'table_name': 'reports',
    'columns': {
        'report_id': {'type': 'int(6) unsigned', 'constraint': 'auto_increment'},
        'month': {'type': 'int(2)', 'constraint': 'not null'},
        'year': {'type': 'int(4)', 'constraint': 'not null'},
        'total_expense': {'type': 'decimal(8, 2)', 'constraint': 'not null'},
        'total_revenue': {'type': 'decimal(8, 2)', 'constraint': 'not null'}
    }
}
