"""
Generate Sample Data for Power BI Testing
This script creates sample transactions with historical dates
for meaningful Power BI visualizations and analysis.
"""

import requests
import random
import time as time_module
from datetime import datetime, timedelta

API_URL = "http://localhost:5000/api/predict"

# Sample data configurations
TRANSACTION_TIMES = ['Morning', 'Afternoon', 'Evening', 'Night']
TRANSACTION_TYPES = ['Online', 'POS', 'ATM']
MERCHANT_CATEGORIES = ['Electronics', 'Grocery', 'Travel', 'Others']
INTERNATIONAL_OPTIONS = ['Yes', 'No']

def generate_sample_transactions(count=50):
    """
    Generate sample transactions for testing Power BI dashboards.
    """
    print(f"Generating {count} sample transactions...")
    print(f"API Endpoint: {API_URL}")
    print("-" * 50)

    fraud_count = 0
    safe_count = 0

    for i in range(count):
        # Randomize transaction parameters
        # Higher amount = higher fraud probability
        amount = random.choice([
            random.uniform(10, 100),    # Small amounts (safe)
            random.uniform(100, 500),   # Medium amounts
            random.uniform(500, 2000),  # Large amounts (risky)
            random.uniform(2000, 10000) # Very large amounts (very risky)
        ])

        # Night + Online + International + Electronics = Higher fraud risk
        transaction_time = random.choice(TRANSACTION_TIMES)
        transaction_type = random.choice(TRANSACTION_TYPES)
        merchant_category = random.choice(MERCHANT_CATEGORIES)
        is_international = random.choice(INTERNATIONAL_OPTIONS)

        # Create transaction payload
        payload = {
            'amount': round(amount, 2),
            'transaction_time': transaction_time,
            'transaction_type': transaction_type,
            'merchant_category': merchant_category,
            'is_international': is_international
        }

        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', {})

                if prediction.get('is_fraud'):
                    fraud_count += 1
                    status = "FRAUD"
                else:
                    safe_count += 1
                    status = "SAFE"

                risk_score = prediction.get('risk_score', 0)

                print(f"[{i+1}/{count}] {status} - ${amount:.2f} - Risk: {risk_score:.1f}% - "
                      f"{transaction_time}, {transaction_type}, {merchant_category}")
            else:
                print(f"[{i+1}/{count}] Error: HTTP {response.status_code}")

        except Exception as e:
            print(f"[{i+1}/{count}] Error: {e}")

        # Small delay to avoid overwhelming the server
        time_module.sleep(0.1)

    print("-" * 50)
    print(f"Data Generation Complete!")
    print(f"Total Transactions: {count}")
    print(f"Fraud Detected: {fraud_count}")
    print(f"Safe Transactions: {safe_count}")
    print(f"Fraud Rate: {(fraud_count/count)*100:.1f}%")

def generate_test_scenarios():
    """
    Generate specific test scenarios to demonstrate fraud patterns.
    """
    print("\nGenerating specific test scenarios...")
    print("=" * 50)

    scenarios = [
        # (description, amount, time, type, category, international)
        ("Low Risk - Small grocery purchase", 45.50, 'Morning', 'POS', 'Grocery', 'No'),
        ("Low Risk - ATM withdrawal", 100.00, 'Afternoon', 'ATM', 'Others', 'No'),
        ("Medium Risk - Online shopping", 250.00, 'Evening', 'Online', 'Electronics', 'No'),
        ("High Risk - Night international", 1500.00, 'Night', 'Online', 'Electronics', 'Yes'),
        ("High Risk - Large travel purchase", 3000.00, 'Night', 'Online', 'Travel', 'Yes'),
        ("Medium Risk - POS electronics", 800.00, 'Evening', 'POS', 'Electronics', 'No'),
        ("Low Risk - Morning grocery", 75.00, 'Morning', 'POS', 'Grocery', 'No'),
        ("Critical Risk - High value intl", 5000.00, 'Night', 'Online', 'Electronics', 'Yes'),
        ("Low Risk - ATM small", 50.00, 'Morning', 'ATM', 'Others', 'No'),
        ("Medium Risk - Travel booking", 1200.00, 'Afternoon', 'Online', 'Travel', 'Yes'),
    ]

    for i, (desc, amount, time, type_, category, intl) in enumerate(scenarios, 1):
        payload = {
            'amount': amount,
            'transaction_time': time,
            'transaction_type': type_,
            'merchant_category': category,
            'is_international': intl
        }

        try:
            response = requests.post(
                API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                result = response.json()
                prediction = result.get('prediction', {})
                status = "FRAUD" if prediction.get('is_fraud') else "SAFE"
                risk = prediction.get('risk_score', 0)

                print(f"{i}. {desc}")
                print(f"   Amount: ${amount} | Result: {status} | Risk: {risk:.1f}%")

        except Exception as e:
            print(f"{i}. Error: {e}")

        time_module.sleep(0.2)

def main():
    """
    Main function to generate sample data.
    """
    print("=" * 50)
    print("FRAUD DETECTION - SAMPLE DATA GENERATOR")
    print("=" * 50)
    print("\nThis script will create sample transactions")
    print("to populate the database for Power BI testing.")
    print("\nMake sure the Flask app is running!")
    print("Command: python app.py")
    print("=" * 50)

    input("\nPress Enter to start generating data...")

    # Generate random transactions
    generate_sample_transactions(count=30)

    # Generate specific scenarios
    generate_test_scenarios()

    print("\n" + "=" * 50)
    print("DATA GENERATION COMPLETE!")
    print("=" * 50)
    print("\nYou can now:")
    print("1. View the dashboard: http://localhost:5000/dashboard")
    print("2. Connect Power BI to: http://localhost:5000/api/powerbi/transactions")
    print("3. Export CSV: http://localhost:5000/api/powerbi/export/csv")

if __name__ == "__main__":
    main()
