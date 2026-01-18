# SQL - Complete Guide

SQL (Structured Query Language) is the standard language for managing and manipulating relational databases. It enables you to create, read, update, and delete data, as well as manage database structures.

---

## Core Concepts

### Database
A **database** is an organized collection of structured data stored electronically. It consists of tables that store related information.

---

### Table
A **table** is a collection of related data organized in rows and columns.

**Example:**
```
users table:
| id | username | email              | created_at |
|----|----------|--------------------|------------|
| 1  | alice    | alice@example.com  | 2024-01-15 |
| 2  | bob      | bob@example.com    | 2024-01-20 |
```

---

### Row (Record/Tuple)
A **row** represents a single record in a table.

---

### Column (Field/Attribute)
A **column** represents a specific attribute of data in a table.

---

### Primary Key
A **primary key** uniquely identifies each row in a table. It cannot be NULL and must be unique.

---

### Foreign Key
A **foreign key** is a column that creates a relationship between two tables by referencing the primary key of another table.

---

### Index
An **index** improves query performance by creating a data structure that allows faster data retrieval.

---

## Data Types

### Numeric Types

```sql
-- Integer types
TINYINT       -- -128 to 127
SMALLINT      -- -32,768 to 32,767
MEDIUMINT     -- -8,388,608 to 8,388,607
INT / INTEGER -- -2,147,483,648 to 2,147,483,647
BIGINT        -- Very large integers

-- Decimal types
DECIMAL(p, s) -- Fixed-point (p=precision, s=scale)
NUMERIC(p, s) -- Same as DECIMAL
FLOAT         -- Floating-point (approximate)
DOUBLE        -- Double precision floating-point
REAL          -- Alias for FLOAT or DOUBLE
```

**Examples:**
```sql
price DECIMAL(10, 2)  -- Max 10 digits, 2 after decimal: 12345678.90
quantity INT
rating FLOAT
```

---

### String Types

```sql
-- Fixed length
CHAR(n)       -- Fixed-length string (max n characters)

-- Variable length
VARCHAR(n)    -- Variable-length string (max n characters)
TEXT          -- Large text data
TINYTEXT      -- Small text (255 characters)
MEDIUMTEXT    -- Medium text (16 MB)
LONGTEXT      -- Large text (4 GB)

-- Binary
BINARY(n)     -- Fixed-length binary data
VARBINARY(n)  -- Variable-length binary data
BLOB          -- Binary Large Object
```

**Examples:**
```sql
username VARCHAR(50)
bio TEXT
country_code CHAR(2)  -- 'US', 'GB', etc.
```

---

### Date and Time Types

```sql
DATE          -- Date only (YYYY-MM-DD)
TIME          -- Time only (HH:MM:SS)
DATETIME      -- Date and time (YYYY-MM-DD HH:MM:SS)
TIMESTAMP     -- Date and time with timezone
YEAR          -- Year only (YYYY)
```

**Examples:**
```sql
birth_date DATE
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_at DATETIME
```

---

### Boolean Type

```sql
BOOLEAN       -- TRUE (1) or FALSE (0)
BOOL          -- Alias for BOOLEAN
```

**Example:**
```sql
is_active BOOLEAN DEFAULT TRUE
```

---

### Other Types

```sql
ENUM('val1', 'val2', ...)  -- Predefined list of values
SET('val1', 'val2', ...)   -- Set of predefined values
JSON                        -- JSON data (PostgreSQL, MySQL 5.7+)
UUID                        -- Universally Unique Identifier (PostgreSQL)
```

---

## SELECT - Querying Data

### Basic SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT username, email FROM users;

-- Select with alias
SELECT username AS user_name, email AS user_email
FROM users;

-- Select distinct values
SELECT DISTINCT country FROM users;

-- Select with limit
SELECT * FROM users LIMIT 10;

-- Select with offset (pagination)
SELECT * FROM users LIMIT 10 OFFSET 20;
```

---

### WHERE - Filtering Rows

```sql
-- Comparison operators: =, !=, <, >, <=, >=
SELECT * FROM products WHERE price > 100;
SELECT * FROM users WHERE age >= 18;
SELECT * FROM orders WHERE status = 'pending';
SELECT * FROM items WHERE stock != 0;

-- BETWEEN
SELECT * FROM products WHERE price BETWEEN 50 AND 100;

-- IN
SELECT * FROM users WHERE country IN ('USA', 'Canada', 'Mexico');

