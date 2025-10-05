# Quick Setup Script for Fly.io + Neon.tech Deployment
# Follow the prompts to deploy your Aptiverse app

Write-Host ""
Write-Host "🚀 Aptiverse Deployment: Fly.io + Neon.tech" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This script will help you deploy your app for FREE!" -ForegroundColor Green
Write-Host ""

# Step 1: Neon.tech Setup
Write-Host "📊 STEP 1: Neon.tech Database Setup" -ForegroundColor Yellow
Write-Host "------------------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open your browser: https://neon.tech" -ForegroundColor White
Write-Host "2. Sign up with GitHub" -ForegroundColor White
Write-Host "3. Create a project named: aptiverse-db" -ForegroundColor White
Write-Host "4. Region: Asia Pacific (Singapore)" -ForegroundColor White
Write-Host "5. Copy the connection string" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when you have your Neon.tech connection string ready"

$neonUrl = Read-Host "Paste your Neon.tech connection string"
Write-Host "✅ Database URL saved!" -ForegroundColor Green

# Step 2: Generate SECRET_KEY
Write-Host ""
Write-Host "🔐 STEP 2: Generating Secrets" -ForegroundColor Yellow
Write-Host "-----------------------------" -ForegroundColor Yellow
Write-Host "Generating SECRET_KEY..." -ForegroundColor White

$secretKey = python -c "import secrets; print(secrets.token_hex(32))"
Write-Host "✅ SECRET_KEY generated: $secretKey" -ForegroundColor Green

# Step 3: Deploy Backend
Write-Host ""
Write-Host "🚀 STEP 3: Deploy Backend to Fly.io" -ForegroundColor Yellow
Write-Host "-----------------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: In your browser (Fly.io deployment page):" -ForegroundColor Red
Write-Host ""
Write-Host "1. In 'Databases - Postgres' section:" -ForegroundColor White
Write-Host "   - Provider: Select 'none'" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. In 'Secrets' section, add these 7 secrets:" -ForegroundColor White
Write-Host ""
Write-Host "   Secret 1:" -ForegroundColor Cyan
Write-Host "   Name: DATABASE_URL" -ForegroundColor White
Write-Host "   Value: $neonUrl" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 2:" -ForegroundColor Cyan
Write-Host "   Name: SECRET_KEY" -ForegroundColor White
Write-Host "   Value: $secretKey" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 3:" -ForegroundColor Cyan
Write-Host "   Name: GMAIL_USER" -ForegroundColor White
Write-Host "   Value: misna5984@gmail.com" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 4:" -ForegroundColor Cyan
Write-Host "   Name: GMAIL_APP_PASSWORD" -ForegroundColor White
Write-Host "   Value: rbhbbehowdofefkj" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 5:" -ForegroundColor Cyan
Write-Host "   Name: FRONTEND_URL" -ForegroundColor White
Write-Host "   Value: https://aptiverse-frontend.fly.dev" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 6:" -ForegroundColor Cyan
Write-Host "   Name: ALGORITHM" -ForegroundColor White
Write-Host "   Value: HS256" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 7:" -ForegroundColor Cyan
Write-Host "   Name: ACCESS_TOKEN_EXPIRE_MINUTES" -ForegroundColor White
Write-Host "   Value: 30" -ForegroundColor Gray
Write-Host ""
Write-Host "   Secret 8 (Optional):" -ForegroundColor Cyan
Write-Host "   Name: WEAVIATE_URL" -ForegroundColor White
Write-Host "   Value: http://localhost:8080" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Click 'Deploy' button at the bottom" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter once backend deployment is complete"

Write-Host "✅ Backend should now be live!" -ForegroundColor Green
Write-Host "   URL: https://aptiverse-backend.fly.dev" -ForegroundColor Cyan

# Step 4: Seed Database
Write-Host ""
Write-Host "🌱 STEP 4: Seed Database" -ForegroundColor Yellow
Write-Host "------------------------" -ForegroundColor Yellow
Write-Host ""
$seedNow = Read-Host "Do you want to seed the database now? (y/n)"

if ($seedNow -eq "y") {
    Write-Host ""
    Write-Host "Opening SSH console to backend..." -ForegroundColor White
    Write-Host "Once inside, run these commands:" -ForegroundColor Yellow
    Write-Host "  cd backend" -ForegroundColor Cyan
    Write-Host "  python seed_data.py" -ForegroundColor Cyan
    Write-Host "  python create_admin.py" -ForegroundColor Cyan
    Write-Host "  exit" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "Press Enter to open SSH console"
    
    fly ssh console --app aptiverse-backend
    
    Write-Host "✅ Database seeded!" -ForegroundColor Green
}

# Step 5: Deploy Frontend
Write-Host ""
Write-Host "🌐 STEP 5: Deploy Frontend" -ForegroundColor Yellow
Write-Host "--------------------------" -ForegroundColor Yellow
Write-Host ""
$deployFrontend = Read-Host "Deploy frontend now? (y/n)"

if ($deployFrontend -eq "y") {
    Write-Host "Deploying frontend to Fly.io..." -ForegroundColor White
    fly deploy --config fly.frontend.toml
    
    Write-Host "✅ Frontend deployed!" -ForegroundColor Green
    
    # Update CORS
    Write-Host ""
    Write-Host "Updating backend CORS settings..." -ForegroundColor White
    fly secrets set FRONTEND_URL="https://aptiverse-frontend.fly.dev" --app aptiverse-backend
    
    Write-Host "✅ CORS updated!" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green
Write-Host ""
Write-Host "Your app is now live at:" -ForegroundColor Cyan
Write-Host "  Frontend:  https://aptiverse-frontend.fly.dev" -ForegroundColor White
Write-Host "  Backend:   https://aptiverse-backend.fly.dev" -ForegroundColor White
Write-Host "  API Docs:  https://aptiverse-backend.fly.dev/docs" -ForegroundColor White
Write-Host "  Database:  Neon.tech dashboard" -ForegroundColor White
Write-Host ""
Write-Host "Total Cost: $0/month! 🎉" -ForegroundColor Green
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Yellow
Write-Host "  fly logs --app aptiverse-backend     # View backend logs" -ForegroundColor White
Write-Host "  fly logs --app aptiverse-frontend    # View frontend logs" -ForegroundColor White
Write-Host "  fly ssh console --app aptiverse-backend  # SSH into backend" -ForegroundColor White
Write-Host ""
Write-Host "For detailed docs, see: FLY_NEON_DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host ""
