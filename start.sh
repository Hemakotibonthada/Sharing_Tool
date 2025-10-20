#!/bin/bash
# NetShare Pro - Quick Start Script for macOS/Linux
# This script installs dependencies and runs the desktop application

echo "========================================"
echo "NetShare Pro - Quick Start"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo -e "${RED}ERROR: Python is not installed${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo -e "${GREEN}[1/3] Python found${NC}"
$PYTHON_CMD --version

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo -e "${RED}ERROR: requirements.txt not found${NC}"
    echo "Please make sure you're running this from the FileShare directory"
    exit 1
fi

echo ""
echo -e "${YELLOW}[2/3] Installing dependencies...${NC}"
echo "This may take a few minutes..."
$PIP_CMD install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}ERROR: Failed to install dependencies${NC}"
    echo "Try running: $PIP_CMD install --user -r requirements.txt"
    exit 1
fi

echo ""
echo -e "${YELLOW}[3/3] Starting NetShare Pro...${NC}"
echo ""
echo "========================================"
echo "The application will open in your browser"
echo "Default login: admin / admin123"
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

$PYTHON_CMD desktop_app.py