-- NOT IN
SELECT * FROM users WHERE status NOT IN ('banned', 'deleted');

-- LIKE (pattern matching)
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM products WHERE name LIKE 'iPhone%';
SELECT * FROM users WHERE username LIKE '_oh_';  -- _ matches single char

-- IS NULL / IS NOT NULL
SELECT * FROM users WHERE phone IS NULL;
SELECT * FROM orders WHERE shipped_at IS NOT NULL;

-- Logical operators: AND, OR, NOT
SELECT * FROM products 
WHERE price > 50 AND category = 'electronics';

SELECT * FROM users 
WHERE country = 'USA' OR country = 'Canada';

SELECT * FROM products 
WHERE NOT (price < 10 OR stock = 0);
```

---

### ORDER BY - Sorting Results

```sql
-- Ascending order (default)
SELECT * FROM users ORDER BY username ASC;
SELECT * FROM products ORDER BY price;  -- ASC is implicit

-- Descending order
SELECT * FROM products ORDER BY price DESC;

-- Multiple columns
SELECT * FROM users 
ORDER BY country ASC, created_at DESC;

-- Order by expression
SELECT * FROM products 
ORDER BY (price * 0.9) DESC;

-- Order by column position
SELECT username, email FROM users ORDER BY 1;  -- Order by first column
```

---

### LIMIT and OFFSET - Pagination

```sql
-- First 10 rows
SELECT * FROM users LIMIT 10;

-- Rows 11-20 (skip first 10)
SELECT * FROM users LIMIT 10 OFFSET 10;

-- Alternative syntax
SELECT * FROM users OFFSET 10 ROWS FETCH NEXT 10 ROWS ONLY;

-- Pagination example: Page 3, 20 items per page
SELECT * FROM products
LIMIT 20 OFFSET 40;  -- Skip 2 pages (40 items)
```

---

## Aggregate Functions

### COUNT

```sql
-- Count all rows
SELECT COUNT(*) FROM users;

-- Count non-NULL values
SELECT COUNT(phone) FROM users;

-- Count distinct values
SELECT COUNT(DISTINCT country) FROM users;

-- Count with condition
SELECT COUNT(*) FROM orders WHERE status = 'completed';
```

---

### SUM, AVG, MIN, MAX

```sql
-- Sum
SELECT SUM(amount) FROM orders;
SELECT SUM(price * quantity) AS total_revenue FROM order_items;

-- Average
SELECT AVG(price) FROM products;
SELECT AVG(rating) AS avg_rating FROM reviews;

-- Minimum
SELECT MIN(price) FROM products;
SELECT MIN(created_at) AS first_order FROM orders;

-- Maximum
SELECT MAX(price) FROM products;
SELECT MAX(salary) AS highest_salary FROM employees;

-- Multiple aggregates
SELECT 
    COUNT(*) AS total_orders,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_order_value,
    MIN(amount) AS min_order,
    MAX(amount) AS max_order
FROM orders;
```

---

### GROUP BY - Grouping Data

```sql
-- Count users by country
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country;

-- Total sales by product
SELECT product_id, SUM(quantity) AS total_sold
FROM order_items
GROUP BY product_id;

-- Average price by category
SELECT category, AVG(price) AS avg_price
FROM products
GROUP BY category;

-- Multiple columns in GROUP BY
SELECT country, city, COUNT(*) AS user_count
FROM users
GROUP BY country, city;

-- Group by expression
SELECT 
    YEAR(created_at) AS year,
    MONTH(created_at) AS month,
    COUNT(*) AS order_count
FROM orders
GROUP BY YEAR(created_at), MONTH(created_at);
```

---

### HAVING - Filtering Groups

```sql
-- Countries with more than 100 users
SELECT country, COUNT(*) AS user_count
FROM users
GROUP BY country
HAVING COUNT(*) > 100;

-- Categories with average price over $50
SELECT category, AVG(price) AS avg_price
FROM products
GROUP BY category
HAVING AVG(price) > 50;

-- Products sold more than 10 times
SELECT product_id, SUM(quantity) AS total_sold
FROM order_items
GROUP BY product_id
HAVING SUM(quantity) > 10;

-- WHERE vs HAVING
SELECT category, AVG(price) AS avg_price
FROM products
WHERE stock > 0  -- Filter before grouping
GROUP BY category
HAVING AVG(price) > 50  -- Filter after grouping
ORDER BY avg_price DESC;
```

---

## JOIN - Combining Tables

### INNER JOIN

Returns rows that have matching values in both tables.

```sql
-- Basic INNER JOIN
SELECT users.username, orders.order_date, orders.amount
FROM users
INNER JOIN orders ON users.id = orders.user_id;

