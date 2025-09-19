-- =====================================================
-- MoMo SMS Data Processing System Database Setup
-- Team: Group 7 (Amazing Mkhonta, Tito Sibo, Kevine Uwisanga)
-- Description: Database schema for processing mobile money transactions
-- Created: January 2024
-- Note: This took us quite a while to get right - lots of iterations!
-- =====================================================

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS momo_sms_processor;
USE momo_sms_processor;

-- =====================================================
-- CORE ENTITIES
-- =====================================================

-- Users/Customers Table
-- Stores information about transaction participants (senders and receivers)
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    phone_number VARCHAR(15) UNIQUE NOT NULL COMMENT 'Primary phone number for MoMo account',
    full_name VARCHAR(100) NOT NULL COMMENT 'User full name',
    id_number VARCHAR(20) UNIQUE COMMENT 'National ID or passport number',
    email VARCHAR(100) COMMENT 'User email address',
    account_status ENUM('ACTIVE', 'SUSPENDED', 'INACTIVE') DEFAULT 'ACTIVE',
    kyc_status ENUM('VERIFIED', 'PENDING', 'REJECTED') DEFAULT 'PENDING' COMMENT 'Know Your Customer verification status',
    registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_phone_number (phone_number),
    INDEX idx_account_status (account_status),
    INDEX idx_kyc_status (kyc_status)
) COMMENT = 'Stores user information for MoMo transaction participants';

-- Transaction Categories Table
-- Defines different types of mobile money transactions
CREATE TABLE transaction_categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) UNIQUE NOT NULL COMMENT 'Category name (e.g., MONEY_TRANSFER, BILL_PAYMENT)',
    category_code VARCHAR(10) UNIQUE NOT NULL COMMENT 'Short code for the category',
    description TEXT COMMENT 'Detailed description of the category',
    is_active BOOLEAN DEFAULT TRUE,
    fee_percentage DECIMAL(5,4) DEFAULT 0.0000 COMMENT 'Transaction fee as percentage',
    minimum_fee DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Minimum fee amount',
    maximum_fee DECIMAL(10,2) DEFAULT 1000.00 COMMENT 'Maximum fee amount',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_category_code (category_code),
    INDEX idx_is_active (is_active)
) COMMENT = 'Defines types of mobile money transactions and associated fees';

-- Service Providers Table (for many-to-many relationship)
-- Stores information about different MoMo service providers
CREATE TABLE service_providers (
    provider_id INT PRIMARY KEY AUTO_INCREMENT,
    provider_name VARCHAR(100) UNIQUE NOT NULL COMMENT 'Provider name (e.g., MTN, Airtel, Vodafone)',
    provider_code VARCHAR(10) UNIQUE NOT NULL COMMENT 'Short provider code',
    api_endpoint VARCHAR(255) COMMENT 'API endpoint for provider integration',
    is_active BOOLEAN DEFAULT TRUE,
    country_code CHAR(2) DEFAULT 'UG' COMMENT 'ISO country code',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_provider_code (provider_code),
    INDEX idx_is_active (is_active),
    INDEX idx_country_code (country_code)
) COMMENT = 'Mobile money service providers';

-- User-Provider Relationship (Many-to-Many Junction Table)
-- Users can have accounts with multiple providers
CREATE TABLE user_provider_accounts (
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    provider_id INT NOT NULL,
    account_number VARCHAR(20) NOT NULL COMMENT 'Account number with the provider',
    account_balance DECIMAL(15,2) DEFAULT 0.00 COMMENT 'Current account balance',
    account_limit DECIMAL(15,2) DEFAULT 10000.00 COMMENT 'Daily transaction limit',
    is_primary BOOLEAN DEFAULT FALSE COMMENT 'Is this the primary account for the user',
    status ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (provider_id) REFERENCES service_providers(provider_id) ON DELETE RESTRICT,
    
    UNIQUE KEY unique_user_provider (user_id, provider_id),
    INDEX idx_account_number (account_number),
    INDEX idx_user_provider (user_id, provider_id),
    INDEX idx_is_primary (is_primary)
) COMMENT = 'Junction table for user-provider many-to-many relationship';

