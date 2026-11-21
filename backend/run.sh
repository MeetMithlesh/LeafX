#!/bin/bash

# AgroScan AI Backend Startup Script for macOS/Linux

echo ""
echo "==============================================="
echo "  AgroScan AI - Plant Disease Detection"
echo "  Backend Server"
echo "==============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed"
    echo "Please install Python 3.8+ using:"
    echo "  macOS: brew install python@3.11"
    echo "  Ubuntu/Debian: sudo apt-get install python3"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "[INFO] Found Python $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "[ACTION] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "[ACTION] Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "[ACTION] Checking dependencies..."
if ! pip list | grep -q fastapi; then
    echo "[ACTION] Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to install dependencies"
        exit 1
    fi
fi

# Validate setup
echo "[ACTION] Validating setup..."
python3 validate_setup.py
VALIDATE_RESULT=$?

if [ $VALIDATE_RESULT -ne 0 ]; then
    echo ""
    echo "[WARNING] Some setup checks failed"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the server
echo ""
echo "[ACTION] Starting AgroScan AI Backend..."
echo ""
echo "==============================================="
echo "  Server: http://localhost:8000"
echo "  Docs:   http://localhost:8000/docs"
echo "==============================================="
echo ""

python3 main.py

# If script exits, show message
echo ""
echo "[INFO] Backend server stopped"
