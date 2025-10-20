@echo off
REM NetShare Pro - Windows Startup Script
REM Automatically requests administrator privileges

echo.
echo ========================================
echo  NetShare Pro - Server Startup
echo ========================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from python.org
    echo.
    pause
    exit /b 1
)

REM Check for admin privileges
net session >nul 2>&1
if errorlevel 1 (
    echo [!] Administrator privileges required for firewall configuration
    echo [!] Right-click this file and select "Run as Administrator"
    echo.
    echo Press any key to continue without admin privileges...
    echo (Network access from other devices may not work)
    pause >nul
)

REM Start the server
echo Starting NetShare Pro server...
echo.
python start_server.py

REM Keep window open if error occurred
if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start
    pause
)
