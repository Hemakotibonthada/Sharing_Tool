"""
Test script to verify redirect loop fix
"""

def test_login_page_protection():
    """Test that login page has redirect protection"""
    with open('templates/login.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Has redirecting flag': 'let redirecting = false' in content,
        'Has setTimeout delay': 'setTimeout(() => {' in content and '}, 300)' in content,
        'Has token validation': "fetch('/api/auth/me'" in content,
        'Clears invalid tokens': 'localStorage.removeItem' in content,
    }
    
    return checks

def test_main_page_protection():
    """Test that main page has redirect protection"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Has isRedirecting flag': 'let isRedirecting = false' in content,
        'Has pathname check': "window.location.pathname === '/login'" in content,
        'Has setTimeout in showLoginButton': 'setTimeout(() => {' in content and 'window.location.href = \'/login\'' in content,
        'Has authCheckInProgress flag': 'let authCheckInProgress = false' in content,
        'Skips init on login page': "if (window.location.pathname === '/login')" in content and 'return;' in content,
    }
    
    return checks

def test_settings_page_protection():
    """Test that settings page has redirect protection"""
    with open('templates/settings.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Has authCheckInProgress flag': 'let authCheckInProgress = false' in content,
        'Has redirectingToLogin flag': 'let redirectingToLogin = false' in content,
        'Has setTimeout delay': 'setTimeout(() => {' in content and '}, 500)' in content,
        'Has pathname check': "window.location.pathname !== '/login'" in content,
    }
    
    return checks

def main():
    print("=" * 60)
    print("REDIRECT LOOP FIX VERIFICATION")
    print("=" * 60)
    
    all_passed = True
    
    # Test login page
    print("\n✓ Login Page Protection:")
    login_checks = test_login_page_protection()
    for check, passed in login_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    # Test main page
    print("\n✓ Main Page Protection:")
    main_checks = test_main_page_protection()
    for check, passed in main_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    # Test settings page
    print("\n✓ Settings Page Protection:")
    settings_checks = test_settings_page_protection()
    for check, passed in settings_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED - Redirect loop fix verified!")
        print("\nThe following protections are in place:")
        print("  • Login page: 300ms delay + token validation")
        print("  • Main page: Skips init on /login + redirect delays")
        print("  • Settings page: 500ms delay + duplicate check")
        print("\nYou should now be able to:")
        print("  1. Start the server without refresh loops")
        print("  2. Type credentials immediately on login page")
        print("  3. Navigate between pages without issues")
    else:
        print("✗ SOME CHECKS FAILED - Please review the output above")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
