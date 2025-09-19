# MoMo SMS Data Processing System - Database Design Document

**Team:** Group 7 - Amazing Mkhonta, Tito Sibo, Kevine Uwisanga  
**Date:** January 18, 2024  
**Version:** 1.0  

## Executive Summary

This document presents the comprehensive database design for the MoMo SMS Data Processing System, a fullstack enterprise application that processes mobile money transaction data from SMS messages, stores it in a relational database, and provides analytical capabilities through a web interface.

## 1. Entity Relationship Diagram (ERD)

### Core Entities Overview
Our database design implements a robust relational model with the following core entities:

1. **Users** - Customer/participant information
2. **Service Providers** - Mobile money service providers (MTN, Airtel, etc.)
3. **Transaction Categories** - Types of transactions with fee structures
4. **User Provider Accounts** - Many-to-many junction table
5. **Transactions** - Main transaction records
6. **System Logs** - Audit and processing logs
7. **Failed Transactions** - Error tracking
8. **User Sessions** - Web interface security

### Entity Relationships

#### Primary Relationships:
- **Users ↔ Service Providers** (Many-to-Many via User Provider Accounts)
- **Transactions → Users** (sender_id) - Many-to-One
- **Transactions → Users** (receiver_id) - Many-to-One (nullable)  
- **Transactions → Transaction Categories** - Many-to-One
- **Transactions → Service Providers** - Many-to-One
- **System Logs → Transactions** - Many-to-One (nullable)
- **System Logs → Users** - Many-to-One (nullable)

#### Key Design Features:
- **Many-to-Many Resolution:** Users can have accounts with multiple service providers through the `user_provider_accounts` junction table
- **Referential Integrity:** All foreign keys properly constrained with appropriate cascade rules
- **Audit Trail:** Complete logging system with system_logs table
- **Data Validation:** CHECK constraints ensure data integrity
- **Performance Optimization:** Strategic indexing on frequently queried columns

## 2. Design Rationale and Business Logic

### 2.1 User Management Design
**Decision:** Separate user identification from provider-specific accounts
**Rationale:** 
- Users often maintain accounts with multiple mobile money providers
- Enables comprehensive transaction tracking across all user accounts
- Supports future expansion to new providers without schema changes
- Facilitates KYC (Know Your Customer) compliance tracking

**Key Features:**
- Unique phone numbers as primary identifiers
- Account status tracking (ACTIVE, SUSPENDED, INACTIVE)
- KYC status management for regulatory compliance
- Audit timestamps for user activity tracking

### 2.2 Transaction Processing Architecture  
**Decision:** Comprehensive transaction logging with balance tracking
**Rationale:**
- SMS messages contain before/after balance information crucial for reconciliation
- Transaction fees are calculated and stored for financial reporting
- Multiple status states support complex transaction workflows
- Separate tracking of SMS receipt vs. processing timestamps

**Key Features:**
- Generated `net_amount` column for automatic fee calculation
- Support for both registered and external recipients
- Comprehensive transaction status lifecycle
- Balance consistency validation through CHECK constraints

### 2.3 Service Provider Abstraction
**Decision:** Provider-agnostic design with configurable fee structures
**Rationale:**
- Different providers have varying API endpoints and integration requirements
- Fee structures vary by provider and transaction category
- System must support adding new providers without code changes
- Country-specific compliance requirements

**Key Features:**
- Flexible API endpoint configuration
- Provider-specific transaction limits and fee structures
- Country code support for international expansion
- Active/inactive status management

### 2.4 Logging and Audit Design
**Decision:** Comprehensive system activity logging with structured data
**Rationale:**
- Financial systems require extensive audit trails
- JSON additional_data field provides flexibility for varying log contexts
- Multiple log levels support different operational needs
- Source system tracking enables microservice architecture

**Key Features:**
- JSON column for structured additional data
- Hierarchical log levels (DEBUG, INFO, WARNING, ERROR)
- Source system identification for distributed architecture
- Optional transaction and user association

## 3. Data Dictionary

