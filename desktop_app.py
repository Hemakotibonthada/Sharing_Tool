"""
NetShare Pro - Desktop Application
Runs Flask server and opens in a native window
Works on Windows and macOS
"""

import sys
import os
import threading
import time
import webbrowser
from pathlib import Path

# Determine if we're running as a PyInstaller bundle
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    application_path = sys._MEIPASS
else:
    # Running as script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Add application path to system path
sys.path.insert(0, application_path)

# Set working directory
os.chdir(application_path)

def setup_environment():
    """Setup environment for desktop application"""
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Set environment variables for desktop mode
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DESKTOP_MODE'] = '1'
    
    # Create .env file if it doesn't exist
    env_file = Path('.env')
    if not env_file.exists():
        import secrets
        with open(env_file, 'w') as f:
            f.write(f'SECRET_KEY={secrets.token_hex(32)}\n')
            f.write('FLASK_ENV=production\n')
            f.write('HOST=127.0.0.1\n')
            f.write('PORT=5001\n')
            f.write('DEBUG=False\n')

def find_free_port(start_port=5001, max_attempts=10):
    """Find a free port to run the server"""
    import socket
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port

def run_flask_server(port):
    """Run Flask server in background thread"""
    try:
        # Import app after setting up environment
        from app import app
        
        # Configure app for desktop mode
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.config['TEMPLATES_AUTO_RELOAD'] = False
        
        # Run server
        print(f"Starting NetShare Pro server on port {port}...")
        app.run(host='127.0.0.1', port=port, debug=False, threaded=True, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

def open_browser(port, max_attempts=30):
    """Wait for server to start and open browser"""
    import socket
    import urllib.request
    
    url = f'http://127.0.0.1:{port}'
    
    # Wait for server to be ready
    for i in range(max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                # Server is up, try to access it
                try:
                    urllib.request.urlopen(url, timeout=2)
                    print(f"Server is ready at {url}")
                    break
                except:
                    pass
        except:
            pass
        
        time.sleep(0.5)
    
    # Open in browser
    print(f"Opening NetShare Pro at {url}")
    webbrowser.open(url)

def create_window_webview(port):
    """Create a native window using webview (if available)"""
    try:
        import webview
        
        url = f'http://127.0.0.1:{port}'
        
        # Wait a bit for server to start
        time.sleep(2)
        
        # Create window
        window = webview.create_window(
            'NetShare Pro',
            url,
            width=1280,
            height=800,
            resizable=True,
            fullscreen=False,
            min_size=(800, 600)
        )
        
        webview.start()
        
    except ImportError:
        print("pywebview not available, using browser instead")
        open_browser(port)
    except Exception as e:
        print(f"Error creating window: {e}")
        open_browser(port)

def create_window_pyqt(port):
    """Create a native window using PyQt5 (if available)"""
    try:
        from PyQt5.QtCore import QUrl, Qt
        from PyQt5.QtWidgets import QApplication, QMainWindow
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        
        class NetShareWindow(QMainWindow):
            def __init__(self, url):
                super().__init__()
                self.setWindowTitle('NetShare Pro')
                self.setGeometry(100, 100, 1280, 800)
                
                # Create web view
                self.browser = QWebEngineView()
                self.browser.setUrl(QUrl(url))
                
                self.setCentralWidget(self.browser)
        
        # Wait for server to start
        time.sleep(2)
        
        app = QApplication(sys.argv)
        window = NetShareWindow(f'http://127.0.0.1:{port}')
        window.show()
        sys.exit(app.exec_())
        
    except ImportError:
        print("PyQt5 not available, trying webview")
        create_window_webview(port)
    except Exception as e:
        print(f"Error creating PyQt window: {e}")
        create_window_webview(port)

def main():
    """Main entry point for desktop application"""
    print("=" * 50)
    print("NetShare Pro - Desktop Application")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Find free port
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Start Flask server in background thread
    server_thread = threading.Thread(target=run_flask_server, args=(port,), daemon=True)
    server_thread.start()
    
    # Give server a moment to start
    time.sleep(1)
    
    # Try to create native window, fallback to browser
    try:
        # Check platform and available libraries
        if sys.platform == 'darwin':
            # macOS - prefer webview
            create_window_webview(port)
        elif sys.platform == 'win32':
            # Windows - try PyQt5 first, then webview
            create_window_pyqt(port)
        else:
            # Linux or other - use webview
            create_window_webview(port)
    except KeyboardInterrupt:
        print("\nShutting down NetShare Pro...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        print("Opening in browser as fallback...")
        open_browser(port)
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down NetShare Pro...")
            sys.exit(0)

if __name__ == '__main__':
    main()
