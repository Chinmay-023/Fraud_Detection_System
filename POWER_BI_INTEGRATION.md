# Power BI Integration Guide

This guide explains how to connect the Fraud Detection System to Microsoft Power BI for advanced analytics and visualization.

## Overview

The Fraud Detection System provides several Power BI-compatible endpoints:

| Endpoint | Description | Use Case |
|----------|-------------|----------|
| `/api/powerbi/transactions` | Full transaction data with predictions | Detailed analysis |
| `/api/powerbi/daily-summary` | Daily aggregated statistics | Time-series charts |
| `/api/powerbi/alerts` | Fraud alert records | Alert monitoring |
| `/api/powerbi/export/csv` | CSV export | Direct file import |
| `/api/powerbi/schema` | Data structure documentation | Reference |

## Connection Methods

### Method 1: Web Connector (Recommended)

Power BI can directly consume JSON REST APIs using the Web connector.

#### Step-by-Step Instructions:

1. **Open Power BI Desktop**
   - Download from: https://powerbi.microsoft.com/desktop

2. **Get Data**
   - Click **Home** → **Get Data** → **Web**

3. **Enter URL**
   ```
   http://localhost:5000/api/powerbi/transactions
   ```

4. **Configure Connection**
   - Select **Advanced** mode if needed
   - No authentication required (for local development)
   - Click **OK**

5. **Transform Data**
   - Power BI will show the JSON structure
   - Click **Into Table** to convert the list
   - Click **Expand** to flatten the columns
   - Click **Close & Apply**

6. **Repeat for Additional Tables**
   - Add another Web connection for daily summary:
   ```
   http://localhost:5000/api/powerbi/daily-summary
   ```

### Method 2: CSV Import

For a simple one-time import or scheduled refresh with CSV files:

1. **Export CSV from API**
   - Open browser: `http://localhost:5000/api/powerbi/export/csv`
   - File will download as `fraud_detection_data.csv`

2. **Import to Power BI**
   - Power BI: **Home** → **Get Data** → **Text/CSV**
   - Select the downloaded file
   - Click **Load**

3. **Schedule Refresh (Optional)**
   - Use Power Automate to schedule CSV downloads
   - Or set up a data gateway for automatic refresh

### Method 3: Python Script (Advanced)

For complex transformations, use Python in Power BI:

1. **Enable Python in Power BI**
   - **File** → **Options** → **Python scripting**
   - Set Python home directory

2. **Use Python Data Source**
   ```python
   import requests
   import pandas as pd

   # Fetch data from API
   url = "http://localhost:5000/api/powerbi/transactions"
   response = requests.get(url)
   data = response.json()['value']

   # Convert to DataFrame
   df = pd.DataFrame(data)

   # Additional processing
   df['risk_score'] = df['risk_score'].astype(float)

   # Output for Power BI
   print(df)
   ```

### Method 4: ODBC Connection (Database Direct)

Connect Power BI directly to the SQLite database:

1. **Download SQLite ODBC Driver**
   - https://www.ch-werner.de/sqliteodbc/
   - Install 64-bit driver

2. **Configure ODBC Data Source**
   - Windows: **ODBC Data Sources (64-bit)**
   - **Add** → Select **SQLite3 ODBC Driver**
   - Data Source Name: `FraudDetectionDB`
   - Database Name: `C:\Users\sruko\Desktop\Practice\fraud_detection_system\database\fraud_detection.db`

3. **Connect in Power BI**
   - **Get Data** → **More** → **ODBC**
   - Select `FraudDetectionDB`
   - Choose tables: `Transactions`, `Risk_Scores`, `Fraud_Alerts`

## Suggested Power BI Visualizations

### 1. Executive Dashboard

| Visualization | Data | Purpose |
|---------------|------|---------|
| Card | COUNT of transaction_id | Total Transactions |
| Card | SUM of is_fraud | Fraud Count |
| Gauge | fraud_rate | Fraud Rate % |
| Line Chart | date + fraud_count | Fraud Trend |

### 2. Transaction Analysis

| Visualization | Fields | Purpose |
|---------------|--------|---------|
| Stacked Bar | merchant_category + is_fraud | Fraud by Category |
| Pie Chart | transaction_type + COUNT | Transaction Mix |
| Heat Map | transaction_time + merchant_category | Risk Patterns |
| Scatter | amount + risk_score | High-Risk Amounts |

### 3. Alert Monitoring

| Visualization | Fields | Purpose |
|---------------|--------|---------|
| Table | All alert columns | Alert Details |
| Donut Chart | alert_level | Alert Distribution |
| Funnel | alert_level → is_resolved | Resolution Flow |

### 4. Model Performance

| Visualization | Calculation | Purpose |
|---------------|-------------|---------|
| Line Chart | lr_probability vs rf_probability | Model Comparison |
| Histogram | risk_score | Score Distribution |
| Matrix | prediction_result vs is_fraud | Confusion Matrix |

