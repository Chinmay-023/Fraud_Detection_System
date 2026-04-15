-- Credit Card Fraud Detection System Database Schema
-- SQLite Database

-- Table 1: Users - Store user information
CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);

-- Table 2: Transactions - Store all transaction records
CREATE TABLE IF NOT EXISTS Transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL NOT NULL,
    transaction_time VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    merchant_category VARCHAR(30) NOT NULL,
    is_international BOOLEAN NOT NULL,
    is_fraud INTEGER DEFAULT 0,
    prediction_result VARCHAR(10),
    risk_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

-- Table 3: Fraud_Alerts - Store fraud alert notifications
CREATE TABLE IF NOT EXISTS Fraud_Alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    alert_level VARCHAR(20) NOT NULL,
    alert_message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);

-- Table 4: Risk_Scores - Store detailed risk scoring information
CREATE TABLE IF NOT EXISTS Risk_Scores (
    score_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER NOT NULL,
    logistic_regression_score REAL,
    random_forest_score REAL,
    final_score REAL NOT NULL,
    risk_category VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);

-- Table 5: Model_Logs - Store model predictions and performance logs
CREATE TABLE IF NOT EXISTS Model_Logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id INTEGER,
    model_name VARCHAR(50) NOT NULL,
    prediction INTEGER NOT NULL,
    probability REAL,
    confidence REAL,
    input_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON Transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_fraud ON Transactions(is_fraud);
CREATE INDEX IF NOT EXISTS idx_fraud_alerts_transaction ON Fraud_Alerts(transaction_id);
CREATE INDEX IF NOT EXISTS idx_risk_scores_transaction ON Risk_Scores(transaction_id);
CREATE INDEX IF NOT EXISTS idx_model_logs_transaction ON Model_Logs(transaction_id);