-- Main Transactions Table
-- Core table storing all mobile money transactions
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_reference VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique transaction reference from SMS',
    sender_id INT NOT NULL COMMENT 'User ID of transaction sender',
    receiver_id INT COMMENT 'User ID of transaction receiver (NULL for non-user recipients)',
    receiver_phone VARCHAR(15) COMMENT 'Receiver phone number (for non-registered users)',
    category_id INT NOT NULL,
    provider_id INT NOT NULL,
    amount DECIMAL(15,2) NOT NULL COMMENT 'Transaction amount',
    currency CHAR(3) DEFAULT 'UGX' COMMENT 'Currency code',
    transaction_fee DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Fee charged for transaction',
    net_amount DECIMAL(15,2) GENERATED ALWAYS AS (amount - transaction_fee) STORED COMMENT 'Amount after fees',
    transaction_status ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    transaction_type ENUM('DEBIT', 'CREDIT') NOT NULL COMMENT 'Transaction direction for sender',
    description TEXT COMMENT 'Transaction description from SMS',
    balance_before DECIMAL(15,2) COMMENT 'Sender balance before transaction',
    balance_after DECIMAL(15,2) COMMENT 'Sender balance after transaction',
    transaction_date DATETIME NOT NULL COMMENT 'Date and time of transaction',
    sms_received_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'When SMS was received',
    processed_date DATETIME COMMENT 'When transaction was processed in our system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sender_id) REFERENCES users(user_id) ON DELETE RESTRICT,
    FOREIGN KEY (receiver_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES transaction_categories(category_id) ON DELETE RESTRICT,
    FOREIGN KEY (provider_id) REFERENCES service_providers(provider_id) ON DELETE RESTRICT,
    
    -- Constraints
    CONSTRAINT chk_positive_amount CHECK (amount > 0),
    CONSTRAINT chk_positive_fee CHECK (transaction_fee >= 0),
    CONSTRAINT chk_valid_currency CHECK (currency IN ('UGX', 'USD', 'EUR', 'KES', 'TZS')),
    CONSTRAINT chk_balance_consistency CHECK (
        (balance_before IS NULL AND balance_after IS NULL) OR 
        (balance_before IS NOT NULL AND balance_after IS NOT NULL)
    ),
    
    -- Indexes for performance
    INDEX idx_transaction_reference (transaction_reference),
    INDEX idx_sender_id (sender_id),
    INDEX idx_receiver_id (receiver_id),
    INDEX idx_category_id (category_id),
    INDEX idx_provider_id (provider_id),
    INDEX idx_transaction_date (transaction_date),
    INDEX idx_transaction_status (transaction_status),
    INDEX idx_amount (amount),
    INDEX idx_composite_sender_date (sender_id, transaction_date),
    INDEX idx_composite_status_date (transaction_status, transaction_date)
) COMMENT = 'Main transactions table storing all MoMo transactions';

-- System Logs Table
-- Tracks system processing activities and errors
CREATE TABLE system_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id INT COMMENT 'Related transaction ID if applicable',
    log_level ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG') NOT NULL DEFAULT 'INFO',
    log_category VARCHAR(50) NOT NULL COMMENT 'Category of log (SMS_PROCESSING, DB_OPERATION, API_CALL)',
    message TEXT NOT NULL COMMENT 'Log message details',
    additional_data JSON COMMENT 'Additional structured data in JSON format',
    source_system VARCHAR(50) DEFAULT 'SMS_PROCESSOR' COMMENT 'System component that generated log',
    user_id INT COMMENT 'User ID if log is user-related',
    ip_address VARCHAR(45) COMMENT 'IP address if applicable',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_log_level (log_level),
    INDEX idx_log_category (log_category),
    INDEX idx_created_at (created_at),
    INDEX idx_transaction_id (transaction_id),
    INDEX idx_composite_level_date (log_level, created_at)
) COMMENT = 'System activity and error logs for audit and debugging';

-- =====================================================
-- ADDITIONAL SECURITY AND AUDIT TABLES
-- =====================================================

