# NetShare Pro - Windows Desktop Application Builder
# Builds standalone .exe for Windows using PyInstaller

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "NetShare Pro - Windows Build Script" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check if pip is available
Write-Host "Checking pip..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✓ pip is available" -ForegroundColor Green
} catch {
    Write-Host "✗ pip not found!" -ForegroundColor Red
    exit 1
}

# Install/upgrade required packages
Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller pywebview pyqt5 pyqtwebengine

# Clean previous builds
Write-Host ""
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "NetShare_Pro.spec") { Remove-Item -Force "NetShare_Pro.spec" }

# Create application icon (if not exists)
Write-Host "Checking application icon..." -ForegroundColor Yellow
if (-not (Test-Path "icon.ico")) {
    Write-Host "! No icon found, using default" -ForegroundColor Yellow
}

# Build with PyInstaller
Write-Host ""
Write-Host "Building Windows application..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray

$iconArg = ""
if (Test-Path "icon.ico") {
    $iconArg = "--icon=icon.ico"
}

pyinstaller --name="NetShare Pro" `
    --onefile `
    --windowed `
    $iconArg `
    --add-data "templates;templates" `
    --add-data "static;static" `
    --add-data "data;data" `
    --add-data ".env.example;." `
    --hidden-import=flask `
    --hidden-import=flask_cors `
    --hidden-import=eventlet `
    --hidden-import=eventlet.wsgi `
    --hidden-import=socketio `
    --hidden-import=engineio `
    --hidden-import=qrcode `
    --hidden-import=PIL `
    --hidden-import=bcrypt `
    --hidden-import=werkzeug `
    --hidden-import=jinja2 `
    --hidden-import=click `
    --hidden-import=itsdangerous `
    --hidden-import=markupsafe `
    --hidden-import=webview `
    --hidden-import=PyQt5 `
    --hidden-import=PyQt5.QtWebEngineWidgets `
    --collect-all flask `
    --collect-all socketio `
    --collect-all eventlet `
    --collect-all engineio `
    --collect-all webview `
    desktop_app.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host "✓ Build completed successfully!" -ForegroundColor Green
    Write-Host "=====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application location:" -ForegroundColor Cyan
    Write-Host "  dist\NetShare Pro.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "To run:" -ForegroundColor Cyan
    Write-Host "  .\dist\NetShare Pro.exe" -ForegroundColor White
    Write-Host ""
    
    # Create shortcuts and distribution folder
    Write-Host "Creating distribution package..." -ForegroundColor Yellow
    
    if (-not (Test-Path "NetShare_Pro_Windows")) {
        New-Item -ItemType Directory -Path "NetShare_Pro_Windows" | Out-Null
    }
    
    Copy-Item "dist\NetShare Pro.exe" "NetShare_Pro_Windows\"
    Copy-Item "README.md" "NetShare_Pro_Windows\" -ErrorAction SilentlyContinue
    Copy-Item ".env.example" "NetShare_Pro_Windows\" -ErrorAction SilentlyContinue
    
    # Create README for distribution
    @"
NetShare Pro - Windows Desktop Application
==========================================

Installation:
1. Simply run "NetShare Pro.exe"
2. The application will start automatically
3. A browser window will open with NetShare Pro

Default Login:
- Username: admin
- Password: admin123

Configuration:
- Edit .env file to customize settings
- Data is stored in the 'data' folder
- Uploaded files are stored in 'uploads' folder

Troubleshooting:
- If the application doesn't start, run it from command line to see errors
- Make sure port 5001 is not in use
- Check firewall settings if needed

For more information, visit: https://github.com/Hemakotibonthada/Sharing_Tool
"@ | Out-File -FilePath "NetShare_Pro_Windows\INSTALLATION.txt" -Encoding UTF8
    
    Write-Host "✓ Distribution package created: NetShare_Pro_Windows\" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now distribute the NetShare_Pro_Windows folder" -ForegroundColor Cyan
    
} else {
    Write-Host ""
    Write-Host "✗ Build failed!" -ForegroundColor Red
    Write-Host "Check the errors above for details" -ForegroundColor Yellow
    exit 1
}