-- Table aliases
SELECT u.username, o.order_date, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- Multiple joins
SELECT 
    u.username,
    o.order_date,
    p.product_name,
    oi.quantity,
    oi.price
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id;

-- Join with WHERE
SELECT u.username, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.status = 'completed';
```

---

### LEFT JOIN (LEFT OUTER JOIN)

Returns all rows from left table, and matched rows from right table. NULL for non-matches.

```sql
-- All users and their orders (including users with no orders)
SELECT u.username, o.order_date, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- Find users with no orders
SELECT u.username
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;

-- Count orders per user (including 0)
SELECT u.username, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username;
```

---

### RIGHT JOIN (RIGHT OUTER JOIN)

Returns all rows from right table, and matched rows from left table. NULL for non-matches.

```sql
-- All orders and user info (including orphaned orders)
SELECT u.username, o.order_date, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- Find orders without users
SELECT o.id, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id
WHERE u.id IS NULL;
```

---

### FULL OUTER JOIN

Returns all rows when there's a match in either table.

```sql
-- All users and orders (matched and unmatched)
SELECT u.username, o.order_date, o.amount
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- Note: MySQL doesn't support FULL OUTER JOIN directly
-- Workaround using UNION:
SELECT u.username, o.order_date, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
UNION
SELECT u.username, o.order_date, o.amount
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;
```

---

### CROSS JOIN

Returns Cartesian product (all possible combinations).

```sql
-- Every combination of colors and sizes
SELECT c.color, s.size
FROM colors c
CROSS JOIN sizes s;

-- Alternative syntax
SELECT c.color, s.size
FROM colors c, sizes s;
```

---

### SELF JOIN

Join table to itself.

```sql
-- Find employees and their managers
SELECT 
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find users in same city
SELECT 
    u1.username AS user1,
    u2.username AS user2,
    u1.city
FROM users u1
INNER JOIN users u2 ON u1.city = u2.city AND u1.id < u2.id;
```

---

## Subqueries

### Subquery in WHERE

```sql
-- Users who placed orders
SELECT username FROM users
WHERE id IN (SELECT user_id FROM orders);

-- Users who haven't placed orders
SELECT username FROM users
WHERE id NOT IN (SELECT user_id FROM orders WHERE user_id IS NOT NULL);

-- Products more expensive than average
SELECT name, price FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Users from countries with more than 100 users
SELECT * FROM users
WHERE country IN (
    SELECT country FROM users
    GROUP BY country
    HAVING COUNT(*) > 100
);
```

---

### Subquery in SELECT

```sql
-- Count orders for each user
SELECT 
    username,
    email,
    (SELECT COUNT(*) FROM orders WHERE user_id = users.id) AS order_count
FROM users;

-- Show product with category name
SELECT 
    name,
    price,
    (SELECT category_name FROM categories WHERE id = products.category_id) AS category
FROM products;
```

---

### Subquery in FROM

```sql
-- Average of category averages
SELECT AVG(avg_price) AS overall_avg
FROM (
    SELECT category, AVG(price) AS avg_price
    FROM products
    GROUP BY category
) AS category_averages;

-- Top 5 users by order count
SELECT username, order_count
FROM (
    SELECT 
        u.username,
        COUNT(o.id) AS order_count
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    GROUP BY u.id, u.username
) AS user_orders
ORDER BY order_count DESC
LIMIT 5;
```

---

### Correlated Subquery

```sql
-- Products more expensive than average in their category
SELECT name, price, category
FROM products p1
WHERE price > (
    SELECT AVG(price)
    FROM products p2
    WHERE p2.category = p1.category
);

