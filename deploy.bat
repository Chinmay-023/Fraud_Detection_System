@echo off
REM Fraud Detection System - Heroku Deployment Script
echo ========================================
echo FRAUD DETECTION SYSTEM - HEROKU DEPLOY
echo ========================================
echo.

REM Check if Heroku CLI is installed
where heroku >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Heroku CLI not found
    echo Please install from: https://devcenter.heroku.com/articles/heroku-cli
    pause
    exit /b 1
)

REM Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Git not found
    pause
    exit /b 1
)

echo [1/5] Logging into Heroku...
call heroku login
if %errorlevel% neq 0 (
    echo Login failed
    pause
    exit /b 1
)

echo.
echo [2/5] Creating Heroku app...
call heroku create fraud-detection-system-chinmay
if %errorlevel% neq 0 (
    echo App creation failed (may already exist)
)

echo.
echo [3/5] Deploying to Heroku...
call git push heroku main

echo.
echo [4/5] Deployment complete!
echo.
echo [5/5] Opening your app in browser...
call heroku open

echo.
echo ========================================
echo DEPLOYMENT SUCCESSFUL!
echo ========================================
echo Your Fraud Detection System is now live at:
echo https://fraud-detection-system-chinmay.herokuapp.com
echo.
pause
