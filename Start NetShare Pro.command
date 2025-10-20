#!/bin/bash

# NetShare Pro - Quick Launcher
# Double-click this file to start NetShare Pro

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Clear screen
clear

echo "=================================================="
echo "🚀 NetShare Pro - File Sharing Server"
echo "=================================================="
echo ""
echo "Starting server..."
echo ""

# Create necessary directories
mkdir -p shared_files file_versions data

# Open browser after 3 seconds
(sleep 3 && open http://localhost:5001) &

# Start the server
python3 app.py

# Keep terminal open if there's an error
echo ""
echo "Press any key to exit..."
read -n 1
