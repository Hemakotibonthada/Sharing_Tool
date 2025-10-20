#!/usr/bin/env python3
"""
NetShare Pro - Enhanced Server Startup Script
Includes firewall configuration and network diagnostics
"""

import os
import sys
import socket
import subprocess
import platform

def check_port_available(port=5001):
    """Check if port is available"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0  # Port is available if connection failed
    except:
        return True

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def configure_windows_firewall(port=5001):
    """Configure Windows Firewall to allow the port"""
    if platform.system() != 'Windows':
        return True
    
    print(f"\n🔥 Configuring Windows Firewall for port {port}...")
    
    try:
        # Remove existing rule if it exists
        subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
            'name=NetShare Pro'
        ], capture_output=True, shell=True)
        
        # Add new firewall rule
        result = subprocess.run([
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            'name=NetShare Pro',
            'dir=in',
            'action=allow',
            'protocol=TCP',
            f'localport={port}',
            'profile=private,public',
            'description=NetShare Pro File Sharing Server'
        ], capture_output=True, shell=True)
        
        if result.returncode == 0:
            print(f"✓ Firewall rule added successfully")
            return True
        else:
            print(f"⚠ Could not add firewall rule automatically")
            print(f"  You may need to run this script as Administrator")
            print(f"  Or manually allow port {port} in Windows Firewall")
            return False
    except Exception as e:
        print(f"⚠ Firewall configuration failed: {e}")
        return False

def check_network():
    """Check network connectivity"""
    print("\n🌐 Network Diagnostics:")
    
    local_ip = get_local_ip()
    print(f"  • Local IP: {local_ip}")
    
    try:
        hostname = socket.gethostname()
        print(f"  • Hostname: {hostname}")
    except:
        print(f"  • Hostname: Unable to determine")
    
    # Check if we're on a real network (not just localhost)
    if local_ip.startswith('127.'):
        print(f"  ⚠ WARNING: Only localhost IP detected")
        print(f"    Make sure you're connected to a network (Wi-Fi/Ethernet)")
    elif local_ip.startswith('169.254.'):
        print(f"  ⚠ WARNING: APIPA address detected (no DHCP)")
        print(f"    Check your network connection")
    else:
        print(f"  ✓ Valid network connection detected")
    
    return local_ip

def print_startup_banner(local_ip, port=5001):
    """Print startup information"""
    print("\n" + "="*70)
    print("🚀 NetShare Pro v2.0 - Advanced File Sharing Server")
    print("   by Circuvent Technologies")
    print("="*70)
    print(f"\n📍 SERVER ADDRESSES:")
    print(f"   • Local access:   http://localhost:{port}")
    print(f"   • Network access: http://{local_ip}:{port}")
    print(f"\n📱 MOBILE/OTHER DEVICES:")
    print(f"   1. Connect to the same Wi-Fi network")
    print(f"   2. Open browser and go to: http://{local_ip}:{port}")
    print(f"   3. Or scan the QR code shown in the Network tab")
    print(f"\n💡 TROUBLESHOOTING:")
    print(f"   • Can't connect from another device?")
    print(f"     → Check Windows Firewall settings")
    print(f"     → Make sure devices are on the same network")
    print(f"     → Try disabling VPN if active")
    print(f"   • Server won't start?")
    print(f"     → Port {port} may be in use by another application")
    print(f"     → Try closing other web servers and restart")
    print("="*70)
    print()

def main():
    """Main startup function"""
    port = 5001
    
    print("\n🚀 Starting NetShare Pro Server...")
    print("="*70)
    
    # Check if port is available
    if not check_port_available(port):
        print(f"\n✗ ERROR: Port {port} is already in use!")
        print(f"  Another application may be using this port.")
        print(f"  Please close it and try again.\n")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Check network
    local_ip = check_network()
    
    # Configure firewall (Windows only)
    if platform.system() == 'Windows':
        print("\n" + "="*70)
        print("🔒 IMPORTANT: Administrator Access Required")
        print("="*70)
        print("\nTo allow network access from other devices, this script needs to")
        print("configure Windows Firewall.")
        print("\nIf you see a UAC prompt, please click 'Yes' to allow.")
        print("\nIf the firewall rule cannot be added automatically:")
        print("  1. Open Windows Defender Firewall")
        print("  2. Click 'Advanced settings'")
        print("  3. Click 'Inbound Rules' → 'New Rule'")
        print("  4. Select 'Port' → Next")
        print(f"  5. Enter port number: {port}")
        print("  6. Allow the connection → Finish")
        
        input("\nPress Enter to continue...")
        configure_windows_firewall(port)
    
    # Print startup banner
    print_startup_banner(local_ip, port)
    
    # Start the server
    print("🔄 Starting server...\n")
    
    try:
        # Import app after all checks
        from app import app, high_speed
        
        # Start server with SocketIO
        high_speed.socketio.run(
            app,
            host='0.0.0.0',
            port=port,
            debug=False,
            use_reloader=False,
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except ImportError as e:
        print(f"\n✗ ERROR: Missing dependencies!")
        print(f"  {e}")
        print(f"\n  Please run: pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print(f"\n  Check the error message above for details.")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == '__main__':
    main()