-- Failed Transaction Attempts
CREATE TABLE failed_transactions (
    failed_id INT PRIMARY KEY AUTO_INCREMENT,
    sms_content TEXT NOT NULL COMMENT 'Original SMS content that failed to process',
    sender_phone VARCHAR(15) COMMENT 'Phone number that sent the SMS',
    failure_reason TEXT NOT NULL COMMENT 'Reason for processing failure',
    error_code VARCHAR(20) COMMENT 'System error code',
    retry_count INT DEFAULT 0 COMMENT 'Number of retry attempts',
    last_retry_date DATETIME COMMENT 'Last retry attempt date',
    is_resolved BOOLEAN DEFAULT FALSE COMMENT 'Whether the issue has been resolved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_sender_phone (sender_phone),
    INDEX idx_is_resolved (is_resolved),
    INDEX idx_created_at (created_at)
) COMMENT = 'Tracks SMS messages that failed to process into transactions';

-- User Session Tracking (for web interface)
CREATE TABLE user_sessions (
    session_id VARCHAR(128) PRIMARY KEY,
    user_id INT NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    user_agent TEXT COMMENT 'Browser/client information',
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    logout_time DATETIME COMMENT 'When user logged out',
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    
    INDEX idx_user_id (user_id),
    INDEX idx_is_active (is_active),
    INDEX idx_last_activity (last_activity)
) COMMENT = 'Tracks user sessions for web interface security';

-- =====================================================
-- SAMPLE DATA INSERTION
-- =====================================================

-- Insert Service Providers
INSERT INTO service_providers (provider_name, provider_code, api_endpoint, country_code) VALUES
('MTN Mobile Money', 'MTN', 'https://api.mtn.ug/momo', 'UG'),
('Airtel Money', 'AIRTEL', 'https://api.airtel.ug/money', 'UG'),
('Vodafone Cash', 'VODAFONE', 'https://api.vodafone.ug/cash', 'UG'),
('Stanbic Bank Mobile', 'STANBIC', 'https://api.stanbicbank.ug/mobile', 'UG'),
('Centenary Bank Mobile', 'CENTENARY', 'https://api.centenary.ug/mobile', 'UG');

-- Insert Transaction Categories
INSERT INTO transaction_categories (category_name, category_code, description, fee_percentage, minimum_fee, maximum_fee) VALUES
('Money Transfer', 'TRANSFER', 'Person to person money transfer', 0.015, 100.00, 15000.00),
('Bill Payment', 'BILL_PAY', 'Utility and service bill payments', 0.01, 50.00, 5000.00),
('Airtime Purchase', 'AIRTIME', 'Mobile airtime top-up', 0.005, 0.00, 1000.00),
('Merchant Payment', 'MERCHANT', 'Payment to registered merchants', 0.02, 200.00, 20000.00),
('Bank Deposit', 'DEPOSIT', 'Deposit to bank account', 0.025, 500.00, 25000.00),
('Bank Withdrawal', 'WITHDRAW', 'Withdrawal from bank account', 0.03, 1000.00, 30000.00),
('Salary Payment', 'SALARY', 'Bulk salary payments', 0.008, 300.00, 10000.00);

-- Insert Sample Users
-- Using realistic Ugandan names and phone numbers
INSERT INTO users (phone_number, full_name, id_number, email, account_status, kyc_status) VALUES
('256781234567', 'John Mukasa', 'CM90123456789', 'john.mukasa@email.com', 'ACTIVE', 'VERIFIED'),
('256782345678', 'Sarah Nakato', 'CM91234567890', 'sarah.nakato@email.com', 'ACTIVE', 'VERIFIED'),
('256783456789', 'David Ssemakula', 'CM92345678901', 'david.ssemakula@email.com', 'ACTIVE', 'PENDING'),
('256784567890', 'Grace Namusoke', 'CM93456789012', 'grace.namusoke@email.com', 'ACTIVE', 'VERIFIED'),
('256785678901', 'Robert Kabuye', 'CM94567890123', 'robert.kabuye@email.com', 'SUSPENDED', 'VERIFIED'), -- This guy had issues
('256786789012', 'Mary Nansubuga', 'CM95678901234', 'mary.nansubuga@email.com', 'ACTIVE', 'REJECTED');

