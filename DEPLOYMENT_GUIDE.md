# Deployment Guide - Fraud Detection System

## Option 1: Deploy to Render (Recommended - Easiest)

### Prerequisites
- GitHub account (already set up ✓)
- Render account (free at https://render.com)

### Steps

1. **Go to Render Dashboard**
   - Visit https://render.com
   - Sign up with GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select `Chinmay-023/Fraud_Detection_System`

3. **Configure Service**
   - **Name**: fraud-detection-system
   - **Environment**: Python 3
   - **Build Command**: `./build.sh`
   - **Start Command**: `python run_server.py`
   - **Instance Type**: Free (for testing)

4. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes for deployment
   - Your app will be live at `https://fraud-detection-system.onrender.com`

---

## Option 2: Deploy to Heroku

### Prerequisites
- Heroku account (free at https://www.heroku.com)
- Heroku CLI installed

### Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Push to Heroku
git push heroku main

# Your app will be live at https://your-app-name.herokuapp.com
```

---

## What Was Prepared for Deployment

✅ **Procfile** - Tells hosting platform how to run your app
✅ **runtime.txt** - Specifies Python version (3.11.9)
✅ **build.sh** - Automated build script (installs dependencies, trains models, initializes database)
✅ **.gitignore** - Excludes unnecessary files from deployment
✅ **run_server.py** - Updated to use PORT environment variable
✅ **requirements.txt** - All Python dependencies listed

---

## After Deployment

### Access Your App
- Open your deployed URL in browser
- Fill in transaction form to test fraud detection

### Monitor Logs
**On Render:**
```
Dashboard → Your Service → Logs
```

### Troubleshooting

**Models not loading?**
- Render will run `build.sh` which trains models during deployment
- Takes 2-3 minutes initially

**Database issues?**
- SQLite database is auto-created on first run
- Data persists in Render's ephemeral storage during session

**Port error?**
- Already configured in `run_server.py` ✓

---

## Speed Comparison

| Platform | Setup Time | Free Tier | Speed | Cold Start |
|----------|-----------|----------|-------|-----------|
| Render | 5 min | Yes | Fast | 30-50s |
| Heroku | 10 min | No | Fast | 10-20s |
| Netlify | Not suitable (static only) | - | - | - |

**Recommendation: Use Render for best free hosting experience**

---

## Next Steps

1. Go to https://render.com
2. Sign up with GitHub
3. Follow the steps above to deploy
4. Share your live app URL!

Questions? Let me know! 🚀