-- Employees earning more than average in their department
SELECT name, salary, department_id
FROM employees e1
WHERE salary > (
    SELECT AVG(salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id
);
```

---

### EXISTS and NOT EXISTS

```sql
-- Users who have placed orders (using EXISTS)
SELECT username FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Users with no orders
SELECT username FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- Products never ordered
SELECT name FROM products p
WHERE NOT EXISTS (
    SELECT 1 FROM order_items oi WHERE oi.product_id = p.id
);
```

---

## INSERT - Adding Data

### Basic INSERT

```sql
-- Insert single row
INSERT INTO users (username, email, created_at)
VALUES ('alice', 'alice@example.com', NOW());

-- Insert multiple rows
INSERT INTO users (username, email)
VALUES 
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com'),
    ('david', 'david@example.com');

-- Insert all columns (match table order)
INSERT INTO products
VALUES (NULL, 'Laptop', 'Electronics', 999.99, 50);

-- Insert with auto-increment primary key
INSERT INTO users (username, email)
VALUES ('eve', 'eve@example.com');
-- id is auto-generated
```

---

### INSERT with SELECT

```sql
-- Copy data from one table to another
INSERT INTO archive_orders (id, user_id, amount, order_date)
SELECT id, user_id, amount, order_date
FROM orders
WHERE order_date < '2023-01-01';

-- Insert aggregated data
INSERT INTO monthly_sales (month, total_sales)
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') AS month,
    SUM(amount) AS total_sales
FROM orders
GROUP BY DATE_FORMAT(order_date, '%Y-%m');
```

---

### INSERT ... ON DUPLICATE KEY UPDATE (MySQL)

```sql
-- Insert or update if unique key exists
INSERT INTO user_stats (user_id, login_count, last_login)
VALUES (1, 1, NOW())
ON DUPLICATE KEY UPDATE 
    login_count = login_count + 1,
    last_login = NOW();
```

---

### INSERT ... RETURNING (PostgreSQL)

```sql
-- Insert and return generated values
INSERT INTO users (username, email)
VALUES ('frank', 'frank@example.com')
RETURNING id, created_at;
```

---

## UPDATE - Modifying Data

### Basic UPDATE

```sql
-- Update single column
UPDATE users
SET last_login = NOW()
WHERE id = 1;

-- Update multiple columns
UPDATE users
SET 
    email = 'newemail@example.com',
    updated_at = NOW()
WHERE username = 'alice';

-- Update all rows (careful!)
UPDATE products
SET discount = 0.1;

-- Update with calculation
UPDATE products
SET price = price * 1.1
WHERE category = 'Electronics';
```

---

### UPDATE with JOIN

```sql
-- Update based on another table (MySQL)
UPDATE orders o
INNER JOIN users u ON o.user_id = u.id
SET o.status = 'premium_processed'
WHERE u.membership = 'premium' AND o.status = 'pending';

-- PostgreSQL syntax
UPDATE orders
SET status = 'premium_processed'
FROM users
WHERE orders.user_id = users.id
    AND users.membership = 'premium'
    AND orders.status = 'pending';
```

---

### UPDATE with CASE

```sql
-- Conditional update
UPDATE employees
SET salary = CASE
    WHEN department = 'Engineering' THEN salary * 1.15
    WHEN department = 'Sales' THEN salary * 1.10
    WHEN department = 'Support' THEN salary * 1.05
    ELSE salary
END;

-- Update based on complex conditions
UPDATE products
SET status = CASE
    WHEN stock = 0 THEN 'out_of_stock'
    WHEN stock < 10 THEN 'low_stock'
    WHEN stock >= 10 THEN 'in_stock'
END;
```

---

### UPDATE with Subquery

```sql
-- Update using subquery value
UPDATE products
SET price = (SELECT AVG(price) FROM products WHERE category = 'Electronics')
WHERE category = 'Electronics' AND price IS NULL;

-- Update based on subquery condition
UPDATE users
SET status = 'active'
WHERE id IN (
    SELECT user_id FROM orders
    WHERE order_date > DATE_SUB(NOW(), INTERVAL 30 DAY)
);
```

---

## DELETE - Removing Data

### Basic DELETE

```sql
-- Delete specific rows
DELETE FROM users
WHERE id = 5;

-- Delete with condition
DELETE FROM orders
WHERE status = 'cancelled' AND order_date < '2023-01-01';

-- Delete all rows (dangerous!)
DELETE FROM temp_data;
```

---

### DELETE with JOIN

```sql
-- Delete based on another table (MySQL)
DELETE o
FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE u.status = 'deleted';

-- PostgreSQL syntax
DELETE FROM orders
USING users
WHERE orders.user_id = users.id AND users.status = 'deleted';
```

---

### DELETE with Subquery

```sql
-- Delete orphaned records
DELETE FROM order_items
WHERE order_id NOT IN (SELECT id FROM orders);

-- Delete old inactive users
DELETE FROM users
WHERE id NOT IN (
    SELECT user_id FROM orders
    WHERE order_date > DATE_SUB(NOW(), INTERVAL 1 YEAR)
) AND created_at < DATE_SUB(NOW(), INTERVAL 2 YEAR);
```

---

### TRUNCATE vs DELETE

```sql
-- DELETE: Slower, can rollback, fires triggers
DELETE FROM logs;

-- TRUNCATE: Faster, resets auto-increment, cannot rollback
TRUNCATE TABLE logs;

-- TRUNCATE with cascade (drop all dependent data)
TRUNCATE TABLE users CASCADE;
```

---

## CREATE - Database Objects

### CREATE DATABASE

```sql
-- Create database
CREATE DATABASE my_app;

-- Create with specific charset
CREATE DATABASE my_app
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create if not exists
CREATE DATABASE IF NOT EXISTS my_app;
```

---

### CREATE TABLE

```sql
-- Basic table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table with foreign key
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('pending', 'processing', 'completed', 'cancelled') DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table with composite primary key
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Table with check constraint
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    CHECK (price > 0),
    CHECK (stock >= 0)
);

