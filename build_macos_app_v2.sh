#!/bin/bash

# NetShare Pro - macOS Desktop Application Builder
# Builds standalone .app for macOS using PyInstaller

echo "====================================="
echo "NetShare Pro - macOS Build Script"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if Python is installed
echo -e "${YELLOW}Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo -e "${GREEN}✓ Found: $PYTHON_VERSION${NC}"
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo -e "${RED}✗ Python not found! Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if pip is available
echo -e "${YELLOW}Checking pip...${NC}"
if command -v $PIP_CMD &> /dev/null; then
    echo -e "${GREEN}✓ pip is available${NC}"
else
    echo -e "${RED}✗ pip not found!${NC}"
    exit 1
fi

# Install/upgrade required packages
echo ""
echo -e "${YELLOW}Installing required packages...${NC}"
$PIP_CMD install --upgrade pip
$PIP_CMD install -r requirements.txt
$PIP_CMD install pyinstaller pywebview

# Clean previous builds
echo ""
echo -e "${YELLOW}Cleaning previous builds...${NC}"
rm -rf build dist "NetShare Pro.spec"

# Create application icon (if not exists)
echo -e "${YELLOW}Checking application icon...${NC}"
if [ ! -f "icon.icns" ]; then
    echo -e "${YELLOW}! No icon found, using default${NC}"
    ICON_ARG=""
else
    ICON_ARG="--icon=icon.icns"
fi

# Build with PyInstaller
echo ""
echo -e "${YELLOW}Building macOS application...${NC}"
echo -e "${CYAN}This may take a few minutes...${NC}"

pyinstaller --name="NetShare Pro" \
    --onefile \
    --windowed \
    $ICON_ARG \
    --add-data "templates:templates" \
    --add-data "static:static" \
    --add-data "data:data" \
    --add-data ".env.example:." \
    --hidden-import=flask \
    --hidden-import=flask_cors \
    --hidden-import=eventlet \
    --hidden-import=eventlet.wsgi \
    --hidden-import=socketio \
    --hidden-import=engineio \
    --hidden-import=qrcode \
    --hidden-import=PIL \
    --hidden-import=bcrypt \
    --hidden-import=werkzeug \
    --hidden-import=jinja2 \
    --hidden-import=click \
    --hidden-import=itsdangerous \
    --hidden-import=markupsafe \
    --hidden-import=webview \
    --collect-all flask \
    --collect-all socketio \
    --collect-all eventlet \
    --collect-all engineio \
    --collect-all webview \
    --osx-bundle-identifier com.circuvent.netsharepro \
    desktop_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=====================================${NC}"
    echo -e "${GREEN}✓ Build completed successfully!${NC}"
    echo -e "${GREEN}=====================================${NC}"
    echo ""
    echo -e "${CYAN}Application location:${NC}"
    echo -e "  ${GREEN}dist/NetShare Pro.app${NC}"
    echo ""
    echo -e "${CYAN}To run:${NC}"
    echo -e "  ${GREEN}open dist/NetShare\\ Pro.app${NC}"
    echo ""
    
    # Create distribution package
    echo -e "${YELLOW}Creating distribution package...${NC}"
    
    mkdir -p "NetShare_Pro_macOS"
    cp -r "dist/NetShare Pro.app" "NetShare_Pro_macOS/"
    cp README.md "NetShare_Pro_macOS/" 2>/dev/null || true
    cp .env.example "NetShare_Pro_macOS/" 2>/dev/null || true
    
    # Create README for distribution
    cat > "NetShare_Pro_macOS/INSTALLATION.txt" << 'EOF'
NetShare Pro - macOS Desktop Application
=========================================

Installation:
1. Drag "NetShare Pro.app" to your Applications folder
2. Double-click to run
3. If macOS blocks the app (first run):
   - Go to System Preferences > Security & Privacy
   - Click "Open Anyway"
   - Or right-click the app and select "Open"

Default Login:
- Username: admin
- Password: admin123

Configuration:
- Edit .env file to customize settings
- Data is stored in the 'data' folder
- Uploaded files are stored in 'uploads' folder

Troubleshooting:
- If the application doesn't start, run it from Terminal to see errors
- Make sure port 5001 is not in use
- Check firewall settings if needed

For more information, visit: https://github.com/Hemakotibonthada/Sharing_Tool
EOF
    
    # Create DMG for easier distribution (optional)
    echo ""
    echo -e "${YELLOW}Creating DMG installer...${NC}"
    if command -v hdiutil &> /dev/null; then
        hdiutil create -volname "NetShare Pro" \
            -srcfolder "NetShare_Pro_macOS" \
            -ov -format UDZO \
            "NetShare_Pro_macOS.dmg"
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ DMG created: NetShare_Pro_macOS.dmg${NC}"
        fi
    fi
    
    echo -e "${GREEN}✓ Distribution package created: NetShare_Pro_macOS/${NC}"
    echo ""
    echo -e "${CYAN}You can now distribute:${NC}"
    echo -e "  - NetShare_Pro_macOS folder (contains .app)"
    echo -e "  - NetShare_Pro_macOS.dmg (installer)"
    
else
    echo ""
    echo -e "${RED}✗ Build failed!${NC}"
    echo -e "${YELLOW}Check the errors above for details${NC}"
    exit 1
fi
