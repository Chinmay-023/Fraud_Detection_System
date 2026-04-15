"""
Credit Card Fraud Detection - Model Training Script
This script trains Logistic Regression and Random Forest models
for fraud detection using synthetic data.
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

# Create directories if they don't exist
os.makedirs('models', exist_ok=True)
os.makedirs('data', exist_ok=True)

def generate_synthetic_data(n_samples=10000):
    """
    Generate synthetic credit card transaction data.
    Creates a balanced dataset with fraud and non-fraud examples.
    """
    np.random.seed(42)

    print("Generating synthetic dataset...")

    # Transaction Amount (normalized later)
    amount = np.random.exponential(100, n_samples)

    # Transaction Time categories
    time_categories = ['Morning', 'Afternoon', 'Evening', 'Night']
    transaction_time = np.random.choice(time_categories, n_samples)

    # Transaction Type
    type_categories = ['Online', 'POS', 'ATM']
    transaction_type = np.random.choice(type_categories, n_samples)

    # Merchant Category
    merchant_categories = ['Electronics', 'Grocery', 'Travel', 'Others']
    merchant_category = np.random.choice(merchant_categories, n_samples)

    # International Transaction
    is_international = np.random.choice([0, 1], n_samples, p=[0.8, 0.2])

    # Create fraud patterns (higher probability for certain patterns)
    fraud_probability = np.zeros(n_samples)

    # High amounts increase fraud probability
    fraud_probability += (amount > np.percentile(amount, 90)) * 0.3

    # Night transactions are more suspicious
    fraud_probability += (transaction_time == 'Night') * 0.2

    # Online transactions have higher fraud risk
    fraud_probability += (transaction_type == 'Online') * 0.2

    # International transactions are riskier
    fraud_probability += is_international * 0.2

    # Electronics have higher fraud rates
    fraud_probability += (merchant_category == 'Electronics') * 0.1

    # Generate fraud labels based on probability
    is_fraud = np.random.binomial(1, np.clip(fraud_probability, 0, 0.9))

    # Create DataFrame
    data = pd.DataFrame({
        'amount': amount,
        'transaction_time': transaction_time,
        'transaction_type': transaction_type,
        'merchant_category': merchant_category,
        'is_international': is_international,
        'is_fraud': is_fraud
    })

    print(f"Dataset generated with {n_samples} samples")
    print(f"Fraud cases: {sum(is_fraud)} ({100*sum(is_fraud)/n_samples:.2f}%)")
    print(f"Non-fraud cases: {sum(1-is_fraud)} ({100*sum(1-is_fraud)/n_samples:.2f}%)")

    return data

def preprocess_data(df):
    """
    Preprocess the data for model training.
    - Encode categorical variables
    - Scale numerical features
    """
    print("\nPreprocessing data...")

    # Create a copy
    df_processed = df.copy()

    # Encode categorical variables
    # Transaction Time: Morning=0, Afternoon=1, Evening=2, Night=3
    time_mapping = {'Morning': 0, 'Afternoon': 1, 'Evening': 2, 'Night': 3}
    df_processed['transaction_time_encoded'] = df_processed['transaction_time'].map(time_mapping)

    # Transaction Type: Online=0, POS=1, ATM=2
    type_mapping = {'Online': 0, 'POS': 1, 'ATM': 2}
    df_processed['transaction_type_encoded'] = df_processed['transaction_type'].map(type_mapping)

    # Merchant Category: Electronics=0, Grocery=1, Travel=2, Others=3
    merchant_mapping = {'Electronics': 0, 'Grocery': 1, 'Travel': 2, 'Others': 3}
    df_processed['merchant_category_encoded'] = df_processed['merchant_category'].map(merchant_mapping)

    # Scale the amount feature
    scaler = StandardScaler()
    df_processed['amount_scaled'] = scaler.fit_transform(df_processed[['amount']])

    # Save the scaler for later use
    with open('models/scaler.pkl', 'wb') as f:
        pickle.dump(scaler, f)
    print("Scaler saved to models/scaler.pkl")

    # Select features for training
    feature_columns = [
        'amount_scaled',
        'transaction_time_encoded',
        'transaction_type_encoded',
        'merchant_category_encoded',
        'is_international'
    ]

    X = df_processed[feature_columns]
    y = df_processed['is_fraud']

    return X, y, scaler

def handle_imbalanced_data(X, y):
    """
    Handle class imbalance using SMOTE (Synthetic Minority Over-sampling Technique).
    """
    print("\nHandling class imbalance with SMOTE...")

    print(f"Before SMOTE: {dict(zip(*np.unique(y, return_counts=True)))}")

    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    print(f"After SMOTE: {dict(zip(*np.unique(y_resampled, return_counts=True)))}")

    return X_resampled, y_resampled

def train_models(X, y):
    """
    Train Logistic Regression and Random Forest models.
    """
    print("\nTraining models...")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train Logistic Regression
    print("\nTraining Logistic Regression...")
    lr_model = LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced')
    lr_model.fit(X_train, y_train)

    # Train Random Forest
    print("Training Random Forest...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )
    rf_model.fit(X_train, y_train)

    # Evaluate models
    print("\n" + "="*50)
    print("MODEL EVALUATION")
    print("="*50)

    # Logistic Regression Evaluation
    lr_pred = lr_model.predict(X_test)
    lr_prob = lr_model.predict_proba(X_test)[:, 1]
    lr_auc = roc_auc_score(y_test, lr_prob)

    print("\nLogistic Regression Results:")
    print(f"ROC-AUC Score: {lr_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, lr_pred))

    # Random Forest Evaluation
    rf_pred = rf_model.predict(X_test)
    rf_prob = rf_model.predict_proba(X_test)[:, 1]
    rf_auc = roc_auc_score(y_test, rf_prob)

    print("\nRandom Forest Results:")
    print(f"ROC-AUC Score: {rf_auc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, rf_pred))

    return lr_model, rf_model

def save_models(lr_model, rf_model):
    """
    Save trained models to disk using pickle.
    """
    print("\nSaving models...")

    # Save Logistic Regression model
    with open('models/logistic_regression.pkl', 'wb') as f:
        pickle.dump(lr_model, f)
    print("Logistic Regression saved to models/logistic_regression.pkl")

    # Save Random Forest model
    with open('models/random_forest.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    print("Random Forest saved to models/random_forest.pkl")

def create_ensemble_prediction(lr_model, rf_model, X):
    """
    Create ensemble prediction combining both models.
    """
    lr_prob = lr_model.predict_proba(X)[:, 1]
    rf_prob = rf_model.predict_proba(X)[:, 1]

    # Average probabilities (you can adjust weights)
    ensemble_prob = (lr_prob + rf_prob) / 2
    ensemble_pred = (ensemble_prob >= 0.5).astype(int)

    return ensemble_pred, ensemble_prob

def main():
    """
    Main function to orchestrate model training.
    """
    print("="*50)
    print("CREDIT CARD FRAUD DETECTION - MODEL TRAINING")
    print("="*50)

    # Generate synthetic data
    data = generate_synthetic_data(n_samples=10000)

    # Save raw data
    data.to_csv('data/synthetic_transactions.csv', index=False)
    print(f"\nSynthetic data saved to data/synthetic_transactions.csv")

    # Preprocess data
    X, y, scaler = preprocess_data(data)

    # Handle imbalanced data
    X_resampled, y_resampled = handle_imbalanced_data(X, y)

    # Train models
    lr_model, rf_model = train_models(X_resampled, y_resampled)

    # Save models
    save_models(lr_model, rf_model)

    print("\n" + "="*50)
    print("TRAINING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print("\nFiles created:")
    print("  - models/logistic_regression.pkl")
    print("  - models/random_forest.pkl")
    print("  - models/scaler.pkl")
    print("  - data/synthetic_transactions.csv")

if __name__ == "__main__":
    main()