-- Create table from query
CREATE TABLE archived_orders AS
SELECT * FROM orders
WHERE order_date < '2023-01-01';
```

---

### CREATE INDEX

```sql
-- Simple index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Composite index
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_users ON users(email)
WHERE status = 'active';

-- Full-text index (MySQL)
CREATE FULLTEXT INDEX idx_products_description ON products(description);
```

---

### CREATE VIEW

```sql
-- Create view
CREATE VIEW active_users AS
SELECT id, username, email, created_at
FROM users
WHERE status = 'active';

-- Use view
SELECT * FROM active_users;

-- Create or replace view
CREATE OR REPLACE VIEW user_order_summary AS
SELECT 
    u.id,
    u.username,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.amount), 0) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.username;

-- Materialized view (PostgreSQL)
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    DATE(order_date) AS date,
    SUM(amount) AS daily_total
FROM orders
GROUP BY DATE(order_date);

-- Refresh materialized view
REFRESH MATERIALIZED VIEW sales_summary;
```

---

## ALTER - Modifying Objects

### ALTER TABLE

```sql
-- Add column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Add column with constraints
ALTER TABLE users 
ADD COLUMN date_of_birth DATE NOT NULL DEFAULT '1900-01-01';

-- Add multiple columns
ALTER TABLE users
ADD COLUMN city VARCHAR(50),
ADD COLUMN country VARCHAR(50);

-- Drop column
ALTER TABLE users DROP COLUMN phone;

-- Modify column type
ALTER TABLE users MODIFY COLUMN email VARCHAR(150);

-- Rename column
ALTER TABLE users RENAME COLUMN username TO user_name;

-- Change column (rename and modify)
ALTER TABLE users CHANGE COLUMN user_name username VARCHAR(60);

-- Add constraint
ALTER TABLE users ADD CONSTRAINT email_unique UNIQUE (email);

-- Add foreign key
ALTER TABLE orders 
ADD CONSTRAINT fk_user
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Drop constraint
ALTER TABLE users DROP CONSTRAINT email_unique;
ALTER TABLE users DROP INDEX email_unique;  -- MySQL

-- Drop foreign key
ALTER TABLE orders DROP FOREIGN KEY fk_user;

-- Rename table
ALTER TABLE users RENAME TO app_users;
RENAME TABLE users TO app_users;  -- MySQL
```

---

## DROP - Removing Objects

```sql
-- Drop table
DROP TABLE temp_data;

-- Drop if exists
DROP TABLE IF EXISTS deprecated_table;

-- Drop multiple tables
DROP TABLE table1, table2, table3;

-- Drop database
DROP DATABASE old_database;
DROP DATABASE IF EXISTS test_db;

-- Drop view
DROP VIEW active_users;

-- Drop index
DROP INDEX idx_users_email ON users;  -- MySQL
DROP INDEX idx_users_email;            -- PostgreSQL
```

---

## Constraints

### Primary Key

```sql
-- Define at column level
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50)
);

-- Define at table level
CREATE TABLE users (
    id INT AUTO_INCREMENT,
    username VARCHAR(50),
    PRIMARY KEY (id)
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id)
);

-- Add primary key to existing table
ALTER TABLE users ADD PRIMARY KEY (id);
```

---

### Foreign Key

```sql
-- Define foreign key
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Foreign key with actions
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Actions:
-- CASCADE: Delete/update related rows
-- SET NULL: Set foreign key to NULL
-- SET DEFAULT: Set foreign key to default value
-- RESTRICT: Prevent delete/update
-- NO ACTION: Same as RESTRICT

