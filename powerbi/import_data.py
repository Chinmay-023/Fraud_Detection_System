"""
Power BI Data Import Script for Fraud Detection System
This script fetches data from the API and prepares it for Power BI.

Usage in Power BI:
1. Install Python support in Power BI
2. Use this script as a data source
3. The output dataframe will be available in Power BI
"""

import pandas as pd
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:5000"

def fetch_transactions():
    """
    Fetch all transaction data from the API.
    Returns a pandas DataFrame.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/powerbi/transactions")
        response.raise_for_status()
        data = response.json()

        # Extract the value array
        transactions = data.get('value', [])

        if not transactions:
            print("No transaction data available")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(transactions)

        # Data type conversions for Power BI
        if not df.empty:
            # Convert datetime strings
            if 'transaction_date' in df.columns:
                df['transaction_date'] = pd.to_datetime(df['transaction_date'])

            # Convert booleans
            bool_columns = ['is_international', 'is_fraud', 'has_alert', 'alert_resolved']
            for col in bool_columns:
                if col in df.columns:
                    df[col] = df[col].astype(bool)

            # Convert numeric columns
            numeric_columns = ['amount', 'risk_score', 'lr_probability', 'rf_probability', 'final_probability']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Add calculated columns for analysis
            df['transaction_hour'] = df['transaction_date'].dt.hour if 'transaction_date' in df.columns else None
            df['transaction_day'] = df['transaction_date'].dt.day_name() if 'transaction_date' in df.columns else None
            df['amount_category'] = df['amount'].apply(categorize_amount) if 'amount' in df.columns else None

        print(f"Fetched {len(df)} transactions")
        return df

    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to API at {API_BASE_URL}")
        print("Make sure the Flask app is running (python app.py)")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return pd.DataFrame()

def fetch_daily_summary():
    """
    Fetch daily aggregated data for time-series analysis.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/powerbi/daily-summary")
        response.raise_for_status()
        data = response.json()

        summary = data.get('value', [])

        if not summary:
            return pd.DataFrame()

        df = pd.DataFrame(summary)

        # Convert date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Convert numeric columns
        numeric_cols = ['total_transactions', 'fraud_count', 'safe_count', 'fraud_rate',
                       'avg_risk_score', 'avg_amount', 'total_amount']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        print(f"Fetched {len(df)} daily summary records")
        return df

    except Exception as e:
        print(f"Error fetching daily summary: {e}")
        return pd.DataFrame()

def fetch_alerts():
    """
    Fetch fraud alerts data.
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/powerbi/alerts")
        response.raise_for_status()
        data = response.json()

        alerts = data.get('value', [])

        if not alerts:
            return pd.DataFrame()

        df = pd.DataFrame(alerts)

        # Convert datetime columns
        datetime_cols = ['created_at', 'resolved_at']
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')

        # Convert booleans
        if 'is_resolved' in df.columns:
            df['is_resolved'] = df['is_resolved'].astype(bool)

        # Calculate resolution time
        if 'resolved_at' in df.columns and 'created_at' in df.columns:
            df['resolution_hours'] = (df['resolved_at'] - df['created_at']).dt.total_seconds() / 3600

        print(f"Fetched {len(df)} alerts")
        return df

    except Exception as e:
        print(f"Error fetching alerts: {e}")
        return pd.DataFrame()

def categorize_amount(amount):
    """
    Categorize transaction amount into buckets.
    """
    if amount < 50:
        return "Small ($0-50)"
    elif amount < 100:
        return "Medium ($50-100)"
    elif amount < 500:
        return "Large ($100-500)"
    else:
        return "Very Large ($500+)"

def generate_summary_stats(transactions_df):
    """
    Generate summary statistics for the dataset.
    Useful for Power BI KPI cards.
    """
    if transactions_df.empty:
        return pd.DataFrame()

    stats = {
        'total_transactions': len(transactions_df),
        'fraud_count': transactions_df['is_fraud'].sum() if 'is_fraud' in transactions_df.columns else 0,
        'total_amount': transactions_df['amount'].sum() if 'amount' in transactions_df.columns else 0,
        'avg_risk_score': transactions_df['risk_score'].mean() if 'risk_score' in transactions_df.columns else 0,
        'fraud_rate': transactions_df['is_fraud'].mean() * 100 if 'is_fraud' in transactions_df.columns else 0,
        'high_risk_count': len(transactions_df[transactions_df['risk_category'].isin(['High Risk', 'Critical'])])
            if 'risk_category' in transactions_df.columns else 0,
        'last_updated': datetime.now()
    }

    return pd.DataFrame([stats])

# Main execution for Power BI
def main():
    """
    Main function that fetches all data.
    This function is called by Power BI to import data.
    """
    print("Starting Power BI data import...")

    # Fetch all data sources
    transactions = fetch_transactions()
    daily_summary = fetch_daily_summary()
    alerts = fetch_alerts()

    # Generate summary statistics
    if not transactions.empty:
        summary_stats = generate_summary_stats(transactions)
    else:
        summary_stats = pd.DataFrame()

    # For Power BI Python integration, we return the main dataframe
    # Power BI can call this script multiple times for different tables
    return transactions

# When running in Power BI, the script output is captured as a dataframe
if __name__ == "__main__":
    # Run main function
    result_df = main()

    # Print summary (for debugging)
    print("\n" + "="*50)
    print("DATA IMPORT SUMMARY")
    print("="*50)
    print(f"Transactions: {len(result_df)} rows")
    print(f"\nColumns: {list(result_df.columns)}")

    if not result_df.empty:
        print(f"\nSample data:")
        print(result_df.head())

    # The dataframe is now available for Power BI
    # In Power BI, use: df = pandas.DataFrame(result_df) 