### 3.1 Users Table
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| user_id | INT | PK, AUTO_INCREMENT | Unique user identifier |
| phone_number | VARCHAR(15) | UNIQUE, NOT NULL | Primary MoMo phone number |
| full_name | VARCHAR(100) | NOT NULL | User's complete name |
| id_number | VARCHAR(20) | UNIQUE | National ID/Passport |
| email | VARCHAR(100) | - | Contact email address |
| account_status | ENUM | DEFAULT 'ACTIVE' | Account operational status |
| kyc_status | ENUM | DEFAULT 'PENDING' | KYC verification status |
| registration_date | DATETIME | DEFAULT CURRENT_TIMESTAMP | Account creation date |
| last_active | DATETIME | DEFAULT CURRENT_TIMESTAMP | Last transaction activity |

### 3.2 Transactions Table
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| transaction_id | INT | PK, AUTO_INCREMENT | Unique transaction identifier |
| transaction_reference | VARCHAR(50) | UNIQUE, NOT NULL | SMS transaction reference |
| sender_id | INT | FK to users, NOT NULL | Transaction sender |
| receiver_id | INT | FK to users, NULLABLE | Registered recipient |
| receiver_phone | VARCHAR(15) | - | External recipient phone |
| category_id | INT | FK to categories, NOT NULL | Transaction type |
| provider_id | INT | FK to providers, NOT NULL | Service provider |
| amount | DECIMAL(15,2) | CHECK > 0, NOT NULL | Transaction amount |
| transaction_fee | DECIMAL(10,2) | CHECK >= 0 | Charged fee |
| net_amount | DECIMAL(15,2) | GENERATED STORED | Amount after fees |
| transaction_status | ENUM | DEFAULT 'PENDING' | Processing status |
| transaction_type | ENUM | NOT NULL | DEBIT or CREDIT |
| balance_before | DECIMAL(15,2) | - | Sender balance before |
| balance_after | DECIMAL(15,2) | - | Sender balance after |
| transaction_date | DATETIME | NOT NULL | Transaction timestamp |

### 3.3 User Provider Accounts Table (Junction)
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| account_id | INT | PK, AUTO_INCREMENT | Unique account identifier |
| user_id | INT | FK to users, NOT NULL | User reference |
| provider_id | INT | FK to providers, NOT NULL | Provider reference |
| account_number | VARCHAR(20) | NOT NULL | Provider account number |
| account_balance | DECIMAL(15,2) | DEFAULT 0.00 | Current balance |
| account_limit | DECIMAL(15,2) | DEFAULT 10000.00 | Daily transaction limit |
| is_primary | BOOLEAN | DEFAULT FALSE | Primary account flag |
| status | ENUM | DEFAULT 'ACTIVE' | Account status |

### 3.4 Transaction Categories Table
| Column | Data Type | Constraints | Description |
|--------|-----------|-------------|-------------|
| category_id | INT | PK, AUTO_INCREMENT | Unique category identifier |
| category_name | VARCHAR(50) | UNIQUE, NOT NULL | Display name |
| category_code | VARCHAR(10) | UNIQUE, NOT NULL | Short code |
| description | TEXT | - | Detailed description |
| fee_percentage | DECIMAL(5,4) | DEFAULT 0.0000 | Fee as percentage |
| minimum_fee | DECIMAL(10,2) | DEFAULT 0.00 | Minimum fee amount |
| maximum_fee | DECIMAL(10,2) | DEFAULT 1000.00 | Maximum fee amount |

## 4. Security Rules and Constraints

### 4.1 Data Integrity Constraints
```sql
-- Amount validation
CONSTRAINT chk_positive_amount CHECK (amount > 0)
CONSTRAINT chk_positive_fee CHECK (transaction_fee >= 0)

-- Currency validation  
CONSTRAINT chk_valid_currency CHECK (currency IN ('UGX', 'USD', 'EUR', 'KES', 'TZS'))

-- Balance consistency
CONSTRAINT chk_balance_consistency CHECK (
    (balance_before IS NULL AND balance_after IS NULL) OR 
    (balance_before IS NOT NULL AND balance_after IS NOT NULL)
)

-- User-provider uniqueness
UNIQUE KEY unique_user_provider (user_id, provider_id)
```

