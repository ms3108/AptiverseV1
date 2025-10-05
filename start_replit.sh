#!/bin/bash

# Replit Startup Script for Aptiverse
# This script sets up and runs both frontend and backend

set -e  # Exit on error

echo "========================================="
echo "   Starting Aptiverse on Replit"
echo "========================================="
echo ""

# Navigate to backend
cd backend

echo "📦 Installing backend dependencies..."
pip install -q -r requirements.txt

echo "🗄️  Setting up database..."
python3 -c "
from database import engine
from models import Base
try:
    Base.metadata.create_all(bind=engine)
    print('✅ Database tables created!')
except Exception as e:
    print(f'⚠️  Database setup: {e}')
"

# Seed data only once
if [ ! -f ".seeded" ]; then
    echo "🌱 Seeding database with initial data..."
    python3 seed_data.py || echo "⚠️  Seeding: May already be seeded"
    python3 create_admin.py || echo "⚠️  Admin: May already exist"
    touch .seeded
    echo "✅ Database seeded!"
else
    echo "✓ Database already seeded, skipping..."
fi

echo ""
echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend running (PID: $BACKEND_PID)"

# Navigate to frontend
cd ../frontend

echo ""
echo "📦 Installing frontend dependencies..."
npm install --silent

# Build frontend if build folder doesn't exist or is outdated
if [ ! -d "build" ] || [ "package.json" -nt "build" ]; then
    echo "🔨 Building React frontend..."
    npm run build
    echo "✅ Frontend built!"
else
    echo "✓ Frontend already built, skipping..."
fi

echo ""
echo "🌐 Starting frontend server on port 3000..."
npx serve -s build -l 3000 &
FRONTEND_PID=$!
echo "✅ Frontend running (PID: $FRONTEND_PID)"

echo ""
echo "========================================="
echo "   🎉 Aptiverse is Ready!"
echo "========================================="
echo ""
echo "📍 Frontend: https://${REPL_SLUG}.${REPL_OWNER}.repl.co"
echo "📍 Backend API: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:8000"
echo "📍 API Docs: https://${REPL_SLUG}.${REPL_OWNER}.repl.co:8000/docs"
echo ""
echo "========================================="

# Keep the script running and wait for both processes
wait $BACKEND_PID $FRONTEND_PID
