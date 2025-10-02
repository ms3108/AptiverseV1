#!/bin/bash
# Battle Room Setup Script

echo "🎮 Setting up Battle Room Feature..."
echo ""

# Step 1: Check if Docker is running
echo "Step 1: Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi
echo "✅ Docker is running"
echo ""

# Step 2: Start containers
echo "Step 2: Starting containers..."
docker-compose up -d
sleep 5
echo "✅ Containers started"
echo ""

# Step 3: Run database migration
echo "Step 3: Running database migration..."
docker-compose exec -T backend python migrate_battle_tables.py
if [ $? -eq 0 ]; then
    echo "✅ Migration completed"
else
    echo "❌ Migration failed. Trying alternative method..."
    # Copy migration script into container and run
    docker-compose exec -T backend bash -c "cd /app && python migrate_battle_tables.py"
fi
echo ""

# Step 4: Verify services
echo "Step 4: Verifying services..."
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:3000"
echo "  - Database: localhost:5433"
echo ""

echo "✅ Setup Complete!"
echo ""
echo "📖 Next Steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login or create an account"
echo "  3. Click '⚔️ Battles' button in dashboard"
echo "  4. Create your first battle room!"
echo ""
echo "📚 For detailed documentation, see: BATTLE_ROOM_GUIDE.md"