-- Named foreign key
ALTER TABLE orders
ADD CONSTRAINT fk_orders_users
FOREIGN KEY (user_id) REFERENCES users(id)
ON DELETE CASCADE;
```

---

### UNIQUE Constraint

```sql
-- Column-level unique
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE
);

-- Table-level unique
CREATE TABLE users (
    id INT PRIMARY KEY,
    email VARCHAR(100),
    UNIQUE (email)
);

-- Composite unique
CREATE TABLE enrollments (
    student_id INT,
    course_id INT,
    UNIQUE (student_id, course_id)
);

-- Add unique constraint
ALTER TABLE users ADD UNIQUE (email);
ALTER TABLE users ADD CONSTRAINT email_unique UNIQUE (email);
```

---

### CHECK Constraint

```sql
-- Column-level check
CREATE TABLE products (
    id INT PRIMARY KEY,
    price DECIMAL(10, 2) CHECK (price > 0),
    stock INT CHECK (stock >= 0)
);

-- Table-level check
CREATE TABLE employees (
    id INT PRIMARY KEY,
    age INT,
    salary DECIMAL(10, 2),
    CHECK (age >= 18),
    CHECK (salary > 0)
);

-- Named check constraint
CREATE TABLE products (
    id INT PRIMARY KEY,
    price DECIMAL(10, 2),
    CONSTRAINT positive_price CHECK (price > 0)
);

-- Complex check
CREATE TABLE orders (
    id INT PRIMARY KEY,
    discount DECIMAL(5, 2),
    CHECK (discount >= 0 AND discount <= 100)
);
```

---

### NOT NULL Constraint

```sql
-- Define NOT NULL
CREATE TABLE users (
    id INT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Add NOT NULL
ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) NOT NULL;