### 4.2 Security Triggers
```sql
-- Prevent deletion of completed transactions
CREATE TRIGGER prevent_transaction_deletion
BEFORE DELETE ON transactions
FOR EACH ROW
BEGIN
    IF OLD.transaction_status = 'COMPLETED' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Cannot delete completed transactions for audit compliance';
    END IF;
END

-- Audit user account changes
CREATE TRIGGER user_account_audit 
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    IF OLD.account_status != NEW.account_status THEN
        INSERT INTO system_logs (log_level, log_category, message, additional_data, user_id)
        VALUES ('INFO', 'ACCOUNT_STATUS_CHANGE', 
                CONCAT('Account status changed from ', OLD.account_status, ' to ', NEW.account_status),
                JSON_OBJECT('old_status', OLD.account_status, 'new_status', NEW.account_status),
                NEW.user_id);
    END IF;
END
```

### 4.3 Performance Optimization
```sql
-- Strategic indexing for common queries
INDEX idx_transaction_reference (transaction_reference)
INDEX idx_composite_sender_date (sender_id, transaction_date)
INDEX idx_composite_status_date (transaction_status, transaction_date)
INDEX idx_phone_number (phone_number)
INDEX idx_transaction_date (transaction_date)
```

### 4.4 Access Control Rules
- **Application User:** Limited to SELECT, INSERT, UPDATE on operational tables
- **Read-Only Access:** SELECT permissions only for reporting systems
- **Admin Access:** Full privileges with additional DELETE permissions on logs
- **Backup User:** SELECT permissions for data export operations

## 5. Sample Queries and Expected Results

### 5.1 User Transaction Summary
```sql
-- Get comprehensive transaction summary for a specific user
SELECT 
    u.full_name,
    u.phone_number,
    tc.category_name,
    COUNT(*) as transaction_count,
    SUM(CASE WHEN t.transaction_type = 'DEBIT' THEN t.amount ELSE 0 END) as total_sent,
    SUM(CASE WHEN t.transaction_type = 'CREDIT' THEN t.amount ELSE 0 END) as total_received,
    SUM(t.transaction_fee) as total_fees
FROM users u
JOIN transactions t ON (u.user_id = t.sender_id OR u.user_id = t.receiver_id)
JOIN transaction_categories tc ON t.category_id = tc.category_id
WHERE u.user_id = 1 
    AND t.transaction_status = 'COMPLETED'
    AND DATE(t.transaction_date) BETWEEN '2024-01-15' AND '2024-01-18'
GROUP BY u.user_id, tc.category_name
ORDER BY total_sent DESC;
```

**Expected Result:**
```
| full_name    | phone_number   | category_name  | transaction_count | total_sent | total_received | total_fees |
|--------------|----------------|----------------|-------------------|------------|----------------|------------|
| John Mukasa  | 256781234567   | Money Transfer | 2                 | 75000.00   | 0.00           | 1125.00    |
| John Mukasa  | 256781234567   | Bill Payment   | 1                 | 15000.00   | 0.00           | 150.00     |
```

### 5.2 Daily Transaction Volume Analysis
```sql
-- Analyze daily transaction volumes by provider and category
SELECT 
    DATE(transaction_date) as transaction_day,
    sp.provider_name,
    tc.category_name,
    COUNT(*) as transaction_count,
    SUM(amount) as total_amount,
    SUM(transaction_fee) as total_fees,
    AVG(amount) as avg_transaction_amount
FROM transactions t
JOIN service_providers sp ON t.provider_id = sp.provider_id
JOIN transaction_categories tc ON t.category_id = tc.category_id
WHERE DATE(transaction_date) BETWEEN '2024-01-15' AND '2024-01-18'
    AND t.transaction_status = 'COMPLETED'
GROUP BY DATE(transaction_date), sp.provider_name, tc.category_name
ORDER BY transaction_day DESC, total_amount DESC;
```

