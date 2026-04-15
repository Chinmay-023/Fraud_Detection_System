"""
Credit Card Fraud Detection System - Flask Application
This is the main backend application that serves the web interface,
handles predictions, and manages the database.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask import Response
import sqlite3
import pickle
import numpy as np
import os
import csv
import io
from datetime import datetime
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fraud_detection_secret_key'

# Enable CORS for Power BI web connector
@app.after_request
def after_request(response):
    """
    Add CORS headers to allow Power BI web connector access.
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Database path
DATABASE = 'database/fraud_detection.db'

# Load machine learning models
models_loaded = False
lr_model = None
rf_model = None
scaler = None

def load_models():
    """
    Load the pre-trained machine learning models and scaler.
    Returns True if successful, False otherwise.
    """
    global lr_model, rf_model, scaler, models_loaded

    try:
        with open('models/logistic_regression.pkl', 'rb') as f:
            lr_model = pickle.load(f)
        with open('models/random_forest.pkl', 'rb') as f:
            rf_model = pickle.load(f)
        with open('models/scaler.pkl', 'rb') as f:
            scaler = pickle.load(f)
        models_loaded = True
        print("Models loaded successfully!")
        return True
    except FileNotFoundError as e:
        print(f"Error loading models: {e}")
        print("Please run model_training.py first to train the models.")
        return False
    except Exception as e:
        print(f"Unexpected error loading models: {e}")
        return False

def get_db_connection():
    """
    Create and return a database connection.
    """
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """
    Initialize the database with required tables.
    Reads SQL from database.sql file and executes it.
    """
    # Ensure database directory exists
    os.makedirs('database', exist_ok=True)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Read and execute SQL schema
    with open('database.sql', 'r') as f:
        sql_script = f.read()

    # Execute each CREATE TABLE statement
    cursor.executescript(sql_script)

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def preprocess_input(amount, transaction_time, transaction_type, merchant_category, is_international):
    """
    Preprocess user input for model prediction.
    Converts categorical values to numerical format expected by the model.

    Returns:
        numpy array: Processed features ready for model prediction
    """
    # Encode transaction time
    time_mapping = {'Morning': 0, 'Afternoon': 1, 'Evening': 2, 'Night': 3}
    time_encoded = time_mapping.get(transaction_time, 0)

    # Encode transaction type
    type_mapping = {'Online': 0, 'POS': 1, 'ATM': 2}
    type_encoded = type_mapping.get(transaction_type, 0)

    # Encode merchant category
    merchant_mapping = {'Electronics': 0, 'Grocery': 1, 'Travel': 2, 'Others': 3}
    merchant_encoded = merchant_mapping.get(merchant_category, 0)

    # International transaction (0 or 1)
    international = 1 if is_international == 'Yes' else 0

    # Scale the amount using the loaded scaler
    amount_scaled = scaler.transform([[amount]])[0][0]

    # Create feature array (same order as training)
    features = np.array([
        amount_scaled,
        time_encoded,
        type_encoded,
        merchant_encoded,
        international
    ]).reshape(1, -1)

    return features, {
        'amount': amount,
        'amount_scaled': amount_scaled,
        'transaction_time': transaction_time,
        'time_encoded': time_encoded,
        'transaction_type': transaction_type,
        'type_encoded': type_encoded,
        'merchant_category': merchant_category,
        'merchant_encoded': merchant_encoded,
        'is_international': is_international,
        'international_binary': international
    }

def predict_fraud(features):
    """
    Make fraud prediction using both Logistic Regression and Random Forest.
    Returns ensemble prediction with risk score.

    Returns:
        dict: Prediction results including fraud probability, risk score, and model outputs
    """
    # Get predictions from both models
    lr_prob = lr_model.predict_proba(features)[0][1]  # Probability of fraud
    rf_prob = rf_model.predict_proba(features)[0][1]

    # Ensemble: average of both probabilities
    ensemble_prob = (lr_prob + rf_prob) / 2

    # Convert to risk score (0-100%)
    risk_score = ensemble_prob * 100

    # Binary prediction (fraud if probability >= 0.5)
    is_fraud = 1 if ensemble_prob >= 0.5 else 0

    # Determine risk category
    if risk_score >= 80:
        risk_category = 'High Risk'
        alert_level = 'Critical'
    elif risk_score >= 50:
        risk_category = 'Medium Risk'
        alert_level = 'Warning'
    elif risk_score >= 20:
        risk_category = 'Low Risk'
        alert_level = 'Caution'
    else:
        risk_category = 'Safe'
        alert_level = 'None'

    return {
        'is_fraud': is_fraud,
        'risk_score': round(risk_score, 2),
        'risk_category': risk_category,
        'alert_level': alert_level,
        'lr_probability': round(lr_prob * 100, 2),
        'rf_probability': round(rf_prob * 100, 2),
        'ensemble_probability': round(ensemble_prob * 100, 2),
        'prediction_message': 'FRAUD DETECTED!' if is_fraud else 'Transaction appears legitimate'
    }