-- Remove NOT NULL
ALTER TABLE users MODIFY COLUMN phone VARCHAR(20) NULL;
```

---

### DEFAULT Constraint

```sql
-- Define default
CREATE TABLE users (
    id INT PRIMARY KEY,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Add default
ALTER TABLE users ALTER COLUMN status SET DEFAULT 'pending';

-- Drop default
ALTER TABLE users ALTER COLUMN status DROP DEFAULT;
```

---

## Functions and Operators

### String Functions

```sql
-- Concatenation
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;
SELECT first_name || ' ' || last_name AS full_name FROM users;  -- PostgreSQL

-- Length
SELECT LENGTH(username) FROM users;
SELECT CHAR_LENGTH(username) FROM users;

-- Uppercase/Lowercase
SELECT UPPER(username), LOWER(email) FROM users;

-- Substring
SELECT SUBSTRING(email, 1, 5) FROM users;
SELECT LEFT(username, 3), RIGHT(username, 3) FROM users;

-- Trim
SELECT TRIM(username) FROM users;
SELECT LTRIM(username), RTRIM(username) FROM users;

-- Replace
SELECT REPLACE(email, '@gmail.com', '@company.com') FROM users;

-- Position
SELECT POSITION('@' IN email) FROM users;
SELECT INSTR(email, '@') FROM users;  -- MySQL
```

---

### Numeric Functions

```sql
-- Rounding
SELECT ROUND(price, 2) FROM products;
SELECT CEIL(price), FLOOR(price) FROM products;
SELECT TRUNCATE(price, 2) FROM products;  -- MySQL

-- Absolute value
SELECT ABS(balance) FROM accounts;

-- Power and square root
SELECT POWER(2, 10), SQRT(16);
SELECT POW(2, 10) FROM DUAL;  -- MySQL

-- Random
SELECT RAND();  -- MySQL (0 to 1)
SELECT RANDOM();  -- PostgreSQL (0 to 1)

-- Modulo
SELECT MOD(10, 3);  -- Result: 1
SELECT 10 % 3;
```

---

### Date and Time Functions

```sql
-- Current date/time
SELECT NOW(), CURRENT_TIMESTAMP;
SELECT CURRENT_DATE, CURRENT_TIME;
SELECT CURDATE(), CURTIME();  -- MySQL

-- Extract parts
SELECT YEAR(order_date), MONTH(order_date), DAY(order_date) FROM orders;
SELECT EXTRACT(YEAR FROM order_date) FROM orders;
SELECT DATE_PART('year', order_date) FROM orders;  -- PostgreSQL

-- Date arithmetic
SELECT DATE_ADD(order_date, INTERVAL 7 DAY) FROM orders;  -- MySQL
SELECT order_date + INTERVAL '7 days' FROM orders;  -- PostgreSQL
SELECT DATE_SUB(NOW(), INTERVAL 30 DAY);  -- MySQL

-- Date difference
SELECT DATEDIFF(NOW(), created_at) AS days_old FROM users;
SELECT AGE(NOW(), created_at) FROM users;  -- PostgreSQL

-- Formatting
SELECT DATE_FORMAT(order_date, '%Y-%m-%d') FROM orders;  -- MySQL
SELECT TO_CHAR(order_date, 'YYYY-MM-DD') FROM orders;  -- PostgreSQL
```

---

### Conditional Functions

```sql
-- CASE expression
SELECT 
    username,
    CASE
        WHEN age < 18 THEN 'Minor'
        WHEN age BETWEEN 18 AND 64 THEN 'Adult'
        ELSE 'Senior'
    END AS age_group
FROM users;

-- Simple CASE
SELECT 
    status,
    CASE status
        WHEN 'pending' THEN 'Waiting'
        WHEN 'processing' THEN 'In Progress'
        WHEN 'completed' THEN 'Done'
        ELSE 'Unknown'
    END AS status_text
FROM orders;

-- COALESCE (return first non-NULL)
SELECT COALESCE(phone, email, 'No contact') AS contact FROM users;

-- NULLIF (return NULL if equal)
SELECT NULLIF(discount, 0) FROM products;

-- IFNULL / ISNULL (MySQL)
SELECT IFNULL(phone, 'N/A') FROM users;

-- IF (MySQL)
SELECT IF(stock > 0, 'Available', 'Out of stock') FROM products;
```

---

## Window Functions

### ROW_NUMBER, RANK, DENSE_RANK

```sql
-- Assign row numbers
SELECT 
    username,
    email,
    ROW_NUMBER() OVER (ORDER BY created_at) AS row_num
FROM users;

-- Rank with gaps
SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- Rank without gaps
SELECT 
    name,
    salary,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- Partition by department
SELECT 
    department,
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;
```

---

### LAG and LEAD

```sql
-- Previous value
SELECT 
    order_date,
    amount,
    LAG(amount) OVER (ORDER BY order_date) AS prev_amount
FROM orders;

-- Next value
SELECT 
    order_date,
    amount,
    LEAD(amount) OVER (ORDER BY order_date) AS next_amount
FROM orders;

-- With offset and default
SELECT 
    order_date,
    amount,
    LAG(amount, 1, 0) OVER (ORDER BY order_date) AS prev_amount
FROM orders;
```

---

### Aggregate Window Functions

```sql
-- Running total
SELECT 
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total
FROM orders;

-- Moving average
SELECT 
    order_date,
    amount,
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg
FROM orders;

-- Percent of total
SELECT 
    category,
    revenue,
    revenue / SUM(revenue) OVER () * 100 AS percent_of_total
FROM category_sales;
```

---

## Transactions

### Basic Transaction

```sql
-- Start transaction
START TRANSACTION;
-- or
BEGIN;

-- Execute queries
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Commit (save changes)
COMMIT;

-- Or rollback (undo changes)
ROLLBACK;
```

---

### Transaction Properties (ACID)

- **Atomicity**: All or nothing
- **Consistency**: Valid state before and after
- **Isolation**: Transactions don't interfere
- **Durability**: Changes persist after commit

---

### Savepoints

```sql
START TRANSACTION;

UPDATE accounts SET balance = balance - 100 WHERE id = 1;

SAVEPOINT sp1;

UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Rollback to savepoint
ROLLBACK TO SAVEPOINT sp1;

-- Or commit everything
COMMIT;
```

---

### Transaction Isolation Levels

```sql
-- Set isolation level
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Example
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION;
SELECT * FROM accounts WHERE id = 1;
-- ... other operations
COMMIT;
```

**Isolation levels:**
- **READ UNCOMMITTED**: Dirty reads possible
- **READ COMMITTED**: No dirty reads
- **REPEATABLE READ**: Consistent reads within transaction
- **SERIALIZABLE**: Fully isolated

---

## Performance Optimization

### Indexes Best Practices

```sql
-- Index foreign keys
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Index frequently searched columns
CREATE INDEX idx_users_email ON users(email);

-- Composite index for multi-column queries
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Index column order matters: most selective first
CREATE INDEX idx_orders_date_status ON orders(order_date, status);

-- Analyze index usage
EXPLAIN SELECT * FROM orders WHERE user_id = 1;
SHOW INDEX FROM orders;
```

---

### Query Optimization Tips

```sql
-- Use EXPLAIN to analyze queries
EXPLAIN SELECT * FROM orders WHERE user_id = 1;
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 1;  -- PostgreSQL

-- Avoid SELECT *
SELECT id, username, email FROM users;  -- Good
SELECT * FROM users;  -- Bad

-- Use EXISTS instead of IN for large subqueries
SELECT * FROM users WHERE EXISTS (
    SELECT 1 FROM orders WHERE orders.user_id = users.id
);

-- Use LIMIT for large result sets
SELECT * FROM orders ORDER BY order_date DESC LIMIT 100;

-- Avoid functions on indexed columns
SELECT * FROM orders WHERE DATE(order_date) = '2024-01-15';  -- Bad
SELECT * FROM orders 
WHERE order_date >= '2024-01-15' 
  AND order_date < '2024-01-16';  -- Good

-- Use JOIN instead of subquery when possible
-- Subquery (slower)
SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);

