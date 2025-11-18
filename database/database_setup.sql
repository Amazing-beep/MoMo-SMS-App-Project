-- drop old tables if they exist
DROP TABLE IF EXISTS system_logs;
DROP TABLE IF EXISTS transaction_participants;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS transaction_categories;
DROP TABLE IF EXISTS users;

-- users table
CREATE TABLE users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  phone_number VARCHAR(20),
  name VARCHAR(100)
);

-- transaction categories
CREATE TABLE transaction_categories (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(50),
  description TEXT
);

-- transactions table
CREATE TABLE transactions (
  transaction_id INT AUTO_INCREMENT PRIMARY KEY,
  receiver_id INT,
  sender_id INT,
  amount DECIMAL(10,2),
  currency VARCHAR(3),
  transaction_date DATETIME,
  fee DECIMAL(10,2),
  category_id INT
);

-- transaction participants
CREATE TABLE transaction_participants (
  participant_id INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id INT,
  user_id INT,
  participant_type ENUM('SENDER','RECEIVER')
);

-- system logs
CREATE TABLE system_logs (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  transaction_id INT,
  log_type ENUM('INFO','WARNING','ERROR'),
  log_timestamp DATETIME,
  sms_address VARCHAR(50),
  message TEXT
);

-- sample data

INSERT INTO users (phone_number, name) VALUES
('1234567890', 'Alice'),
('2345678901', 'Bob'),
('3456789012', 'Charlie'),
('4567890123', 'David'),
('5678901234', 'Eva');

INSERT INTO transaction_categories (category_name, description) VALUES
('Transfer', 'Money transfers'),
('Bill', 'Bill payments'),
('Purchase', 'Goods and services'),
('Refund', 'Refunds'),
('Donation', 'Charity donations');

INSERT INTO transactions (receiver_id, sender_id, amount, currency, transaction_date, fee, category_id) VALUES
(1, 2, 100.50, 'USD', NOW(), 1.50, 1),
(3, 1, 250.00, 'USD', NOW(), 2.00, 2),
(2, 4, 75.25, 'USD', NOW(), 0.75, 3),
(5, 3, 300.00, 'USD', NOW(), 3.00, 4),
(4, 5, 150.00, 'USD', NOW(), 1.00, 5);

INSERT INTO transaction_participants (transaction_id, user_id, participant_type) VALUES
(1, 2, 'SENDER'),
(1, 1, 'RECEIVER'),
(2, 1, 'SENDER'),
(2, 3, 'RECEIVER'),
(3, 4, 'SENDER');

INSERT INTO system_logs (transaction_id, log_type, log_timestamp, sms_address, message) VALUES
(1, 'INFO', NOW(), '1234567890', 'Transaction ok'),
(2, 'WARNING', NOW(), '2345678901', 'Delayed'),
(3, 'ERROR', NOW(), '3456789012', 'Failed'),
(4, 'INFO', NOW(), '4567890123', 'Completed'),
(5, 'INFO', NOW(), '5678901234', 'Processed');
