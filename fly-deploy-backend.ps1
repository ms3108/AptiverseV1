# Fly.io Backend Deployment Script
# This script deploys the backend using Docker (fixes mise/buildpack issues)

Write-Host ""
Write-Host "🚀 Deploying Backend to Fly.io (Docker Mode)" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if fly CLI is installed
if (!(Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Fly CLI not found. Installing..." -ForegroundColor Red
    iwr https://fly.io/install.ps1 -useb | iex
    Write-Host "✅ Fly CLI installed. Please restart PowerShell and run this script again." -ForegroundColor Green
    exit
}

# Check if logged in
Write-Host "Checking Fly.io authentication..." -ForegroundColor Yellow
$authStatus = fly auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to Fly.io" -ForegroundColor Red
    Write-Host "Running: fly auth login" -ForegroundColor Yellow
    fly auth login
}

Write-Host "✅ Authenticated with Fly.io" -ForegroundColor Green
Write-Host ""

# Check if app exists
Write-Host "Checking if aptiverse-backend app exists..." -ForegroundColor Yellow
$appExists = fly status --app aptiverse-backend 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ App exists, will update it" -ForegroundColor Green
} else {
    Write-Host "Creating new app: aptiverse-backend" -ForegroundColor Yellow
    fly apps create aptiverse-backend --org personal
}

Write-Host ""

# Get Neon.tech database URL
Write-Host "📊 Database Configuration" -ForegroundColor Cyan
Write-Host "------------------------" -ForegroundColor Cyan
Write-Host ""

$hasNeon = Read-Host "Do you have a Neon.tech database URL? (y/n)"
if ($hasNeon -ne "y") {
    Write-Host ""
    Write-Host "Please set up Neon.tech first:" -ForegroundColor Yellow
    Write-Host "1. Go to https://neon.tech" -ForegroundColor White
    Write-Host "2. Sign up with GitHub" -ForegroundColor White
    Write-Host "3. Create project: aptiverse-db" -ForegroundColor White
    Write-Host "4. Region: Asia Pacific (Singapore)" -ForegroundColor White
    Write-Host "5. Copy the connection string" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter when ready"
}

$databaseUrl = Read-Host "Paste your Neon.tech connection string"
Write-Host "✅ Database URL saved" -ForegroundColor Green

# Generate SECRET_KEY
Write-Host ""
Write-Host "🔐 Generating SECRET_KEY..." -ForegroundColor Cyan
$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "✅ SECRET_KEY generated" -ForegroundColor Green

# Set secrets
Write-Host ""
Write-Host "Setting environment secrets..." -ForegroundColor Yellow

fly secrets set DATABASE_URL="$databaseUrl" --app aptiverse-backend --stage
fly secrets set SECRET_KEY="$secretKey" --app aptiverse-backend --stage
fly secrets set GMAIL_USER="misna5984@gmail.com" --app aptiverse-backend --stage
fly secrets set GMAIL_APP_PASSWORD="rbhbbehowdofefkj" --app aptiverse-backend --stage
fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend --stage
fly secrets set ALGORITHM="HS256" --app aptiverse-backend --stage
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES="30" --app aptiverse-backend --stage
fly secrets set WEAVIATE_URL="http://localhost:8080" --app aptiverse-backend --stage

Write-Host "✅ All secrets configured" -ForegroundColor Green

# Deploy using Docker
Write-Host ""
Write-Host "🐳 Deploying with Docker (bypassing buildpack)..." -ForegroundColor Cyan
Write-Host ""

# Use explicit dockerfile flag to force Docker build
fly deploy --app aptiverse-backend --config fly.backend.toml --dockerfile Dockerfile.backend --strategy immediate

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Backend Deployed Successfully!" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Backend URL: https://aptiverse-backend.fly.dev" -ForegroundColor Cyan
    Write-Host "API Docs: https://aptiverse-backend.fly.dev/docs" -ForegroundColor Cyan
    Write-Host ""
    
    # Seed database
    Write-Host ""
    $seedDb = Read-Host "Do you want to seed the database? (y/n)"
    if ($seedDb -eq "y") {
        Write-Host ""
        Write-Host "Opening SSH console..." -ForegroundColor Yellow
        Write-Host "Run these commands:" -ForegroundColor Cyan
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host "  python seed_data.py" -ForegroundColor White
        Write-Host "  python create_admin.py" -ForegroundColor White
        Write-Host "  exit" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to open SSH"
        fly ssh console --app aptiverse-backend
    }
    
    Write-Host ""
    Write-Host "Next step: Deploy frontend with .\fly-deploy-frontend.ps1" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed. Check logs:" -ForegroundColor Red
    Write-Host "   fly logs --app aptiverse-backend" -ForegroundColor Yellow
}

Write-Host ""
