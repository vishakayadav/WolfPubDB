CREATE TABLE publication_houses (
    house_id INT(1) UNIQUE DEFAULT 1,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    CONSTRAINT publication_house_pk PRIMARY KEY (house_id)
);
INSERT INTO publication_houses (name, location) VALUES ('WolfPub', 'NCSU, Raleigh');

CREATE TABLE distributors (
    distributor_id INT(6) UNSIGNED AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    distributor_type VARCHAR(20) NOT NULL,
    address VARCHAR(100) NOT NULL,
    city VARCHAR(20) NOT NULL,
    phone_number INT(10),
    contact_person VARCHAR(100),
    is_active BOOL DEFAULT 1,
    CONSTRAINT distributor_pk PRIMARY KEY (distributor_id)
);

CREATE TABLE accounts (
    account_id INT(6) UNSIGNED AUTO_INCREMENT,
    distributor_id INT(6) UNSIGNED,
    house_id INT(1) DEFAULT 1,
    balance DECIMAL(8, 2) NOT NULL,
    contact_email VARCHAR(100) NOT NULL,
    periodicity VARCHAR(20)  NOT NULL,
    is_active BOOL DEFAULT 1,
    CONSTRAINT account_pk PRIMARY KEY (account_id),
    CONSTRAINT account_fk1 FOREIGN KEY (distributor_id) REFERENCES distributors(distributor_id),
    CONSTRAINT account_fk2 FOREIGN KEY (house_id) REFERENCES publication_houses(house_id)
);

CREATE TABLE employees (
  emp_id VARCHAR(6) NOT NULL,
  personnel_id VARCHAR(4) NOT NULL,
  ssn VARCHAR(12) NOT NULL UNIQUE,
  name VARCHAR(100) NOT NULL,
  gender VARCHAR(1),
  age INT(2) UNSIGNED,
  phone_number INT(10) UNSIGNED NOT NULL,
  address VARCHAR(100) NOT NULL,
  email_id VARCHAR(100) NOT NULL,
  job_type VARCHAR(20) NOT NULL,
  CONSTRAINT employees_pk PRIMARY KEY (emp_id)
);