-- Insert User-Provider Account Relationships (Many-to-Many)
INSERT INTO user_provider_accounts (user_id, provider_id, account_number, account_balance, account_limit, is_primary) VALUES
-- John Mukasa accounts
(1, 1, '256781234567', 150000.00, 500000.00, TRUE),   -- MTN (primary)
(1, 2, '256781234567', 75000.00, 200000.00, FALSE),   -- Airtel (secondary)
-- Sarah Nakato accounts
(2, 1, '256782345678', 220000.00, 1000000.00, TRUE),  -- MTN (primary)
(2, 4, 'STB001234567', 50000.00, 300000.00, FALSE),   -- Stanbic (secondary)
-- David Ssemakula accounts
(3, 2, '256783456789', 95000.00, 400000.00, TRUE),    -- Airtel (primary)
(3, 3, '256783456789', 30000.00, 150000.00, FALSE),   -- Vodafone (secondary)
-- Grace Namusoke accounts
(4, 1, '256784567890', 180000.00, 750000.00, TRUE),   -- MTN (primary)
(4, 5, 'CEN987654321', 120000.00, 500000.00, FALSE),  -- Centenary (secondary)
-- Robert Kabuye accounts (suspended user)
(5, 2, '256785678901', 5000.00, 100000.00, TRUE),     -- Airtel (primary)
-- Mary Nansubuga accounts
(6, 3, '256786789012', 85000.00, 350000.00, TRUE);    -- Vodafone (primary)

-- Insert Sample Transactions
INSERT INTO transactions (transaction_reference, sender_id, receiver_id, receiver_phone, category_id, provider_id, amount, transaction_fee, transaction_status, transaction_type, description, balance_before, balance_after, transaction_date, processed_date) VALUES
('MTN123456789001', 1, 2, NULL, 1, 1, 50000.00, 750.00, 'COMPLETED', 'DEBIT', 'Send money to Sarah Nakato', 200000.00, 149250.00, '2024-01-15 10:30:00', '2024-01-15 10:30:15'),
('ATL987654321001', 2, 1, NULL, 1, 1, 25000.00, 375.00, 'COMPLETED', 'DEBIT', 'Send money to John Mukasa', 245000.00, 219625.00, '2024-01-15 14:20:00', '2024-01-15 14:20:10'),
('MTN123456789002', 1, NULL, '256787777777', 2, 1, 15000.00, 150.00, 'COMPLETED', 'DEBIT', 'Pay UMEME bill', 149250.00, 134100.00, '2024-01-16 09:15:00', '2024-01-16 09:15:08'),
('ATL987654321002', 3, 4, NULL, 4, 2, 80000.00, 1600.00, 'COMPLETED', 'DEBIT', 'Pay merchant SuperMarket Ltd', 175000.00, 93400.00, '2024-01-16 16:45:00', '2024-01-16 16:45:12'),
('VOD555666777001', 6, NULL, '256788888888', 3, 3, 5000.00, 25.00, 'COMPLETED', 'DEBIT', 'Buy airtime', 90000.00, 84975.00, '2024-01-17 08:00:00', '2024-01-17 08:00:05'),
('MTN123456789003', 4, NULL, 'BANK001234567', 5, 1, 100000.00, 2500.00, 'PENDING', 'DEBIT', 'Deposit to Stanbic Bank', 280000.00, 177500.00, '2024-01-17 11:30:00', NULL),
('ATL987654321003', 2, 3, NULL, 7, 1, 350000.00, 2800.00, 'COMPLETED', 'CREDIT', 'Salary payment received', 219625.00, 566825.00, '2024-01-18 06:00:00', '2024-01-18 06:00:20');

