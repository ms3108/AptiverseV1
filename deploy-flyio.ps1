# Fly.io Deployment Script for Aptiverse
# Run this script to deploy your app to Fly.io

Write-Host "🚀 Aptiverse Fly.io Deployment Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
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

Write-Host ""
Write-Host "✅ Authenticated with Fly.io" -ForegroundColor Green
Write-Host ""

# Step 1: Create PostgreSQL Database
Write-Host "📊 Step 1: Creating PostgreSQL Database" -ForegroundColor Cyan
Write-Host "--------------------------------------" -ForegroundColor Cyan
$createDb = Read-Host "Do you want to create a new PostgreSQL database? (y/n)"
if ($createDb -eq "y") {
    Write-Host "Creating database..." -ForegroundColor Yellow
    fly postgres create --name aptiverse-db --region ord --vm-size shared-cpu-1x --volume-size 1
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Save the password shown above!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter once you've saved the password"
}

# Get database password
$dbPassword = Read-Host "Enter your PostgreSQL password"
$databaseUrl = "postgresql://postgres:${dbPassword}@aptiverse-db.internal:5432/postgres"

# Step 2: Set up secrets
Write-Host ""
Write-Host "🔐 Step 2: Generating Secrets" -ForegroundColor Cyan
Write-Host "-----------------------------" -ForegroundColor Cyan

# Generate SECRET_KEY
Write-Host "Generating SECRET_KEY..." -ForegroundColor Yellow
$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "✅ SECRET_KEY generated" -ForegroundColor Green

# Get Gmail credentials
$gmailUser = Read-Host "Enter your Gmail address (e.g., your-email@gmail.com)"
$gmailPassword = Read-Host "Enter your Gmail App Password (16 characters)" -AsSecureString
$gmailPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($gmailPassword))

# Step 3: Deploy Backend
Write-Host ""
Write-Host "🚀 Step 3: Deploying Backend" -ForegroundColor Cyan
Write-Host "---------------------------" -ForegroundColor Cyan

$deployBackend = Read-Host "Deploy backend now? (y/n)"
if ($deployBackend -eq "y") {
    Write-Host "Setting secrets..." -ForegroundColor Yellow
    
    # Set secrets for backend
    fly secrets set DATABASE_URL="$databaseUrl" --app aptiverse-backend
    fly secrets set SECRET_KEY="$secretKey" --app aptiverse-backend
    fly secrets set GMAIL_USER="$gmailUser" --app aptiverse-backend
    fly secrets set GMAIL_APP_PASSWORD="$gmailPasswordPlain" --app aptiverse-backend
    fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
    fly secrets set WEAVIATE_URL="http://localhost:8080" --app aptiverse-backend
    
    Write-Host "Deploying backend..." -ForegroundColor Yellow
    fly deploy --config fly.backend.toml
    
    Write-Host "✅ Backend deployed!" -ForegroundColor Green
    
    # Seed database
    Write-Host ""
    $seedDb = Read-Host "Do you want to seed the database? (y/n)"
    if ($seedDb -eq "y") {
        Write-Host "Seeding database..." -ForegroundColor Yellow
        Write-Host "Run these commands in the SSH console that will open:" -ForegroundColor Yellow
        Write-Host "  cd backend" -ForegroundColor White
        Write-Host "  python seed_data.py" -ForegroundColor White
        Write-Host "  python create_admin.py" -ForegroundColor White
        Write-Host "  exit" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to open SSH console"
        fly ssh console --app aptiverse-backend
    }
}

# Step 4: Deploy Frontend
Write-Host ""
Write-Host "🌐 Step 4: Deploying Frontend" -ForegroundColor Cyan
Write-Host "----------------------------" -ForegroundColor Cyan

$deployFrontend = Read-Host "Deploy frontend now? (y/n)"
if ($deployFrontend -eq "y") {
    Write-Host "Deploying frontend..." -ForegroundColor Yellow
    fly deploy --config fly.frontend.toml
    
    Write-Host "✅ Frontend deployed!" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Green
Write-Host ""
Write-Host "Your app is now live at:" -ForegroundColor Cyan
Write-Host "  Frontend: https://aptiverse-frontend.fly.dev" -ForegroundColor White
Write-Host "  Backend:  https://aptiverse-backend.fly.dev" -ForegroundColor White
Write-Host "  API Docs: https://aptiverse-backend.fly.dev/docs" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  fly logs --app aptiverse-backend     # View backend logs" -ForegroundColor White
Write-Host "  fly logs --app aptiverse-frontend    # View frontend logs" -ForegroundColor White
Write-Host "  fly ssh console --app aptiverse-backend  # SSH into backend" -ForegroundColor White
Write-Host "  fly postgres connect --app aptiverse-db  # Connect to database" -ForegroundColor White
Write-Host ""