def save_transaction(data, prediction_results, preprocessed_data):
    """
    Save transaction to database along with prediction results.
    Also creates fraud alerts if necessary.

    Returns:
        int: Transaction ID of the saved record
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert into Transactions table
        cursor.execute('''
            INSERT INTO Transactions (
                user_id, amount, transaction_time, transaction_type,
                merchant_category, is_international, is_fraud,
                prediction_result, risk_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            1,  # Default user_id (could be dynamic with auth)
            preprocessed_data['amount'],
            preprocessed_data['transaction_time'],
            preprocessed_data['transaction_type'],
            preprocessed_data['merchant_category'],
            preprocessed_data['international_binary'],
            prediction_results['is_fraud'],
            'Fraud' if prediction_results['is_fraud'] else 'Safe',
            prediction_results['risk_score']
        ))

        transaction_id = cursor.lastrowid

        # Insert into Risk_Scores table
        cursor.execute('''
            INSERT INTO Risk_Scores (
                transaction_id, logistic_regression_score,
                random_forest_score, final_score, risk_category
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            transaction_id,
            prediction_results['lr_probability'],
            prediction_results['rf_probability'],
            prediction_results['risk_score'],
            prediction_results['risk_category']
        ))

        # If fraud detected, create fraud alert
        if prediction_results['is_fraud']:
            cursor.execute('''
                INSERT INTO Fraud_Alerts (
                    transaction_id, alert_level, alert_message
                ) VALUES (?, ?, ?)
            ''', (
                transaction_id,
                prediction_results['alert_level'],
                f"Potential fraud detected! Risk Score: {prediction_results['risk_score']}%"
            ))

        # Log model prediction
        cursor.execute('''
            INSERT INTO Model_Logs (
                transaction_id, model_name, prediction, probability, input_features
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            transaction_id,
            'Ensemble (LR + RF)',
            prediction_results['is_fraud'],
            prediction_results['ensemble_probability'],
            str(preprocessed_data)
        ))

        conn.commit()
        print(f"Transaction {transaction_id} saved successfully!")
        return transaction_id

    except Exception as e:
        conn.rollback()
        print(f"Error saving transaction: {e}")
        raise
    finally:
        conn.close()

def get_dashboard_stats():
    """
    Retrieve dashboard statistics from database.

    Returns:
        dict: Total transactions, fraud count, safe transactions, and recent transactions
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Total transactions count
        cursor.execute('SELECT COUNT(*) as total FROM Transactions')
        total_transactions = cursor.fetchone()['total']

        # Fraud count
        cursor.execute('SELECT COUNT(*) as fraud FROM Transactions WHERE is_fraud = 1')
        fraud_count = cursor.fetchone()['fraud']

        # Safe transactions
        safe_count = total_transactions - fraud_count

        # Fraud rate
        fraud_rate = (fraud_count / total_transactions * 100) if total_transactions > 0 else 0

        # Recent transactions
        cursor.execute('''
            SELECT t.*, r.risk_category
            FROM Transactions t
            LEFT JOIN Risk_Scores r ON t.transaction_id = r.transaction_id
            ORDER BY t.created_at DESC
            LIMIT 10
        ''')
        recent_transactions = [dict(row) for row in cursor.fetchall()]

        # High risk alerts
        cursor.execute('''
            SELECT a.*, t.amount, t.merchant_category
            FROM Fraud_Alerts a
            JOIN Transactions t ON a.transaction_id = t.transaction_id
            WHERE a.is_resolved = 0
            ORDER BY a.created_at DESC
            LIMIT 5
        ''')
        active_alerts = [dict(row) for row in cursor.fetchall()]

        return {
            'total_transactions': total_transactions,
            'fraud_count': fraud_count,
            'safe_count': safe_count,
            'fraud_rate': round(fraud_rate, 2),
            'recent_transactions': recent_transactions,
            'active_alerts': active_alerts
        }

    finally:
        conn.close()

