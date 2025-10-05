# Fly.io Frontend Deployment Script

Write-Host ""
Write-Host "🌐 Deploying Frontend to Fly.io" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if fly CLI is installed
if (!(Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Fly CLI not found. Please install it first." -ForegroundColor Red
    exit
}

# Check if logged in
$authStatus = fly auth whoami 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Not logged in to Fly.io" -ForegroundColor Red
    fly auth login
}

# Check if app exists
Write-Host "Checking if aptiverse-frontend app exists..." -ForegroundColor Yellow
$appExists = fly status --app aptiverse-frontend 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ App exists, will update it" -ForegroundColor Green
} else {
    Write-Host "Creating new app: aptiverse-frontend" -ForegroundColor Yellow
    fly apps create aptiverse-frontend --org personal
}

Write-Host ""

# Deploy frontend using Docker
Write-Host "🐳 Deploying frontend with Docker..." -ForegroundColor Cyan
Write-Host ""

fly deploy --app aptiverse-frontend --config fly.frontend.toml --dockerfile Dockerfile.frontend --strategy immediate

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "🎉 Frontend Deployed Successfully!" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Frontend URL: https://aptiverse-frontend.fly.dev" -ForegroundColor Cyan
    Write-Host ""
    
    # Update backend CORS
    Write-Host "Updating backend CORS..." -ForegroundColor Yellow
    fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
    
    Write-Host ""
    Write-Host "✅ Deployment Complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your app is live at:" -ForegroundColor Cyan
    Write-Host "  Frontend: https://aptiverse-frontend.fly.dev" -ForegroundColor White
    Write-Host "  Backend:  https://aptiverse-backend.fly.dev" -ForegroundColor White
    Write-Host "  API Docs: https://aptiverse-backend.fly.dev/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed. Check logs:" -ForegroundColor Red
    Write-Host "   fly logs --app aptiverse-frontend" -ForegroundColor Yellow
}

Write-Host ""
