@echo off
REM NetShare Pro - Quick Start Script for Windows
REM This script installs dependencies and runs the desktop application

echo ========================================
echo NetShare Pro - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Python found
python --version

REM Check if requirements.txt exists
if not exist requirements.txt (
    echo ERROR: requirements.txt not found
    echo Please make sure you're running this from the FileShare directory
    pause
    exit /b 1
)

echo.
echo [2/3] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Try running: pip install --user -r requirements.txt
    pause
    exit /b 1
)

echo.
echo [3/3] Starting NetShare Pro...
echo.
echo ========================================
echo The application will open in your browser
echo Default login: admin / admin123
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python desktop_app.py

pause
