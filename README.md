# Credit Card Fraud Detection System

A complete end-to-end machine learning project for detecting credit card fraud using Flask, SQLite, and an ensemble of Logistic Regression and Random Forest models.

## Features

- **Fraud Prediction**: Uses ML ensemble (Logistic Regression + Random Forest) to predict fraudulent transactions
- **Risk Score**: Displays risk score (0-100%) for each transaction
- **Database Storage**: Stores all transactions, alerts, and model logs in SQLite
- **Dashboard**: Visual dashboard showing statistics and recent activity
- **Responsive UI**: Clean, modern web interface that works on all devices

## Project Structure

```
fraud_detection_system/
│
├── app.py                    # Flask web application (main backend)
├── model_training.py         # ML model training script
├── database.sql              # SQL schema for database tables
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── database/                 # SQLite database (auto-created)
│   └── fraud_detection.db
│
├── models/                   # Trained ML models (auto-created)
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   └── scaler.pkl
│
├── data/                     # Synthetic training data (auto-created)
│   └── synthetic_transactions.csv
│
├── templates/                # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── dashboard.html
│   └── error.html
│
└── static/css/               # Stylesheets
    └── style.css
```

## Database Tables

The system uses 5 tables:

1. **Users** - User account information
2. **Transactions** - All transaction records with predictions
3. **Fraud_Alerts** - Fraud alert notifications
4. **Risk_Scores** - Detailed risk scoring from both models
5. **Model_Logs** - Model prediction logs for tracking

## How to Run

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Train the Machine Learning Models

```bash
python model_training.py
```

This will:
- Generate 10,000 synthetic transactions
- Train Logistic Regression and Random Forest models
- Save models to the `models/` directory
- Display model evaluation metrics

### Step 3: Run the Flask Application

```bash
python app.py
```

### Step 4: Access the Application

Open your browser and navigate to: `http://localhost:5000`

## Routes

- `/` - Home page with transaction input form
- `/predict` - Process form submission and display results
- `/dashboard` - Statistics dashboard
- `/api/predict` - JSON API for programmatic predictions
- `/api/stats` - JSON API for dashboard statistics
- `/api/health` - Health check endpoint

## API Usage

### Predict Fraud (POST)

```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 500.00,
    "transaction_time": "Night",
    "transaction_type": "Online",
    "merchant_category": "Electronics",
    "is_international": "Yes"
  }'
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "is_fraud": 1,
    "risk_score": 78.45,
    "risk_category": "Medium Risk",
    "alert_level": "Warning",
    "prediction_message": "FRAUD DETECTED!"
  },
  "transaction_id": 1
}
```

## Input Features

| Feature | Type | Options |
|---------|------|---------|
| Transaction Amount | Number | $0.01 - $100,000 |
| Transaction Time | Select | Morning, Afternoon, Evening, Night |
| Transaction Type | Select | Online, POS, ATM |
| Merchant Category | Select | Electronics, Grocery, Travel, Others |
| International | Radio | Yes, No |

## Model Details

- **Logistic Regression**: Linear classifier with balanced class weights
- **Random Forest**: 100 trees with balanced class weights
- **Ensemble**: Averaged probabilities from both models
- **SMOTE**: Used for handling class imbalance during training

## Sample Input/Output

### Sample Input (Safe Transaction)
```
Amount: $45.50
Time: Morning
Type: POS
Category: Grocery
International: No
```

**Output:**
- Prediction: Safe
- Risk Score: 12.3%
- Risk Category: Safe

### Sample Input (Fraudulent Transaction)
```
Amount: $2500.00
Time: Night
Type: Online
Category: Electronics
International: Yes
```

**Output:**
- Prediction: Fraud Detected
- Risk Score: 78.5%
- Risk Category: Medium Risk
- Alert Generated: Warning level

## Technologies Used

- **Backend**: Python, Flask
- **Database**: SQLite
- **ML Libraries**: scikit-learn, pandas, numpy
- **Imbalanced Learning**: imbalanced-learn (SMOTE)
- **Frontend**: HTML5, CSS3 (custom responsive design)

## Troubleshooting

### Models not found error
Run `python model_training.py` first to generate the models.

### Port already in use
Change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
```

### Database locked
Close all database connections and restart the application.

## License

This project is for educational purposes.

## Author

Built as a complete fraud detection system demonstration.
