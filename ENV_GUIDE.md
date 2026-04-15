# Environment Configuration Guide

## Overview
This project uses environment variables for configuration management. Environment variables allow you to:
- Store sensitive data (API keys, secret keys) outside of code
- Configure different settings for development vs production
- Easily switch configurations without changing code

## Setup

### 1. Create `.env` File
```bash
cp .env.example .env
```

### 2. Edit `.env`
Open `.env` and update values for your environment:

```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-production-secret-key-here
PORT=5000
```

## Environment Variables Explained

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `FLASK_ENV` | Flask environment mode | `production` | `development` or `production` |
| `FLASK_DEBUG` | Enable Flask debug mode | `False` | `True` or `False` |
| `SECRET_KEY` | Flask session secret key | `fraud_detection_secret_key` | Any long random string |
| `PORT` | Server port | `5000` | `5000`, `8000`, `3000` |
| `HOST` | Server host | `0.0.0.0` | `0.0.0.0` or `localhost` |
| `DATABASE_PATH` | Database file path | `database/fraud_detection.db` | Custom path |
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `ENABLE_ANALYTICS` | Enable analytics tracking | `True` | `True` or `False` |
| `ENABLE_ALERTS` | Enable fraud alerts | `True` | `True` or `False` |

## Development vs Production

### Development (.env.development)
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-123
LOG_LEVEL=DEBUG
```

### Production (.env.production)
```env
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=secure-random-key-with-high-entropy-123456789
LOG_LEVEL=INFO
```

## Security Best Practices

✅ **DO:**
- Change `SECRET_KEY` to a strong random string
- Never commit `.env` file to git
- Use unique keys for each environment
- Rotate `SECRET_KEY` periodically
- Use strong, random values for sensitive settings

❌ **DON'T:**
- Hardcode secrets in source code
- Commit `.env` to version control
- Use same secret key in dev and production
- Share `.env` file with others
- Use simple or guessable secret keys

## Example Secret Key Generation

```bash
# On Linux/Mac:
python -c "import secrets; print(secrets.token_hex(32))"

# On Windows PowerShell:
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((Get-Random -Maximum 999999999)))
```

## Using Environment Variables in Code

The app automatically loads variables from `.env` using `python-dotenv`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv('SECRET_KEY')
port = int(os.getenv('PORT', 5000))
```

## Deployment

### Heroku
Set environment variables via CLI:
```bash
heroku config:set SECRET_KEY="your-production-key"
heroku config:set FLASK_ENV="production"
```

### Render
Set environment variables in dashboard:
1. Go to Service Settings
2. Add Environment Variables
3. Set all required variables

### Local Development
1. Copy `.env.example` to `.env`
2. Update values
3. Run app normally - variables are auto-loaded

## Troubleshooting

**"ModuleNotFoundError: No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**Variables not loading?**
- Ensure `.env` file is in project root
- Verify file is named exactly `.env`
- Check variables are in `KEY=value` format
- Restart the application

**Secret key exposed?**
1. Generate new SECRET_KEY
2. Update in `.env`
3. Restart application
4. Consider re-training models if key was compromised

## Template `.env` File

Copy this template and customize:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=change-this-to-random-secure-key

# Server Configuration
PORT=5000
HOST=0.0.0.0

# Database Configuration
DATABASE_PATH=database/fraud_detection.db

# Feature Flags
ENABLE_ANALYTICS=True
ENABLE_ALERTS=True
```

---

For more information, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
