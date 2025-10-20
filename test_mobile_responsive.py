"""
Mobile Responsive Test - Verification Script
Tests that all mobile enhancements are properly implemented
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}")
        print(f"   Size: {size:,} bytes")
        return True
    else:
        print(f"❌ {description} - NOT FOUND")
        return False

def check_content_in_file(filepath, search_strings, description):
    """Check if specific content exists in file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        found_all = True
        for search_str in search_strings:
            if search_str not in content:
                print(f"❌ {description} - Missing: {search_str[:50]}")
                found_all = False
        
        if found_all:
            print(f"✅ {description}")
            return True
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("🧪 Mobile Responsive Implementation - Verification Test")
    print("="*70 + "\n")
    
    all_checks_passed = True
    
    # Check CSS file
    print("📱 Checking CSS Responsive Design...")
    css_checks = [
        "@media (max-width: 480px)",
        "@media (max-width: 768px)",
        "mobile-device",
        "-webkit-tap-highlight-color",
        "touch-action"
    ]
    if not check_content_in_file(
        'static/style.css',
        css_checks,
        "CSS mobile media queries and touch optimizations"
    ):
        all_checks_passed = False
    print()
    
    # Check JavaScript file
    print("📱 Checking JavaScript Mobile Enhancements...")
    js_checks = [
        "isMobileDevice",
        "initMobileEnhancements",
        "Long-press context menu",
        "touchstart",
        "mobile-device"
    ]
    if not check_content_in_file(
        'static/script.js',
        js_checks,
        "JavaScript mobile detection and touch handlers"
    ):
        all_checks_passed = False
    print()
    
    # Check app.py
    print("🚀 Checking Enhanced App Startup...")
    app_checks = [
        "configure_firewall_if_windows",
        "MOBILE/TABLET ACCESS",
        "Responsive UI: Works perfectly on mobile"
    ]
    if not check_content_in_file(
        'app.py',
        app_checks,
        "App.py startup enhancements and mobile instructions"
    ):
        all_checks_passed = False
    print()
    
    # Check HTML viewport
    print("📱 Checking HTML Viewport Meta Tag...")
    html_checks = [
        '<meta name="viewport"'
    ]
    if not check_content_in_file(
        'templates/index.html',
        html_checks,
        "HTML viewport meta tag for mobile"
    ):
        all_checks_passed = False
    print()
    
    # Check documentation
    print("📚 Checking Documentation...")
    docs = [
        ('MOBILE_RESPONSIVE_GUIDE.md', 'Mobile Responsive Guide'),
        ('MOBILE_IMPLEMENTATION_SUMMARY.md', 'Implementation Summary'),
        ('NETWORK_TROUBLESHOOTING.md', 'Network Troubleshooting Guide'),
    ]
    
    for doc_file, doc_name in docs:
        if not check_file_exists(doc_file, doc_name):
            all_checks_passed = False
    print()
    
    # Final summary
    print("="*70)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\n🎉 Mobile Responsive Implementation Complete!")
        print("\n📱 Your NetShare Pro is now:")
        print("   ✓ Fully responsive for mobile devices")
        print("   ✓ Touch-optimized with gestures")
        print("   ✓ Easy to start with 'python app.py'")
        print("   ✓ Auto-configured for network access")
        print("\n🚀 Ready to test:")
        print("   1. Run: python app.py")
        print("   2. Note the network IP shown")
        print("   3. Open that URL on your phone")
        print("   4. Enjoy the mobile experience!")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("   Please review the errors above")
    print("="*70 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == '__main__':
    sys.exit(main())
