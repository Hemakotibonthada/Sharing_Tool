#!/bin/bash

# NetShare Pro - macOS App Builder
# Creates a standalone .app bundle

echo "=================================================="
echo "🚀 NetShare Pro - macOS App Builder"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "✗ Error: app.py not found!"
    echo "  Please run this script from the Sharing directory"
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install --upgrade pip > /dev/null 2>&1
pip3 install pyinstaller > /dev/null 2>&1
pip3 install -r requirements.txt > /dev/null 2>&1

echo "✓ Dependencies installed"
echo ""

# Create the .app bundle structure
APP_NAME="NetSharePro"
APP_DIR="dist/${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

echo "🔨 Creating app bundle structure..."

# Clean previous build
rm -rf dist build *.spec

# Create directories
mkdir -p "${MACOS_DIR}"
mkdir -p "${RESOURCES_DIR}"

# Copy all necessary files to Resources
echo "📂 Copying files..."
cp -r templates "${RESOURCES_DIR}/"
cp -r static "${RESOURCES_DIR}/"
cp -r data "${RESOURCES_DIR}/"
cp app.py "${RESOURCES_DIR}/"
cp auth_system.py "${RESOURCES_DIR}/"
cp high_speed_transfer.py "${RESOURCES_DIR}/"
cp requirements.txt "${RESOURCES_DIR}/"

# Create the main executable script
cat > "${MACOS_DIR}/${APP_NAME}" << 'EOFEXEC'
#!/bin/bash

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RESOURCES="${DIR}/../Resources"

# Change to resources directory
cd "${RESOURCES}"

# Create necessary directories if they don't exist
mkdir -p shared_files
mkdir -p file_versions
mkdir -p data

# Get Python path
PYTHON=$(which python3)

# Check if Python is available
if [ -z "$PYTHON" ]; then
    osascript -e 'display alert "Python 3 Required" message "Please install Python 3 from python.org" as critical'
    exit 1
fi

# Start the server
echo "Starting NetShare Pro..."
echo "Open http://localhost:5001 in your browser"

# Open browser after 2 seconds in background
(sleep 2 && open http://localhost:5001) &

# Run the app
exec $PYTHON app.py
EOFEXEC

chmod +x "${MACOS_DIR}/${APP_NAME}"

# Create Info.plist
cat > "${CONTENTS_DIR}/Info.plist" << 'EOFPLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>NetSharePro</string>
    <key>CFBundleIdentifier</key>
    <string>com.circuvent.netshare</string>
    <key>CFBundleName</key>
    <string>NetShare Pro</string>
    <key>CFBundleDisplayName</key>
    <string>NetShare Pro</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>
EOFPLIST

echo "✓ App bundle created"
echo ""

echo "=================================================="
echo "🎉 BUILD COMPLETE!"
echo "=================================================="
echo ""
echo "📦 Your app is ready: dist/NetSharePro.app"
echo ""
echo "🚀 To run:"
echo "   • Double-click NetSharePro.app in the dist folder"
echo "   • Or drag it to your Applications folder first"
echo ""
echo "The app will:"
echo "  ✓ Start the file sharing server"
echo "  ✓ Auto-open your browser to http://localhost:5001"
echo "  ✓ Be accessible from any device on your network"
echo ""
echo "💡 Note: Make sure Python 3 is installed on your Mac"
echo "=================================================="
echo ""