## DAX Measures for Power BI

Create these calculated measures in Power BI:

```dax
// Basic Counts
Total Transactions = COUNTROWS('Transactions')

Fraud Count = CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[is_fraud] = TRUE
)

Safe Count = CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[is_fraud] = FALSE
)

// Rates
Fraud Rate = DIVIDE([Fraud Count], [Total Transactions], 0)

Safe Rate = DIVIDE([Safe Count], [Total Transactions], 0)

// Financial
Total Amount = SUM('Transactions'[amount])

Fraud Amount = CALCULATE(
    SUM('Transactions'[amount]),
    'Transactions'[is_fraud] = TRUE
)

Average Risk Score = AVERAGE('Transactions'[risk_score])

// High Risk Transactions
High Risk Count = CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[risk_category] = "High Risk" || 'Transactions'[risk_category] = "Critical"
)

// Time-based
Transactions Today = CALCULATE(
    [Total Transactions],
    DATESBETWEEN(
        'Transactions'[transaction_date],
        TODAY(),
        TODAY()
    )
)

// Model Accuracy (if ground truth available)
True Positives = CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[is_fraud] = TRUE,
    'Transactions'[prediction_result] = "Fraud"
)

Accuracy = DIVIDE([True Positives], [Fraud Count], 0)
```

## Sample Power BI Report Structure

### Page 1: Overview Dashboard
- **KPI Cards**: Total Transactions, Fraud Count, Fraud Rate, Avg Risk Score
- **Line Chart**: Daily fraud trend (last 30 days)
- **Map**: Geographic distribution (if location data added)
- **Slicer**: Date range, Merchant Category

### Page 2: Transaction Details
- **Table**: Transaction list with filters
- **Filters**: Risk Category, Transaction Type, Amount Range
- **Bookmarks**: High-risk transactions view

### Page 3: Fraud Analysis
- **Bar Chart**: Fraud by merchant category
- **Heat Map**: Fraud by time of day
- **Scatter Plot**: Amount vs Risk Score
- **Drill-through**: Transaction details

### Page 4: Model Performance
- **Comparison Chart**: LR vs RF probabilities
- **Histogram**: Risk score distribution
- **Trend**: Model confidence over time
- **Alert Table**: Unresolved alerts

### Page 5: Alerts & Monitoring
- **Alert List**: All active alerts
- **Donut Chart**: Alert level distribution
- **Gauge**: Alerts resolved today
- **Button**: Mark as resolved (requires Power Apps integration)

## Refresh Schedule

### Automatic Refresh Setup

1. **In Power BI Desktop**
   - **Home** → **Transform Data** → **Data source settings**
   - Configure credentials for web sources

2. **In Power BI Service** (app.powerbi.com)
   - Publish report
   - **Dataset** → **Settings** → **Scheduled refresh**
   - Set refresh frequency (e.g., every 15 minutes)
   - Note: Requires data gateway for on-premise data

3. **Data Gateway Setup** (for production)
   - Download: https://powerbi.microsoft.com/gateway/
   - Install on server where app runs
   - Configure in Power BI Service
   - Add data sources

## Troubleshooting

### Connection Issues

**Problem**: Cannot connect to localhost from Power BI Service
**Solution**: Use data gateway or deploy app to cloud server

**Problem**: Web connector shows error
**Solution**: 
1. Verify Flask app is running (`python app.py`)
2. Check firewall settings
3. Try `127.0.0.1` instead of `localhost`

**Problem**: Data not updating
**Solution**:
1. Check Power BI refresh settings
2. Verify API is accessible
3. Check for data caching in Power Query

### Data Issues

**Problem**: Dates not parsing correctly
**Solution**: In Power Query, transform to DateTime type:
```
= Table.TransformColumnTypes(Source, {{"transaction_date", type datetime}})
```

**Problem**: Boolean columns show as text
**Solution**: Add calculated column:
```dax
Is Fraud = IF('Transactions'[is_fraud] = "True", 1, 0)
```

## Security Considerations

For production deployment:

1. **Authentication**: Add API key or OAuth to endpoints
2. **HTTPS**: Use SSL/TLS certificates
3. **IP Whitelisting**: Restrict Power BI service IPs
4. **Row-Level Security**: Implement in Power BI for user access

## Additional Resources

- [Power BI REST API documentation](https://docs.microsoft.com/power-bi/developer/)
- [Power Query M language reference](https://docs.microsoft.com/powerquery-m/)
- [DAX Guide](https://dax.guide/)
- [Flask CORS extension](https://flask-cors.readthedocs.io/) for cross-origin requests

## Support

For issues with:
- **API/Data**: Check Flask app logs
- **Power BI Connection**: Test API in browser first
- **Visualization**: Refer to Power BI community forums