CREATE TABLE editors (
  emp_id VARCHAR(6) NOT NULL,
  type VARCHAR(20) DEFAULT 'staff',
  payment_frequency VARCHAR(20) NOT NULL,
  CONSTRAINT editor_pk PRIMARY KEY (emp_id),
  CONSTRAINT editor_fk FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

CREATE TABLE authors (
  emp_id VARCHAR(6) NOT NULL,
  type VARCHAR(20) DEFAULT 'staff',
  payment_frequency VARCHAR(20) NOT NULL,
  author_type VARCHAR(20) DEFAULT 'writer',
  CONSTRAINT author_pk PRIMARY KEY (emp_id),
  CONSTRAINT author_fk FOREIGN KEY (emp_id) REFERENCES employees(emp_id)
);

CREATE TABLE salary_payments (
  transaction_id INT(8) UNSIGNED AUTO_INCREMENT,
  emp_id VARCHAR(6) NOT NULL,
  house_id INT(1) DEFAULT 1,
  amount DECIMAL(8, 2) UNSIGNED NOT NULL,
  send_date DATE NOT NULL,
  received_date DATE,
  CONSTRAINT salary_payment_pk PRIMARY KEY (transaction_id),
  CONSTRAINT salary_payment_fk1 FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
  CONSTRAINT salary_payment_fk2 FOREIGN KEY (house_id) REFERENCES publication_houses(house_id)
);

CREATE TABLE publications (
  publication_id INT(6) UNSIGNED AUTO_INCREMENT,
  title VARCHAR(100) NOT NULL,
  topic VARCHAR(20),
  price DECIMAL(6, 2) NOT NULL,
  publication_date DATE NOT NULL,
  CONSTRAINT publication_pk PRIMARY KEY (publication_id)
);

CREATE TABLE books (
  publication_id INT(6) UNSIGNED NOT NULL,
  isbn VARCHAR(17) NOT NULL UNIQUE,
  creation_date DATE NOT NULL,
  edition INT(2) NOT NULL,
  book_id INT(6) UNSIGNED NOT NULL,
  is_available BOOL DEFAULT 1,
  CONSTRAINT book_pk PRIMARY KEY (publication_id),
  CONSTRAINT book_uk1 UNIQUE (book_id, edition),
  CONSTRAINT book_fk FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE chapters (
  chapter_id INT(6) UNSIGNED NOT NULL AUTO_INCREMENT,
  publication_id INT(6) UNSIGNED NOT NULL,
  chapter_title VARCHAR(255) NOT NULL,
  chapter_text TEXT NOT NULL,
  CONSTRAINT chapter_pk PRIMARY KEY (chapter_id, publication_id),
  CONSTRAINT chapter_fk FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE periodicals (
  publication_id INT(6) UNSIGNED NOT NULL,
  issn VARCHAR(17) NOT NULL UNIQUE,
  issue VARCHAR(10) NOT NULL,
  periodical_type VARCHAR(20) NOT NULL,
  periodical_id INT(6) UNSIGNED NOT NULL,
  is_available BOOL DEFAULT 1,
  CONSTRAINT periodical_pk PRIMARY KEY (publication_id),
  CONSTRAINT periodical_uk1 UNIQUE (periodical_id, issue),
  CONSTRAINT periodical_fk FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE articles (
  article_id INT(6) UNSIGNED NOT NULL,
  publication_id INT(6) UNSIGNED NOT NULL,
  creation_date DATE NOT NULL,
  topic VARCHAR(20) NOT NULL,
  title VARCHAR(100) NOT NULL,
  text TEXT NOT NULL,
  CONSTRAINT article_pk PRIMARY KEY (article_id, publication_id),
  CONSTRAINT article_fk FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE review_publications (
  emp_id VARCHAR(6) NOT NULL,
  publication_id INT(6) UNSIGNED NOT NULL,
  CONSTRAINT reviews_of_publication_pk PRIMARY KEY (emp_id, publication_id),
  CONSTRAINT reviews_of_publication_fk1 FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
  CONSTRAINT reviews_of_publication_fk2 FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE write_books (
  emp_id VARCHAR(6) NOT NULL,
  publication_id INT(6) UNSIGNED NOT NULL,
  CONSTRAINT write_book_pk PRIMARY KEY (emp_id, publication_id),
  CONSTRAINT write_book_fk1 FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
  CONSTRAINT write_book_fk2 FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE write_articles (
  emp_id VARCHAR(6) NOT NULL,
  publication_id INT(6) UNSIGNED NOT NULL,
  article_id INT(6) UNSIGNED NOT NULL,
  CONSTRAINT write_article_pk PRIMARY KEY (emp_id, publication_id, article_id),
  CONSTRAINT write_article_fk1 FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
  CONSTRAINT write_article_fk2 FOREIGN KEY (publication_id) REFERENCES publications(publication_id),
  CONSTRAINT write_article_fk3 FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

CREATE TABLE orders (
    order_id INT(6) UNSIGNED AUTO_INCREMENT,
    account_id INT(6) UNSIGNED NOT NULL,
    order_date DATE NOT NULL,
    shipping_cost DECIMAL(8, 2) UNSIGNED NOT NULL,
    delivery_date DATE NOT NULL,
    total_price DECIMAL(8, 2) UNSIGNED NOT NULL,
    CONSTRAINT order_pk PRIMARY KEY (order_id),
    CONSTRAINT order_fk FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE book_orders_info (
  order_id INT(6) UNSIGNED NOT NULL,
  publication_id INT(6) UNSIGNED NOT NULL,
  quantity INT(4) DEFAULT 1,
  price DECIMAL(6, 2) UNSIGNED NOT NULL,
  CONSTRAINT book_order_pk PRIMARY KEY (order_id, publication_id),
  CONSTRAINT book_order_fk1 FOREIGN KEY (order_id) REFERENCES orders(order_id),
  CONSTRAINT book_order_fk2 FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE periodical_orders_info (
  order_id INT(6) UNSIGNED NOT NULL,
  publication_id INT(6) UNSIGNED NOT NULL,
  quantity INT(4) UNSIGNED DEFAULT 1,
  price DECIMAL(6, 2) UNSIGNED NOT NULL,
  CONSTRAINT periodical_order_pk PRIMARY KEY (order_id, publication_id),
  CONSTRAINT periodical_order_fk1 FOREIGN KEY (order_id) REFERENCES orders(order_id),
  CONSTRAINT periodical_order_fk2 FOREIGN KEY (publication_id) REFERENCES publications(publication_id)
);

CREATE TABLE account_bills (
    bill_id INT(6) UNSIGNED AUTO_INCREMENT,
    account_id INT(6) UNSIGNED NOT NULL,
    order_id INT(6) UNSIGNED NOT NULL,
    amount DECIMAL(8, 2) UNSIGNED NOT NULL,
    bill_date DATE NOT NULL,
    CONSTRAINT account_bill_pk PRIMARY KEY (bill_id),
    CONSTRAINT account_bill_fk1 FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT account_bill_fk2 FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE account_houses_info(
    account_id INT(6) UNSIGNED NOT NULL,
    house_id INT(6) DEFAULT 1,
    CONSTRAINT account_houses_pk PRIMARY KEY (account_id),
    CONSTRAINT account_houses_fk1 FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    CONSTRAINT account_houses_fk2 FOREIGN KEY (house_id) REFERENCES publication_houses(house_id)
);

CREATE TABLE account_payments (
    payment_id INT(8) UNSIGNED NOT NULL AUTO_INCREMENT,
    account_id INT(6) UNSIGNED NOT NULL,
    amount DECIMAL(5, 2) NOT NULL,
    payment_date DATE NOT NULL,
    CONSTRAINT account_payment_pk PRIMARY KEY (payment_id),
    CONSTRAINT account_payment_fk FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE reports (
    report_id INT(6) UNSIGNED AUTO_INCREMENT,
    month INT(2) NOT NULL,
    year INT(4) NOT NULL,
    total_expenses DECIMAL(8,2) NOT NULL,
    total_revenue DECIMAL(8,2) NOT NULL,
    CONSTRAINT report_pk PRIMARY KEY (report_id),
    CONSTRAINT report_uk1 UNIQUE (month, year)
);

-- Create triggers
CREATE TRIGGER inactivate_distributor BEFORE UPDATE ON distributors FOR EACH ROW UPDATE accounts set is_active=new.is_active where distributor_id = old.distributor_id and old.is_active != new.is_active;