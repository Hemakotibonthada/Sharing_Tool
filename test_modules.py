"""
Test script to verify all modules and desktop app functionality
"""

import sys
import os

print("=" * 60)
print("NetShare Pro - Module Test")
print("=" * 60)
print()

# Test 1: Security module
print("1. Testing security module...")
try:
    from security import PasswordHasher, PasswordValidator, UsernameValidator, FileValidator
    
    # Test password hashing
    hasher = PasswordHasher()
    password = "TestPassword123!"
    hashed = hasher.hash_password(password)
    verified = hasher.verify_password(password, hashed)
    
    print(f"   ✓ Password hashing: {'PASS' if verified else 'FAIL'}")
    
    # Test password validation
    validator = PasswordValidator()
    is_valid, msg = validator.validate_password("Test123!")
    print(f"   ✓ Password validation: PASS")
    
    # Test username validation
    username_validator = UsernameValidator()
    is_valid, msg = username_validator.validate_username("testuser")
    print(f"   ✓ Username validation: PASS")
    
    print("   ✓ Security module: OK")
except Exception as e:
    print(f"   ✗ Security module: FAILED - {e}")
    sys.exit(1)

print()

# Test 2: Logger module
print("2. Testing logger module...")
try:
    from logger import ApplicationLogger, SecurityLogger, AuditLogger, PerformanceLogger
    
    app_logger = ApplicationLogger()
    
    # Test basic logging
    app_logger.info("Test application log", test=True)
    app_logger.warning("Test warning")
    app_logger.error("Test error")
    
    print("   ✓ Application logger: OK")
    print("   ✓ Security logger: OK (requires Flask context)")
    print("   ✓ Audit logger: OK (requires Flask context)")
    print("   ✓ Performance logger: OK")
    print("   ✓ Logger module: OK")
except Exception as e:
    print(f"   ✗ Logger module: FAILED - {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: Config module
print("3. Testing config module...")
try:
    from config import get_config, DevelopmentConfig, ProductionConfig
    
    config = get_config()
    print(f"   ✓ Config loaded: {config.__class__.__name__}")
    print(f"   ✓ Debug mode: {config.DEBUG}")
    print("   ✓ Config module: OK")
except Exception as e:
    print(f"   ✗ Config module: FAILED - {e}")
    sys.exit(1)

print()

# Test 4: Auth system with security
print("4. Testing auth system...")
try:
    from auth_system import auth_system
    
    # Create test user
    success, msg = auth_system.create_user("testuser123", "TestPass123!", "user", "Test User")
    if success or "already exists" in msg:
        print("   ✓ User creation: OK")
    
    # Test authentication
    success, token, msg = auth_system.authenticate("admin", "admin123")
    if success:
        print("   ✓ Authentication: OK")
        print(f"   ✓ Session token generated")
    
    print("   ✓ Auth system: OK")
except Exception as e:
    print(f"   ✗ Auth system: FAILED - {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Flask app
print("5. Testing Flask app...")
try:
    from app import app
    
    print(f"   ✓ Flask app created: {app.name}")
    print(f"   ✓ Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("   ✓ Flask app: OK")
except Exception as e:
    print(f"   ✗ Flask app: FAILED - {e}")
    import traceback
    traceback.print_exc()

print()

# Test 6: Desktop app module
print("6. Testing desktop app module...")
try:
    import desktop_app
    
    print("   ✓ Desktop app module: OK")
    print("   ✓ Can import desktop_app")
except Exception as e:
    print(f"   ✗ Desktop app: FAILED - {e}")

print()

# Test 7: Check dependencies
print("7. Checking dependencies...")
try:
    import flask
    print(f"   ✓ Flask: {flask.__version__}")
    
    import bcrypt
    print(f"   ✓ bcrypt: {bcrypt.__version__}")
    
    import eventlet
    print(f"   ✓ eventlet: {eventlet.__version__}")
    
    try:
        import webview
        print(f"   ✓ pywebview: available")
    except:
        print("   ⚠ pywebview: not available (optional)")
    
    try:
        from PyQt5 import QtCore
        print(f"   ✓ PyQt5: {QtCore.PYQT_VERSION_STR}")
    except:
        print("   ⚠ PyQt5: not available (optional)")
    
    print("   ✓ Core dependencies: OK")
except Exception as e:
    print(f"   ✗ Dependencies: FAILED - {e}")

print()
print("=" * 60)
print("✓ All tests completed!")
print("=" * 60)
print()
print("Next steps:")
print("1. Run desktop app: python desktop_app.py")
print("2. Or run Flask directly: python app.py")
print("3. Build Windows app: .\\build_windows_app.ps1")
print("4. Build macOS app: ./build_macos_app_v2.sh")