-- JOIN (faster)
SELECT DISTINCT u.* FROM users u
INNER JOIN orders o ON u.id = o.user_id;
```

---

## Common Table Expressions (CTE)

### Basic CTE

```sql
-- Simple CTE
WITH active_users AS (
    SELECT id, username, email
    FROM users
    WHERE status = 'active'
)
SELECT * FROM active_users
WHERE email LIKE '%@gmail.com';

-- Multiple CTEs
WITH 
user_orders AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    GROUP BY user_id
),
high_value_users AS (
    SELECT user_id
    FROM user_orders
    WHERE order_count > 10
)
SELECT u.username, uo.order_count
FROM users u
INNER JOIN user_orders uo ON u.id = uo.user_id
WHERE u.id IN (SELECT user_id FROM high_value_users);
```

---

### Recursive CTE

```sql
-- Organizational hierarchy
WITH RECURSIVE employee_hierarchy AS (
    -- Base case: top-level managers
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: employees with managers
    SELECT e.id, e.name, e.manager_id, eh.level + 1
    FROM employees e
    INNER JOIN employee_hierarchy eh ON e.manager_id = eh.id
)
SELECT * FROM employee_hierarchy
ORDER BY level, name;

-- Generate number sequence
WITH RECURSIVE numbers AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1
    FROM numbers
    WHERE n < 100
)
SELECT * FROM numbers;
```

---

## Best Practices

### Naming Conventions

- **Tables**: Plural nouns (`users`, `orders`, `products`)
- **Columns**: Lowercase with underscores (`user_id`, `created_at`)
- **Primary keys**: `id` or `table_name_id`
- **Foreign keys**: `referenced_table_id`
- **Indexes**: `idx_table_column`
- **Constraints**: `constraint_type_table_column`

---

### Security Best Practices

1. **Use parameterized queries** (prevent SQL injection)
2. **Principle of least privilege** (minimal permissions)
3. **Never store plain text passwords** (use hashing)
4. **Validate and sanitize input**
5. **Use prepared statements**
6. **Regular backups**
7. **Keep database updated**

---

### Design Best Practices

1. **Normalize data** (reduce redundancy)
2. **Use appropriate data types**
3. **Define constraints** (enforce data integrity)
4. **Index wisely** (balance read/write performance)
5. **Document schema**
6. **Use transactions** (maintain consistency)
7. **Regular maintenance** (optimize, vacuum, analyze)

---

## Quick Reference

### SQL Command Categories

| Category | Commands |
|----------|----------|
| **DDL** (Data Definition) | CREATE, ALTER, DROP, TRUNCATE |
| **DML** (Data Manipulation) | SELECT, INSERT, UPDATE, DELETE |
| **DCL** (Data Control) | GRANT, REVOKE |
| **TCL** (Transaction Control) | COMMIT, ROLLBACK, SAVEPOINT |

---

### Query Execution Order

1. **FROM** - Choose tables
2. **JOIN** - Combine tables
3. **WHERE** - Filter rows
4. **GROUP BY** - Group rows
5. **HAVING** - Filter groups
6. **SELECT** - Choose columns
7. **DISTINCT** - Remove duplicates
8. **ORDER BY** - Sort results
9. **LIMIT** - Limit results

---

## See Also
- [[00 - Programming MOC]] - Programming overview