-- Insert System Logs
INSERT INTO system_logs (transaction_id, log_level, log_category, message, additional_data, source_system, user_id) VALUES
(1, 'INFO', 'SMS_PROCESSING', 'Successfully processed MTN transaction SMS', '{"sms_length": 160, "processing_time_ms": 245}', 'SMS_PROCESSOR', 1),
(2, 'INFO', 'SMS_PROCESSING', 'Successfully processed Airtel transaction SMS', '{"sms_length": 145, "processing_time_ms": 189}', 'SMS_PROCESSOR', 2),
(3, 'WARNING', 'DB_OPERATION', 'Transaction amount exceeds daily limit warning', '{"daily_total": 89250, "limit": 100000, "remaining": 10750}', 'TRANSACTION_VALIDATOR', 1),
(4, 'INFO', 'API_CALL', 'Merchant validation successful', '{"merchant_id": "SUPER001", "response_time_ms": 1200}', 'MERCHANT_VALIDATOR', 3),
(5, 'INFO', 'SMS_PROCESSING', 'Airtime purchase SMS processed', '{"provider": "MTN", "amount": 5000}', 'SMS_PROCESSOR', 6),
(6, 'ERROR', 'TRANSACTION_PROCESSING', 'Bank deposit transaction pending verification', '{"bank_code": "STB", "verification_required": true}', 'BANK_PROCESSOR', 4),
(7, 'INFO', 'BULK_PROCESSING', 'Bulk salary payment processed successfully', '{"batch_id": "SAL_20240118_001", "total_recipients": 1}', 'BULK_PROCESSOR', NULL);

-- Insert Failed Transaction Attempts
INSERT INTO failed_transactions (sms_content, sender_phone, failure_reason, error_code, retry_count) VALUES
('MTN: Dear customer, you have sent UGX 50,000 to Invalid_Format_Phone on 15/01/2024. Your new balance is UGX 100,000.', '256789999999', 'Invalid recipient phone number format', 'ERR_INVALID_PHONE', 2),
('Airtel Money: Transaction of UGX to John Doe failed due to insufficient balance', '256788888888', 'SMS format does not contain valid amount', 'ERR_MISSING_AMOUNT', 1),
('Unknown Provider: You have received UGX 25,000 from 256781234567', '256787777777', 'Unrecognized service provider format', 'ERR_UNKNOWN_PROVIDER', 0);

-- =====================================================
-- PERFORMANCE OPTIMIZATION VIEWS
-- =====================================================

-- Daily Transaction Summary View
CREATE VIEW daily_transaction_summary AS
SELECT 
    DATE(transaction_date) as transaction_day,
    tc.category_name,
    sp.provider_name,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    SUM(transaction_fee) as total_fees,
    AVG(amount) as avg_transaction_amount,
    COUNT(CASE WHEN transaction_status = 'COMPLETED' THEN 1 END) as completed_transactions,
    COUNT(CASE WHEN transaction_status = 'FAILED' THEN 1 END) as failed_transactions
FROM transactions t
JOIN transaction_categories tc ON t.category_id = tc.category_id
JOIN service_providers sp ON t.provider_id = sp.provider_id
GROUP BY DATE(transaction_date), tc.category_name, sp.provider_name
ORDER BY transaction_day DESC, total_amount DESC;

-- User Transaction History View
CREATE VIEW user_transaction_history AS
SELECT 
    t.transaction_id,
    t.transaction_reference,
    sender.full_name as sender_name,
    sender.phone_number as sender_phone,
    COALESCE(receiver.full_name, 'External User') as receiver_name,
    COALESCE(receiver.phone_number, t.receiver_phone) as receiver_phone,
    tc.category_name,
    sp.provider_name,
    t.amount,
    t.transaction_fee,
    t.transaction_status,
    t.transaction_date,
    t.description
FROM transactions t
LEFT JOIN users sender ON t.sender_id = sender.user_id
LEFT JOIN users receiver ON t.receiver_id = receiver.user_id
JOIN transaction_categories tc ON t.category_id = tc.category_id
JOIN service_providers sp ON t.provider_id = sp.provider_id
ORDER BY t.transaction_date DESC;

-- =====================================================
-- STORED PROCEDURES FOR COMMON OPERATIONS
-- =====================================================

DELIMITER //

