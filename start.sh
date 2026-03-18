#!/bin/bash
# Data Center Intelligent Site Selection & Energy Optimization - Launch Script (Linux/Mac)

echo "🚀 Starting Data Center Intelligent Site Selection & Energy Optimization"
echo "=================================================="

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env configuration file not found"
    echo "📋 Please run: cp env.example .env"
    echo "📝 Then edit .env and fill in your settings"
    exit 1
fi

# Set proxy if needed
echo "🌐 Setting proxy..."
source .env
if [ ! -z "$HTTP_PROXY" ]; then
    export HTTP_PROXY=$HTTP_PROXY
    export HTTPS_PROXY=$HTTPS_PROXY
    export http_proxy=$http_proxy
    export https_proxy=$https_proxy
    echo "✅ Proxy set: $HTTP_PROXY"
fi

# Start backend service
echo "🔧 Starting backend service..."
python3 start_system.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Verify backend started
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend is running (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend service
echo "🎨 Starting frontend service..."
cd frontend
python3 -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 System started successfully!"
echo "=================================================="
echo "🌐 Access URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API docs:  http://localhost:8000/docs"
echo ""
echo "⏹️  Stop services: press Ctrl+C"
echo "=================================================="

# Trap to stop services
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '✅ Services stopped'; exit 0" INT

# Keep script running
wait
