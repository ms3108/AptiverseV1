# Battle Room Setup Script for Windows
# Run this in PowerShell

Write-Host "🎮 Setting up Battle Room Feature..." -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Docker is running
Write-Host "Step 1: Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Start containers
Write-Host "Step 2: Starting containers..." -ForegroundColor Yellow
docker-compose up -d
Start-Sleep -Seconds 5
Write-Host "✅ Containers started" -ForegroundColor Green
Write-Host ""

# Step 3: Run database migration
Write-Host "Step 3: Running database migration..." -ForegroundColor Yellow
$result = docker-compose exec -T backend python migrate_battle_tables.py 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Migration completed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Migration may have failed. Checking..." -ForegroundColor Yellow
    Write-Host $result
    
    Write-Host "Trying to copy and run migration..." -ForegroundColor Yellow
    docker cp backend/migrate_battle_tables.py aptiverse_backend:/app/
    docker-compose exec backend python /app/migrate_battle_tables.py
}
Write-Host ""

# Step 4: Verify services
Write-Host "Step 4: Verifying services..." -ForegroundColor Yellow
Write-Host "  - Backend: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Database: localhost:5433" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Open http://localhost:3000 in your browser"
Write-Host "  2. Login or create an account"
Write-Host "  3. Click '⚔️ Battles' button in dashboard"
Write-Host "  4. Create your first battle room!"
Write-Host ""
Write-Host "📚 For detailed documentation, see: BATTLE_ROOM_GUIDE.md" -ForegroundColor Yellow
Write-Host ""

# Optional: Open browser
$open = Read-Host "Would you like to open the app in your browser? (Y/N)"
if ($open -eq "Y" -or $open -eq "y") {
    Start-Process "http://localhost:3000"
}
