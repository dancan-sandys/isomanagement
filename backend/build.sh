#!/bin/bash
set -e

echo "🚀 Starting ISO 22000 FSMS backend build..."

# Upgrade pip and setuptools first
echo "📦 Upgrading pip and build tools..."
python -m pip install --upgrade pip setuptools wheel

# Install requirements
echo "📋 Installing requirements..."
if [ -f "requirements-production.txt" ]; then
    echo "Using production requirements..."
    pip install -r requirements-production.txt
else
    echo "Using standard requirements..."
    pip install -r requirements.txt
fi

# Try to install pandas if build environment supports it
echo "🐼 Attempting to install pandas (optional)..."
pip install --only-binary=:all: "pandas>=2.0.0,<3.0.0" || echo "⚠️  Pandas installation failed - continuing without pandas (export features will use fallback)"

echo "✅ Build completed successfully!"