**Expected Result:**
```
| transaction_day | provider_name     | category_name  | transaction_count | total_amount | total_fees | avg_transaction_amount |
|-----------------|-------------------|----------------|-------------------|--------------|------------|------------------------|
| 2024-01-18      | MTN Mobile Money  | Salary Payment | 1                 | 350000.00    | 2800.00    | 350000.00              |
| 2024-01-17      | MTN Mobile Money  | Bank Deposit   | 1                 | 100000.00    | 2500.00    | 100000.00              |
| 2024-01-17      | Vodafone Cash     | Airtime Purchase| 1                | 5000.00      | 25.00      | 5000.00                |
| 2024-01-16      | Airtel Money      | Merchant Payment| 1                | 80000.00     | 1600.00    | 80000.00               |
| 2024-01-16      | MTN Mobile Money  | Bill Payment   | 1                 | 15000.00     | 150.00     | 15000.00               |
```

### 5.3 Failed Transaction Analysis
```sql
-- Identify patterns in failed transaction attempts
SELECT 
    error_code,
    COUNT(*) as failure_count,
    AVG(retry_count) as avg_retries,
    COUNT(CASE WHEN is_resolved = TRUE THEN 1 END) as resolved_count,
    ROUND(COUNT(CASE WHEN is_resolved = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as resolution_rate
FROM failed_transactions
WHERE DATE(created_at) >= '2024-01-01'
GROUP BY error_code
ORDER BY failure_count DESC;
```

**Expected Result:**
```
| error_code          | failure_count | avg_retries | resolved_count | resolution_rate |
|---------------------|---------------|-------------|----------------|-----------------|
| ERR_INVALID_PHONE   | 1             | 2.0         | 0              | 0.00            |
| ERR_MISSING_AMOUNT  | 1             | 1.0         | 0              | 0.00            |
| ERR_UNKNOWN_PROVIDER| 1             | 0.0         | 0              | 0.00            |
```

## 6. Business Rules and Validation

### 6.1 Transaction Processing Rules
1. **Amount Validation:** All transaction amounts must be positive (> 0)
2. **Fee Calculation:** Fees calculated based on category rules (percentage with min/max limits)
3. **Balance Consistency:** If balance information exists, both before and after must be present
4. **Reference Uniqueness:** Each transaction reference from SMS must be unique
5. **Status Workflow:** Transactions follow: PENDING → COMPLETED/FAILED/CANCELLED

### 6.2 User Account Rules
1. **Phone Uniqueness:** Each phone number can only belong to one user
2. **KYC Requirements:** Certain transaction limits based on KYC verification status
3. **Account Limits:** Daily transaction limits enforced per provider account
4. **Primary Account:** Each user must have exactly one primary account per provider

### 6.3 Audit and Compliance Rules
1. **Immutable Records:** Completed transactions cannot be deleted (enforced by trigger)
2. **Activity Logging:** All critical system activities must be logged
3. **Data Retention:** Transaction records retained indefinitely for compliance
4. **Change Tracking:** User account status changes automatically logged

## 7. Scalability and Performance Considerations

### 7.1 Indexing Strategy
- **Primary queries:** Optimized with composite indexes on commonly filtered columns
- **Date-based queries:** Specific indexes on transaction dates for time-series analysis
- **User lookups:** Fast phone number and user ID lookups
- **Status filtering:** Efficient transaction status queries

### 7.2 Future Enhancements
- **Partitioning:** Table partitioning by date for large transaction volumes
- **Read Replicas:** Separate read-only databases for reporting and analytics
- **Archiving:** Historical data archiving strategy for older transactions
- **Caching:** Redis integration for frequently accessed user and category data

## 8. Conclusion

This database design provides a robust foundation for the MoMo SMS Data Processing System, supporting:
- **Scalable Architecture:** Handles growing transaction volumes and new providers
- **Data Integrity:** Comprehensive constraints and validation rules
- **Audit Compliance:** Complete transaction tracking and system logging  
- **Performance:** Optimized for common query patterns
- **Security:** Protected against data corruption and unauthorized access
- **Flexibility:** JSON fields and extensible provider model support future requirements

The design successfully translates the business requirements for mobile money transaction processing into a normalized, secure, and performant relational database schema that will serve as the foundation for the complete fullstack application.