#!/bin/bash
# Data Center Intelligent Site Selection and Energy Optimization System - One-click Installation Script (Linux/Mac)

echo "🚀 Data Center Intelligent Site Selection and Energy Optimization System - Installation Script"
echo "=================================================="

# Check Python version
echo "🔍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3 is not installed, please install Python 3.8+ first"
    exit 1
fi

# Check Node.js version
echo "🔍 Checking Node.js version..."
node --version
if [ $? -ne 0 ]; then
    echo "❌ Node.js is not installed, please install Node.js 16+ first"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Python dependency installation failed"
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ Frontend dependency installation failed"
    exit 1
fi

# Build frontend
echo "🔨 Building frontend..."
npm run build
if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed"
    exit 1
fi

cd ..

# Copy environment configuration file
echo "📋 Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "✅ Created .env configuration file"
    echo "⚠️  Please edit the .env file and fill in your API keys and configuration"
else
    echo "✅ .env configuration file already exists"
fi

echo ""
echo "🎉 Installation complete!"
echo "=================================================="
echo "📋 Next steps:"
echo "1. Edit the .env file and fill in your configuration"
echo "2. Run python setup_gee_auth.py to set up GEE authentication"
echo "3. Run ./start.sh to start the system"
echo "=================================================="