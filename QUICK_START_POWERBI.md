# Quick Start: Power BI Integration

## Current Status

| Component | Status |
|-----------|--------|
| API Endpoints | ✅ Online |
| CORS Enabled | ✅ Yes |
| Sample Data | ✅ 34 Transactions |
| CSV Export | ✅ Available |
| JSON API | ✅ Available |

## Available Power BI Endpoints

| Endpoint | URL | Format |
|----------|-----|--------|
| Transactions | `http://localhost:5000/api/powerbi/transactions` | JSON |
| Daily Summary | `http://localhost:5000/api/powerbi/daily-summary` | JSON |
| Alerts | `http://localhost:5000/api/powerbi/alerts` | JSON |
| CSV Export | `http://localhost:5000/api/powerbi/export/csv` | CSV |
| Schema | `http://localhost:5000/api/powerbi/schema` | JSON |

## Quick Connect Steps

### Step 1: Open Power BI Desktop
Download from: https://powerbi.microsoft.com/desktop

### Step 2: Get Data
1. Click **Home** → **Get Data** → **Web**
2. Enter URL: `http://localhost:5000/api/powerbi/transactions`
3. Click **OK**

### Step 3: Transform Data
1. Power Query opens with JSON data
2. Click **Into Table**
3. Click **Expand** (double-arrow icon)
4. Select all columns → **OK**
5. Click **Close & Apply**

### Step 4: Create Visualizations

**KPI Cards:**
- Total Transactions = COUNT(transaction_id)
- Fraud Count = SUM(is_fraud)
- Fraud Rate = Fraud Count / Total Transactions * 100

**Charts:**
- Bar Chart: merchant_category vs fraud_count
- Pie Chart: risk_category
- Line Chart: transaction_date vs risk_score
- Table: All transaction details

## Sample DAX Measures

Copy-paste into Power BI:

```dax
Total Transactions = COUNTROWS('Transactions')

Fraud Count = CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[is_fraud] = TRUE
)

Fraud Rate % = DIVIDE([Fraud Count], [Total Transactions], 0) * 100

Total Amount = SUM('Transactions'[amount])

Fraud Amount = CALCULATE(
    SUM('Transactions'[amount]),
    'Transactions'[is_fraud] = TRUE
)

Average Risk Score = AVERAGE('Transactions'[risk_score])

High Risk Transactions = CALCULATE(
    COUNTROWS('Transactions'),
    'Transactions'[risk_category] = "High Risk" || 'Transactions'[risk_category] = "Critical"
)
```

## Current Data Summary

```
Total Transactions: 34
Fraud Detected: 27
Safe Transactions: 7
Fraud Rate: 79%
```

## CSV Import (Alternative)

1. Open browser: http://localhost:5000/api/powerbi/export/csv
2. Save file
3. Power BI: **Get Data** → **Text/CSV**
4. Select downloaded file

## Need More Data?

Run the sample data generator:
```bash
python generate_sample_data.py
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Can't connect | Make sure Flask app is running |
| CORS error | Restart Flask app (CORS is enabled) |
| Empty data | Generate sample data first |
| Date format | Change to DateTime in Power Query |

## Files Created

```
powerbi/
├── import_data.py          # Python script for Power BI
└── [Power BI templates]      # Can be added later

POWER_BI_INTEGRATION.md      # Full documentation
QUICK_START_POWERBI.md        # This file
```

## Support

API Health Check: http://localhost:5000/api/health
Dashboard: http://localhost:5000/dashboard
