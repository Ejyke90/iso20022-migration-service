#!/bin/bash

echo "🚀 Starting Word to PDF Web Application"
echo "========================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Install API dependencies if needed
echo "📦 Installing API dependencies..."
pip install -q -r api/requirements.txt

# Start Flask API in background
echo "🔧 Starting Flask API server on port 5000..."
python api/server.py &
API_PID=$!

# Wait for API to start
sleep 2

# Check if web-app node_modules exists
if [ ! -d "web-app/node_modules" ]; then
    echo "📦 Installing frontend dependencies (this may take a minute)..."
    cd web-app
    npm install
    cd ..
fi

# Start Next.js frontend
echo "🎨 Starting Next.js frontend on port 3000..."
cd web-app
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Application started successfully!"
echo "========================================"
echo "📍 Frontend: http://localhost:3000"
echo "📍 API: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping servers...'; kill $API_PID $FRONTEND_PID; exit" INT
wait