def get_dashboard_chart_data():
    """
    Build chart-ready data for the live dashboard.

    Returns:
        dict: Data series for recent model scores, fraud trend,
              risk distribution, and amount-vs-risk scatter plot.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT
                t.transaction_id,
                t.amount,
                t.is_fraud,
                t.created_at,
                r.logistic_regression_score,
                r.random_forest_score,
                r.final_score,
                r.risk_category
            FROM Transactions t
            LEFT JOIN Risk_Scores r ON t.transaction_id = r.transaction_id
            ORDER BY t.transaction_id DESC
            LIMIT 12
        ''')
        recent_rows = [dict(row) for row in cursor.fetchall()]
        recent_rows.reverse()

        cursor.execute('''
            SELECT
                DATE(created_at) AS date,
                COUNT(*) AS total_transactions,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) AS fraud_count
            FROM Transactions
            WHERE created_at >= DATETIME('now', '-6 days')
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        ''')
        trend_rows = [dict(row) for row in cursor.fetchall()]

        cursor.execute('''
            SELECT
                risk_category,
                COUNT(*) AS count
            FROM Risk_Scores
            GROUP BY risk_category
            ORDER BY count DESC
        ''')
        risk_rows = [dict(row) for row in cursor.fetchall()]

        recent_model_scores = {
            'labels': [f"TX-{row['transaction_id']}" for row in recent_rows],
            'lr': [round(row['logistic_regression_score'] or 0, 2) for row in recent_rows],
            'rf': [round(row['random_forest_score'] or 0, 2) for row in recent_rows],
            'ensemble': [round(row['final_score'] or 0, 2) for row in recent_rows]
        }

        fraud_trend = {
            'labels': [row['date'] for row in trend_rows],
            'fraud': [int(row['fraud_count'] or 0) for row in trend_rows],
            'safe': [int((row['total_transactions'] or 0) - (row['fraud_count'] or 0)) for row in trend_rows]
        }

        risk_distribution = {
            'labels': [row['risk_category'] or 'Unknown' for row in risk_rows],
            'counts': [int(row['count'] or 0) for row in risk_rows]
        }

        amount_risk_scatter = [
            {
                'label': f"TX-{row['transaction_id']}",
                'amount': round(row['amount'] or 0, 2),
                'risk_score': round(row['final_score'] or 0, 2),
                'is_fraud': bool(row['is_fraud']),
                'risk_category': row['risk_category'] or 'Unknown'
            }
            for row in recent_rows
        ]

        return {
            'recent_model_scores': recent_model_scores,
            'fraud_trend': fraud_trend,
            'risk_distribution': risk_distribution,
            'amount_risk_scatter': amount_risk_scatter,
            'last_updated': datetime.now().isoformat()
        }

    finally:
        conn.close()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """
    Home page - Display the transaction input form.
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Handle form submission, make prediction, save to database.
    Returns prediction result page.
    """
    if not models_loaded:
        return render_template('error.html', error="Models not loaded. Please train models first.")

    try:
        # Get form data
        amount = float(request.form.get('amount', 0))
        transaction_time = request.form.get('transaction_time', 'Morning')
        transaction_type = request.form.get('transaction_type', 'Online')
        merchant_category = request.form.get('merchant_category', 'Others')
        is_international = request.form.get('is_international', 'No')

        # Validate amount
        if amount <= 0:
            return render_template('error.html', error="Please enter a valid transaction amount.")

        # Preprocess input
        features, preprocessed_data = preprocess_input(
            amount, transaction_time, transaction_type, merchant_category, is_international
        )

        # Make prediction
        prediction_results = predict_fraud(features)

        # Save to database
        transaction_id = save_transaction(request.form, prediction_results, preprocessed_data)
        prediction_results['transaction_id'] = transaction_id

        # Render result page
        return render_template('result.html',
                             result=prediction_results,
                             transaction_data=preprocessed_data)

    except Exception as e:
        print(f"Error in predict route: {e}")
        return render_template('error.html', error=str(e))

@app.route('/dashboard')
def dashboard():
    """
    Dashboard page - Display statistics and recent activity.
    """
    stats = get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    API endpoint for programmatic access.
    Returns JSON with prediction results.
    """
    if not models_loaded:
        return jsonify({'error': 'Models not loaded'}), 500

    try:
        data = request.get_json()

        # Get input data
        amount = float(data.get('amount', 0))
        transaction_time = data.get('transaction_time', 'Morning')
        transaction_type = data.get('transaction_type', 'Online')
        merchant_category = data.get('merchant_category', 'Others')
        is_international = data.get('is_international', 'No')

        # Preprocess and predict
        features, preprocessed_data = preprocess_input(
            amount, transaction_time, transaction_type, merchant_category, is_international
        )
        prediction_results = predict_fraud(features)

        # Save to database
        transaction_id = save_transaction(data, prediction_results, preprocessed_data)
        prediction_results['transaction_id'] = transaction_id

        return jsonify({
            'success': True,
            'prediction': prediction_results,
            'transaction_data': {
                'amount': amount,
                'transaction_time': transaction_time,
                'transaction_type': transaction_type,
                'merchant_category': merchant_category,
                'is_international': is_international
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats')
def api_stats():
    """
    API endpoint for dashboard statistics.
    Returns JSON with statistics.
    """
    try:
        stats = get_dashboard_stats()
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/dashboard-data')
def api_dashboard_data():
    """
    API endpoint for live dashboard stats and chart data.
    """
    try:
        return jsonify({
            'success': True,
            'stats': get_dashboard_stats(),
            'charts': get_dashboard_chart_data()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'models_loaded': models_loaded,
        'timestamp': datetime.now().isoformat()
    })

# ==================== POWER BI INTEGRATION ====================

def get_transactions_for_powerbi():
    """
    Retrieve all transactions in a format optimized for Power BI.
    Returns a flat table structure suitable for data analysis.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get comprehensive transaction data with risk scores
        cursor.execute('''
            SELECT
                t.transaction_id,
                t.user_id,
                t.amount,
                t.transaction_time,
                t.transaction_type,
                t.merchant_category,
                t.is_international,
                t.is_fraud,
                t.prediction_result,
                t.risk_score,
                t.created_at as transaction_date,
                r.risk_category,
                r.logistic_regression_score,
                r.random_forest_score,
                r.final_score,
                CASE WHEN a.alert_id IS NOT NULL THEN 1 ELSE 0 END as has_alert,
                a.alert_level,
                a.alert_message,
                a.is_resolved as alert_resolved
            FROM Transactions t
            LEFT JOIN Risk_Scores r ON t.transaction_id = r.transaction_id
            LEFT JOIN Fraud_Alerts a ON t.transaction_id = a.transaction_id
            ORDER BY t.created_at DESC
        ''')

        rows = cursor.fetchall()

        # Convert to list of dictionaries
        transactions = []
        for row in rows:
            transactions.append({
                'transaction_id': row['transaction_id'],
                'user_id': row['user_id'],
                'amount': row['amount'],
                'transaction_time': row['transaction_time'],
                'transaction_type': row['transaction_type'],
                'merchant_category': row['merchant_category'],
                'is_international': bool(row['is_international']),
                'is_fraud': bool(row['is_fraud']),
                'prediction_result': row['prediction_result'],
                'risk_score': row['risk_score'],
                'transaction_date': row['transaction_date'],
                'risk_category': row['risk_category'] or 'Unknown',
                'lr_probability': row['logistic_regression_score'],
                'rf_probability': row['random_forest_score'],
                'final_probability': row['final_score'],
                'has_alert': bool(row['has_alert']),
                'alert_level': row['alert_level'] or 'None',
                'alert_message': row['alert_message'] or '',
                'alert_resolved': bool(row['alert_resolved']) if row['alert_resolved'] is not None else None
            })

        return transactions

    finally:
        conn.close()

def get_daily_summary_for_powerbi():
    """
    Get daily aggregated data for Power BI time-series analysis.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT
                DATE(created_at) as date,
                COUNT(*) as total_transactions,
                SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) as fraud_count,
                SUM(CASE WHEN is_fraud = 0 THEN 1 ELSE 0 END) as safe_count,
                AVG(risk_score) as avg_risk_score,
                AVG(amount) as avg_amount,
                SUM(amount) as total_amount,
                transaction_type,
                merchant_category
            FROM Transactions
            GROUP BY DATE(created_at), transaction_type, merchant_category
            ORDER BY date DESC
        ''')

        rows = cursor.fetchall()

        summary = []
        for row in rows:
            summary.append({
                'date': row['date'],
                'total_transactions': row['total_transactions'],
                'fraud_count': row['fraud_count'],
                'safe_count': row['safe_count'],
                'fraud_rate': round((row['fraud_count'] / row['total_transactions']) * 100, 2),
                'avg_risk_score': round(row['avg_risk_score'], 2) if row['avg_risk_score'] else 0,
                'avg_amount': round(row['avg_amount'], 2),
                'total_amount': round(row['total_amount'], 2),
                'transaction_type': row['transaction_type'],
                'merchant_category': row['merchant_category']
            })

        return summary

    finally:
        conn.close()

@app.route('/api/powerbi/transactions')
def powerbi_transactions():
    """
    Power BI API endpoint - Returns all transaction data.
    Compatible with Power BI Web connector.
    """
    try:
        transactions = get_transactions_for_powerbi()
        return jsonify({
            '@odata.context': 'https://localhost:5000/api/powerbi/$metadata#Transactions',
            'value': transactions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/powerbi/daily-summary')
def powerbi_daily_summary():
    """
    Power BI API endpoint - Returns daily aggregated data.
    Useful for time-series charts and trend analysis.
    """
    try:
        summary = get_daily_summary_for_powerbi()
        return jsonify({
            '@odata.context': 'https://localhost:5000/api/powerbi/$metadata#DailySummary',
            'value': summary
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/powerbi/alerts')
def powerbi_alerts():
    """
    Power BI API endpoint - Returns fraud alerts data.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            SELECT
                a.alert_id,
                a.transaction_id,
                a.alert_level,
                a.alert_message,
                a.is_resolved,
                a.created_at,
                a.resolved_at,
                t.amount,
                t.transaction_time,
                t.transaction_type,
                t.merchant_category,
                t.is_international
            FROM Fraud_Alerts a
            JOIN Transactions t ON a.transaction_id = t.transaction_id
            ORDER BY a.created_at DESC
        ''')

        rows = cursor.fetchall()

        alerts = []
        for row in rows:
            alerts.append({
                'alert_id': row['alert_id'],
                'transaction_id': row['transaction_id'],
                'alert_level': row['alert_level'],
                'alert_message': row['alert_message'],
                'is_resolved': bool(row['is_resolved']),
                'created_at': row['created_at'],
                'resolved_at': row['resolved_at'],
                'amount': row['amount'],
                'transaction_time': row['transaction_time'],
                'transaction_type': row['transaction_type'],
                'merchant_category': row['merchant_category'],
                'is_international': bool(row['is_international'])
            })

        return jsonify({
            '@odata.context': 'https://localhost:5000/api/powerbi/$metadata#Alerts',
            'value': alerts
        })

    finally:
        conn.close()

@app.route('/api/powerbi/export/csv')
def powerbi_export_csv():
    """
    Export transaction data as CSV for Power BI import.
    Power BI can directly import CSV files.
    """
    try:
        transactions = get_transactions_for_powerbi()

        if not transactions:
            return "No data available", 404

        # Create CSV output
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=transactions[0].keys())
        writer.writeheader()
        writer.writerows(transactions)

        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=fraud_detection_data.csv',
                'Content-Type': 'text/csv; charset=utf-8'
            }
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/powerbi/schema')
def powerbi_schema():
    """
    Returns the schema for Power BI data tables.
    Helps with understanding the data structure.
    """
    schema = {
        'tables': [
            {
                'name': 'Transactions',
                'endpoint': '/api/powerbi/transactions',
                'description': 'Main transaction data with fraud predictions',
                'columns': [
                    {'name': 'transaction_id', 'type': 'Integer', 'description': 'Unique transaction identifier'},
                    {'name': 'user_id', 'type': 'Integer', 'description': 'User who made the transaction'},
                    {'name': 'amount', 'type': 'Decimal', 'description': 'Transaction amount in USD'},
                    {'name': 'transaction_time', 'type': 'Text', 'description': 'Time of day: Morning, Afternoon, Evening, Night'},
                    {'name': 'transaction_type', 'type': 'Text', 'description': 'Type: Online, POS, ATM'},
                    {'name': 'merchant_category', 'type': 'Text', 'description': 'Category: Electronics, Grocery, Travel, Others'},
                    {'name': 'is_international', 'type': 'Boolean', 'description': 'Whether transaction is international'},
                    {'name': 'is_fraud', 'type': 'Boolean', 'description': 'True if fraud detected'},
                    {'name': 'prediction_result', 'type': 'Text', 'description': 'Fraud or Safe'},
                    {'name': 'risk_score', 'type': 'Decimal', 'description': 'Risk score percentage (0-100)'},
                    {'name': 'transaction_date', 'type': 'DateTime', 'description': 'When transaction was recorded'},
                    {'name': 'risk_category', 'type': 'Text', 'description': 'Safe, Low Risk, Medium Risk, High Risk, Critical'},
                    {'name': 'lr_probability', 'type': 'Decimal', 'description': 'Logistic Regression fraud probability'},
                    {'name': 'rf_probability', 'type': 'Decimal', 'description': 'Random Forest fraud probability'},
                    {'name': 'final_probability', 'type': 'Decimal', 'description': 'Ensemble model probability'},
                    {'name': 'has_alert', 'type': 'Boolean', 'description': 'Whether fraud alert was generated'},
                    {'name': 'alert_level', 'type': 'Text', 'description': 'None, Caution, Warning, Critical'},
                    {'name': 'alert_resolved', 'type': 'Boolean', 'description': 'Whether alert has been resolved'}
                ]
            },
            {
                'name': 'DailySummary',
                'endpoint': '/api/powerbi/daily-summary',
                'description': 'Aggregated daily statistics for trend analysis',
                'columns': [
                    {'name': 'date', 'type': 'Date', 'description': 'Date of transactions'},
                    {'name': 'total_transactions', 'type': 'Integer', 'description': 'Number of transactions'},
                    {'name': 'fraud_count', 'type': 'Integer', 'description': 'Number of fraudulent transactions'},
                    {'name': 'safe_count', 'type': 'Integer', 'description': 'Number of safe transactions'},
                    {'name': 'fraud_rate', 'type': 'Decimal', 'description': 'Percentage of fraudulent transactions'},
                    {'name': 'avg_risk_score', 'type': 'Decimal', 'description': 'Average risk score'},
                    {'name': 'avg_amount', 'type': 'Decimal', 'description': 'Average transaction amount'},
                    {'name': 'total_amount', 'type': 'Decimal', 'description': 'Total transaction amount'},
                    {'name': 'transaction_type', 'type': 'Text', 'description': 'Type of transaction'},
                    {'name': 'merchant_category', 'type': 'Text', 'description': 'Merchant category'}
                ]
            },
            {
                'name': 'Alerts',
                'endpoint': '/api/powerbi/alerts',
                'description': 'Fraud alert records',
                'columns': [
                    {'name': 'alert_id', 'type': 'Integer', 'description': 'Unique alert identifier'},
                    {'name': 'transaction_id', 'type': 'Integer', 'description': 'Related transaction'},
                    {'name': 'alert_level', 'type': 'Text', 'description': 'Caution, Warning, Critical'},
                    {'name': 'alert_message', 'type': 'Text', 'description': 'Alert description'},
                    {'name': 'is_resolved', 'type': 'Boolean', 'description': 'Resolution status'},
                    {'name': 'created_at', 'type': 'DateTime', 'description': 'Alert creation time'},
                    {'name': 'resolved_at', 'type': 'DateTime', 'description': 'Alert resolution time'},
                    {'name': 'amount', 'type': 'Decimal', 'description': 'Transaction amount'}
                ]
            }
        ]
    }

    return jsonify(schema)

# ==================== MAIN ====================

if __name__ == '__main__':
    print("Starting Fraud Detection System...")

    # Initialize database
    init_database()

    # Load models
    if not load_models():
        print("WARNING: Running without loaded models. Train models first!")

    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
