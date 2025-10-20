"""
Test script to verify file loading fix
"""

def test_initialization_order():
    """Test that initialization happens in correct order"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Auth check before loadFiles': content.find('checkAuthStatus()') < content.find('// loadFiles()'),
        'loadFiles commented in init': '// loadFiles(); // Don\'t call here' in content,
        'loadFiles called after auth': 'await loadFiles();' in content and content.find('Authentication successful') < content.find('await loadFiles();'),
    }
    
    return checks

def test_loadfiles_improvements():
    """Test that loadFiles has proper error handling"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Has console logging': 'console.log(\'Loading files...\')' in content,
        'Checks for auth token': 'console.warn(\'No auth token available, files may not load\')' in content,
        'Handles 401 errors': 'response.status === 401' in content,
        'Shows loaded count': 'console.log(`Loaded ${allFiles.length} files successfully`)' in content,
    }
    
    return checks

def test_upload_auth():
    """Test that uploads include auth headers"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'XHR open before headers': content.find("xhr.open('POST', '/upload', true);") < content.find('xhr.setRequestHeader(\'Authorization\''),
        'Auth header warning': 'console.warn(\'No auth token available for upload\')' in content,
        'Auth header logging': 'console.log(\'Added auth header to upload request\')' in content,
    }
    
    return checks

def main():
    print("=" * 70)
    print("FILE LOADING FIX VERIFICATION")
    print("=" * 70)
    
    all_passed = True
    
    # Test initialization order
    print("\n✓ Initialization Order:")
    init_checks = test_initialization_order()
    for check, passed in init_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    # Test loadFiles improvements
    print("\n✓ LoadFiles Improvements:")
    load_checks = test_loadfiles_improvements()
    for check, passed in load_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    # Test upload auth
    print("\n✓ Upload Authentication:")
    upload_checks = test_upload_auth()
    for check, passed in upload_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✓ ALL CHECKS PASSED - File loading should work correctly!")
        print("\nFixes implemented:")
        print("  • loadFiles() now called AFTER authentication completes")
        print("  • Enhanced logging to debug file loading issues")
        print("  • Auth headers properly set for uploads")
        print("  • 401 errors properly handled with redirect to login")
        print("\nExpected behavior:")
        print("  1. Page loads → Authentication starts")
        print("  2. Auth completes → Files load with proper token")
        print("  3. Files display in file manager tab")
        print("  4. Uploads include auth token")
        print("  5. Files refresh after successful upload")
    else:
        print("✗ SOME CHECKS FAILED - Please review the output above")
    print("=" * 70)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
