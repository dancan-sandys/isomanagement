#!/bin/bash

# Deployment script for ISO 22000 FSMS Backend
# This script helps set up the backend on a VM

echo "🚀 Starting ISO 22000 FSMS Backend Deployment..."

# Check if Python 3.8+ is installed
python3 --version || {
    echo "❌ Python 3.8+ is required but not installed"
    exit 1
}

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
echo "📥 Installing production dependencies..."
pip install -r requirements-production.txt

# Create database directory if it doesn't exist
mkdir -p uploads/documents
mkdir -p uploads/avatars

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Create initial admin user if needed
echo "👤 Creating initial admin user..."
python create_test_user_simple.py

echo "✅ Deployment completed successfully!"
echo ""
echo "🎯 To start the server, run:"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --host=0.0.0.0 --port=8000"
echo ""
echo "🌐 The API will be available at: http://your-vm-ip:8000"
echo "📚 API documentation at: http://your-vm-ip:8000/docs" 