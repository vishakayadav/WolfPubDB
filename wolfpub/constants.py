DISTRIBUTORS = {
    'table_name': 'distributors',
    'columns': [
        'distributor_id',
        'name',
        'distributor_type',
        'address',
        'city',
        'phone_number',
        'contact_person'
    ]
}

ACCOUNTS = {
    'table_name': 'accounts',
    'columns': [
        'account_id',
        'distributor_id',
        'house_id',
        'balance',
        'contact_email',
        'periodicity',
        'is_active'
    ]
}

CONTENT_WRITERS = {
    'table_name': 'content_writers',
    'columns': ['emp_id', 'ssn', 'name', 'gender', 'age', 'phone_number', 'job_title']
}

EDITORS = {
    'table_name': 'editors',
    'columns': ['emp_id', 'type']
}

AUTHORS = {
    'table_name': 'authors',
    'columns': ['emp_id', 'type']
}

MANAGEMENT = {
    'table_name': 'management',
    'columns': ['emp_id', 'ssn', 'name', 'gender', 'age', 'phone_number']
}

STAFF_PAYMENTS = {
    'table_name': 'staff_payments',
    'columns': ['emp_id', 'payment_freq']
}

SALARY_PAYMENTS = {
    'table_name': 'salary_payments',
    'columns': ['transaction_id', 'emp_id', 'house_id', 'amount', 'send_date', 'received_date']
}

PUBLICATIONS = {
    'table_name': 'publications',
    'columns': ['publication_id', 'title', 'topic', 'price', 'publication_date']
}

BOOKS = {
    'table_name': 'books',
    'columns': ['publication_id', 'isbn', 'creation_date', 'edition', 'book_id', 'is_available']
}

CHAPTERS = {
    'table_name': 'chapters',
    'columns': ['chapter_id', 'publication_id', 'chapter_title', 'chapter_text']
}

PERIODICALS = {
    'table_name': 'periodicals',
    'columns': ['publication_id', 'issn', 'issue', 'periodical_type', 'periodical_id', 'is_available']
}

ARTICLES = {
    'table_name': 'articles',
    'columns': ['article_id', 'publication_id', 'creation_date', 'topic', 'title', 'text', 'journalist_name']
}

REVIEW_PUBLICATION = {
    'table_name': 'review_publications',
    'columns': ['emp_id', 'publication_id']
}

WRITE_BOOKS = {
    'table_name': 'write_books',
    'columns': ['emp_id', 'publication_id']
}

ORDERS = {
    'table_name': 'orders',
    'columns': ['order_id', 'account_id', 'order_date', 'shipping_cost', 'delivery_date', 'total_price']
}

BOOK_ORDERS_INFO = {
    'table_name': 'book_orders_info',
    'columns': ['order_id', 'publication_id', 'quantity', 'price']
}

PERIODICAL_ORDERS_INFO = {
    'table_name': 'periodical_orders_info',
    'columns': ['order_id', 'publication_id', 'quantity', 'price']
}

ACCOUNT_BILLS = {
    'table_name': 'account_bills',
    'columns': ['bill_id', 'account_id', 'amount', 'bill_date']
}

ACCOUNT_PAYMENTS = {
    'table_name': 'account_payments',
    'columns': ['payment_id', 'account_id', 'amount', 'payment_date']
}