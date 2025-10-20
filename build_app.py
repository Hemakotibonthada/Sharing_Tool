#!/usr/bin/env python3
"""
Build NetShare Pro as a standalone macOS application
Creates a .app bundle that can be double-clicked to run
"""

import os
import sys
import subprocess
import shutil

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✓ PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installed")

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('data', 'data'),
        ('auth_system.py', '.'),
        ('high_speed_transfer.py', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'flask',
        'flask_socketio',
        'eventlet',
        'eventlet.wsgi',
        'eventlet.green',
        'dns',
        'dns.dnssec',
        'dns.e164',
        'dns.hash',
        'dns.namedict',
        'dns.tsigkeyring',
        'dns.update',
        'dns.version',
        'dns.zone',
        'engineio',
        'socketio',
        'qrcode',
        'PIL',
        'werkzeug',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'jupyter'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='NetSharePro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='NetSharePro',
)

app = BUNDLE(
    coll,
    name='NetSharePro.app',
    icon=None,
    bundle_identifier='com.circuvent.netshare',
    info_plist={
        'CFBundleName': 'NetShare Pro',
        'CFBundleDisplayName': 'NetShare Pro',
        'CFBundleGetInfoString': 'Advanced File Sharing',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0',
        'NSHighResolutionCapable': 'True',
    },
)
'''
    with open('NetSharePro.spec', 'w') as f:
        f.write(spec_content)
    print("✓ Created NetSharePro.spec")

def build_app():
    """Build the application using PyInstaller"""
    print("\n🔨 Building NetShare Pro application...")
    print("This may take a few minutes...\n")
    
    try:
        subprocess.check_call([
            'pyinstaller',
            '--clean',
            '--noconfirm',
            'NetSharePro.spec'
        ])
        print("\n✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Build failed: {e}")
        return False

def create_launcher_script():
    """Create a simple launcher script for non-app bundle"""
    launcher_content = '''#!/bin/bash
cd "$(dirname "$0")"
./NetSharePro/NetSharePro
'''
    with open('run_netshare.command', 'w') as f:
        f.write(launcher_content)
    os.chmod('run_netshare.command', 0o755)
    print("✓ Created launcher script: run_netshare.command")

def print_instructions():
    """Print usage instructions"""
    print("\n" + "="*60)
    print("🎉 BUILD COMPLETE!")
    print("="*60)
    print("\n📦 Your standalone application is ready!\n")
    print("Location: dist/NetSharePro.app")
    print("\n🚀 To run:\n")
    print("   Option 1: Double-click 'NetSharePro.app' in the dist folder")
    print("   Option 2: Run from terminal: open dist/NetSharePro.app")
    print("   Option 3: Double-click 'run_netshare.command'\n")
    print("The application will:")
    print("  • Start the file sharing server automatically")
    print("  • Open your browser to http://localhost:5001")
    print("  • Be accessible from any device on your network")
    print("\n💡 Tip: You can move NetSharePro.app to your Applications folder")
    print("="*60 + "\n")

def main():
    """Main build process"""
    print("\n" + "="*60)
    print("🚀 NetShare Pro - Standalone App Builder")
    print("="*60 + "\n")
    
    # Check if we're in the right directory
    if not os.path.exists('app.py'):
        print("✗ Error: app.py not found!")
        print("  Please run this script from the Sharing directory")
        sys.exit(1)
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Create spec file
    create_spec_file()
    
    # Build the app
    if not build_app():
        sys.exit(1)
    
    # Create launcher script
    create_launcher_script()
    
    # Print instructions
    print_instructions()

if __name__ == '__main__':
    main()
