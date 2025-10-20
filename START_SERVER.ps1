# NetShare Pro - PowerShell Startup Script with Auto-Elevation
# This script will automatically request administrator privileges

param(
    [switch]$Elevated
)

function Test-Admin {
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# If not running as administrator, relaunch with elevation
if (-not (Test-Admin) -and -not $Elevated) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host " Requesting Administrator Privileges" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Administrator access is needed to configure Windows Firewall" -ForegroundColor Yellow
    Write-Host "for network access from other devices." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please click 'Yes' on the UAC prompt..." -ForegroundColor Yellow
    Write-Host ""
    
    Start-Sleep -Seconds 2
    
    try {
        # Relaunch the script with elevation
        $scriptPath = $MyInvocation.MyCommand.Path
        Start-Process powershell.exe -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`" -Elevated" -Verb RunAs
        exit
    }
    catch {
        Write-Host "Failed to elevate privileges. Running without admin access..." -ForegroundColor Red
        Write-Host "Network access from other devices may not work." -ForegroundColor Red
        Write-Host ""
        Start-Sleep -Seconds 3
    }
}

# Clear screen and show banner
Clear-Host
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  🚀 NetShare Pro v2.0 - Advanced File Sharing Server" -ForegroundColor Green
Write-Host "     by Circuvent Technologies" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detected: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "  Please install Python 3.7+ from python.org" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if required dependencies are installed
Write-Host "✓ Checking dependencies..." -ForegroundColor Green

$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $requirementsFile) {
    # Check for Flask
    $flaskCheck = python -c "import flask" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "⚠ Some dependencies are missing. Installing..." -ForegroundColor Yellow
        python -m pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
            Write-Host "  Please run: pip install -r requirements.txt" -ForegroundColor Yellow
            Write-Host ""
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
    else {
        Write-Host "✓ All dependencies are installed" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
Write-Host "🔄 Starting NetShare Pro server..." -ForegroundColor Cyan
Write-Host ""

$serverScript = Join-Path $PSScriptRoot "start_server.py"
if (Test-Path $serverScript) {
    python $serverScript
}
else {
    # Fallback to app.py if start_server.py doesn't exist
    Write-Host "⚠ start_server.py not found, using app.py directly..." -ForegroundColor Yellow
    python app.py
}

# Keep window open if there was an error
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "✗ Server stopped with errors" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
}
