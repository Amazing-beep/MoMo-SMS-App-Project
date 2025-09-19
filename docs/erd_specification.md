# MoMo SMS Database - ERD Design Specification

## Entity Relationship Diagram Design

**Note:** This document provides the specification for creating the ERD diagram using Draw.io or Lucidchart.

### Entities and Attributes

#### 1. Users
- **user_id** (PK) - INT
- phone_number - VARCHAR(15) - UNIQUE
- full_name - VARCHAR(100)
- id_number - VARCHAR(20) - UNIQUE
- email - VARCHAR(100)
- account_status - ENUM('ACTIVE', 'SUSPENDED', 'INACTIVE')
- kyc_status - ENUM('VERIFIED', 'PENDING', 'REJECTED')
- registration_date - DATETIME
- last_active - DATETIME

#### 2. Service_Providers
- **provider_id** (PK) - INT
- provider_name - VARCHAR(100) - UNIQUE
- provider_code - VARCHAR(10) - UNIQUE
- api_endpoint - VARCHAR(255)
- is_active - BOOLEAN
- country_code - CHAR(2)

#### 3. Transaction_Categories
- **category_id** (PK) - INT
- category_name - VARCHAR(50) - UNIQUE
- category_code - VARCHAR(10) - UNIQUE
- description - TEXT
- is_active - BOOLEAN
- fee_percentage - DECIMAL(5,4)
- minimum_fee - DECIMAL(10,2)
- maximum_fee - DECIMAL(10,2)

#### 4. User_Provider_Accounts (Junction Table)
- **account_id** (PK) - INT
- user_id (FK) - INT → Users.user_id
- provider_id (FK) - INT → Service_Providers.provider_id
- account_number - VARCHAR(20)
- account_balance - DECIMAL(15,2)
- account_limit - DECIMAL(15,2)
- is_primary - BOOLEAN
- status - ENUM('ACTIVE', 'SUSPENDED', 'CLOSED')

#### 5. Transactions
- **transaction_id** (PK) - INT
- transaction_reference - VARCHAR(50) - UNIQUE
- sender_id (FK) - INT → Users.user_id
- receiver_id (FK) - INT → Users.user_id (NULLABLE)
- receiver_phone - VARCHAR(15)
- category_id (FK) - INT → Transaction_Categories.category_id
- provider_id (FK) - INT → Service_Providers.provider_id
- amount - DECIMAL(15,2)
- currency - CHAR(3)
- transaction_fee - DECIMAL(10,2)
- net_amount - DECIMAL(15,2) - GENERATED
- transaction_status - ENUM('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED')
- transaction_type - ENUM('DEBIT', 'CREDIT')
- description - TEXT
- balance_before - DECIMAL(15,2)
- balance_after - DECIMAL(15,2)
- transaction_date - DATETIME
- sms_received_date - DATETIME
- processed_date - DATETIME

#### 6. System_Logs
- **log_id** (PK) - INT
- transaction_id (FK) - INT → Transactions.transaction_id (NULLABLE)
- log_level - ENUM('INFO', 'WARNING', 'ERROR', 'DEBUG')
- log_category - VARCHAR(50)
- message - TEXT
- additional_data - JSON
- source_system - VARCHAR(50)
- user_id (FK) - INT → Users.user_id (NULLABLE)
- ip_address - VARCHAR(45)
- created_at - TIMESTAMP

#### 7. Failed_Transactions
- **failed_id** (PK) - INT
- sms_content - TEXT
- sender_phone - VARCHAR(15)
- failure_reason - TEXT
- error_code - VARCHAR(20)
- retry_count - INT
- last_retry_date - DATETIME
- is_resolved - BOOLEAN

#### 8. User_Sessions
- **session_id** (PK) - VARCHAR(128)
- user_id (FK) - INT → Users.user_id
- ip_address - VARCHAR(45)
- user_agent - TEXT
- login_time - DATETIME
- last_activity - DATETIME
- is_active - BOOLEAN
- logout_time - DATETIME

### Relationships and Cardinalities

1. **Users ↔ Service_Providers** (Many-to-Many)
   - Through User_Provider_Accounts junction table
   - One user can have multiple provider accounts
   - One provider can have multiple user accounts

2. **Users → Transactions** (One-to-Many) - Sender
   - sender_id FK in Transactions
   - One user can send many transactions

3. **Users → Transactions** (One-to-Many) - Receiver
   - receiver_id FK in Transactions (nullable)
   - One user can receive many transactions
   - Some transactions may have external receivers

4. **Transaction_Categories → Transactions** (One-to-Many)
   - category_id FK in Transactions
   - One category can be used for many transactions

5. **Service_Providers → Transactions** (One-to-Many)
   - provider_id FK in Transactions
   - One provider can process many transactions

6. **Transactions → System_Logs** (One-to-Many)
   - transaction_id FK in System_Logs (nullable)
   - One transaction can have multiple log entries

7. **Users → System_Logs** (One-to-Many)
   - user_id FK in System_Logs (nullable)
   - One user can have multiple log entries

8. **Users → User_Sessions** (One-to-Many)
   - user_id FK in User_Sessions
   - One user can have multiple sessions

## Design Justification (250 words)

Our ERD design prioritizes scalability and real-world business requirements for mobile money processing. The central decision to separate Users from their provider-specific accounts through a many-to-many relationship reflects the reality that customers often maintain accounts with multiple mobile money providers (MTN, Airtel, Vodafone). This junction table approach allows comprehensive transaction tracking across all user accounts while supporting future provider additions without schema changes.

The Transactions entity serves as the system's core, capturing complete SMS data including balance information crucial for reconciliation. We included both registered (receiver_id) and external recipients (receiver_phone) to handle all transaction types. The generated net_amount column automatically calculates post-fee amounts, reducing calculation errors and ensuring consistency.

Transaction_Categories with configurable fee structures support business rule flexibility. Different transaction types (transfers, bill payments, airtime purchases) have varying fee percentages and limits, which our design accommodates through dedicated fee columns.

The comprehensive logging system (System_Logs) addresses audit requirements critical for financial systems. JSON additional_data fields provide flexibility for varying log contexts while maintaining structured querying capabilities. Failed_Transactions tracking enables error pattern analysis and system improvement.

Security considerations include immutable completed transactions (enforced by triggers), comprehensive audit trails, and user session management for web interface security. Strategic indexing on frequently queried columns (phone numbers, transaction dates, statuses) ensures optimal performance as transaction volumes grow.

This design balances normalization principles with practical performance needs, creating a robust foundation for enterprise-level mobile money transaction processing that can scale with business growth while maintaining data integrity and regulatory compliance.