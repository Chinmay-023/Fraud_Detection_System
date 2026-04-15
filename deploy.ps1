# Fraud Detection System - Heroku Deployment Script
# Run in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FRAUD DETECTION SYSTEM - HEROKU DEPLOY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Heroku CLI is installed
$herokuPath = & { Try { (Get-Command heroku -ErrorAction Stop).Path } Catch { $null } }
if (-not $herokuPath) {
    Write-Host "ERROR: Heroku CLI not found" -ForegroundColor Red
    Write-Host "Please install from: https://devcenter.heroku.com/articles/heroku-cli" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Git is installed
$gitPath = & { Try { (Get-Command git -ErrorAction Stop).Path } Catch { $null } }
if (-not $gitPath) {
    Write-Host "ERROR: Git not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/5] Logging into Heroku..." -ForegroundColor Green
heroku login
if ($LASTEXITCODE -ne 0) {
    Write-Host "Login failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[2/5] Creating Heroku app..." -ForegroundColor Green
heroku create fraud-detection-system-chinmay
if ($LASTEXITCODE -ne 0) {
    Write-Host "App creation skipped (may already exist)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[3/5] Deploying to Heroku..." -ForegroundColor Green
git push heroku main

Write-Host ""
Write-Host "[4/5] Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "[5/5] Opening your app in browser..." -ForegroundColor Green
heroku open

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Your Fraud Detection System is now live at:" -ForegroundColor White
Write-Host "https://fraud-detection-system-chinmay.herokuapp.com" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"