-- Procedure to get user transaction summary
CREATE PROCEDURE GetUserTransactionSummary(
    IN p_user_id INT,
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        tc.category_name,
        COUNT(*) as transaction_count,
        SUM(CASE WHEN t.transaction_type = 'DEBIT' THEN t.amount ELSE 0 END) as total_sent,
        SUM(CASE WHEN t.transaction_type = 'CREDIT' THEN t.amount ELSE 0 END) as total_received,
        SUM(t.transaction_fee) as total_fees
    FROM transactions t
    JOIN transaction_categories tc ON t.category_id = tc.category_id
    WHERE (t.sender_id = p_user_id OR t.receiver_id = p_user_id)
        AND DATE(t.transaction_date) BETWEEN p_start_date AND p_end_date
        AND t.transaction_status = 'COMPLETED'
    GROUP BY tc.category_name
    ORDER BY total_sent DESC;
END //

-- Procedure to process transaction fee calculation
CREATE PROCEDURE CalculateTransactionFee(
    IN p_category_id INT,
    IN p_amount DECIMAL(15,2),
    OUT p_fee DECIMAL(10,2)
)
BEGIN
    DECLARE v_fee_percentage DECIMAL(5,4);
    DECLARE v_minimum_fee DECIMAL(10,2);
    DECLARE v_maximum_fee DECIMAL(10,2);
    DECLARE v_calculated_fee DECIMAL(10,2);
    
    SELECT fee_percentage, minimum_fee, maximum_fee
    INTO v_fee_percentage, v_minimum_fee, v_maximum_fee
    FROM transaction_categories
    WHERE category_id = p_category_id;
    
    SET v_calculated_fee = p_amount * v_fee_percentage;
    
    SET p_fee = GREATEST(v_minimum_fee, LEAST(v_calculated_fee, v_maximum_fee));
END //

DELIMITER ;

-- =====================================================
-- SECURITY TRIGGERS
-- =====================================================

DELIMITER //

-- Trigger to log user account changes
CREATE TRIGGER user_account_audit 
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF OLD.account_status != NEW.account_status THEN
        INSERT INTO system_logs (log_level, log_category, message, additional_data, user_id)
        VALUES (
            'INFO', 
            'ACCOUNT_STATUS_CHANGE', 
            CONCAT('Account status changed from ', OLD.account_status, ' to ', NEW.account_status),
            JSON_OBJECT('old_status', OLD.account_status, 'new_status', NEW.account_status),
            NEW.user_id
        );
    END IF;
END //

-- Trigger to prevent deletion of completed transactions
CREATE TRIGGER prevent_transaction_deletion
BEFORE DELETE ON transactions
FOR EACH ROW
BEGIN
    IF OLD.transaction_status = 'COMPLETED' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Cannot delete completed transactions for audit compliance';
    END IF;
END //

-- Trigger to auto-update user last activity
CREATE TRIGGER update_user_activity
AFTER INSERT ON transactions
FOR EACH ROW
BEGIN
    UPDATE users 
    SET last_active = CURRENT_TIMESTAMP 
    WHERE user_id = NEW.sender_id;
END //

DELIMITER ;

-- =====================================================
-- FINAL SETUP OPERATIONS
-- =====================================================

-- Create database user for application (optional - for production)
-- CREATE USER 'momo_app'@'localhost' IDENTIFIED BY 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE ON momo_sms_processor.* TO 'momo_app'@'localhost';
-- GRANT DELETE ON momo_sms_processor.system_logs TO 'momo_app'@'localhost';
-- FLUSH PRIVILEGES;

-- Display summary of created objects
-- Let's see what we've built!
SELECT 'Database Setup Complete!' as Status;
SELECT COUNT(*) as 'Tables Created' FROM information_schema.tables WHERE table_schema = 'momo_sms_processor';
SELECT COUNT(*) as 'Sample Users' FROM users;
SELECT COUNT(*) as 'Sample Transactions' FROM transactions;
SELECT COUNT(*) as 'Transaction Categories' FROM transaction_categories;
SELECT COUNT(*) as 'Service Providers' FROM service_providers;
SELECT COUNT(*) as 'System Logs' FROM system_logs;

-- TODO: Add more test data later if needed
-- End of database setup script
