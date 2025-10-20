#!/usr/bin/env python3
"""
NetShare Pro - Standalone Launcher
Auto-opens browser and starts server
"""

import os
import sys
import time
import webbrowser
import threading

# Add the bundle directory to path if running from .app
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    os.chdir(bundle_dir)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

# Import the main app
from app import app, high_speed

def open_browser():
    """Open browser after short delay"""
    time.sleep(2)
    print("\n🌐 Opening browser...")
    webbrowser.open('http://localhost:5001')

def main():
    """Main launcher"""
    print("\n" + "="*60)
    print("🚀 NetShare Pro - Starting...")
    print("="*60 + "\n")
    
    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # Start the server
    try:
        high_speed.socketio.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False,
            use_reloader=False,
            log_output=False
        )
    except KeyboardInterrupt:
        print("\n\n👋 NetShare Pro stopped")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
