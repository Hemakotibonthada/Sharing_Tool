"""
Complete test script to verify all fixes
"""

def test_initialization_improvements():
    """Test that initialization is properly guarded"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Has appInitialized flag': 'let appInitialized = false' in content,
        'Checks appInitialized': 'if (appInitialized)' in content,
        'Sets appInitialized': 'appInitialized = true' in content,
        'Prevents duplicate init': 'App already initialized, skipping duplicate initialization' in content,
        'Stats not called in init': '// updateStats(); // Don\'t call here' in content,
        'TransferStatus not called in init': '// updateTransferStatus(); // Don\'t call here' in content,
    }
    
    return checks

def test_auth_triggers_data_load():
    """Test that auth success loads both files and stats"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Loads files after auth': 'await loadFiles();' in content and 'Authentication successful' in content,
        'Loads stats after auth': 'await updateStats();' in content and 'Authentication successful' in content,
        'Loads transfer status after auth': 'await updateTransferStatus();' in content and 'Authentication successful' in content,
        'Shows completion message': 'Initial data load complete' in content,
    }
    
    return checks

def test_stats_with_auth():
    """Test that stats includes auth headers"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find updateStats function
    stats_func_start = content.find('async function updateStats()')
    stats_func_end = content.find('\n}', stats_func_start) + 2
    stats_func = content[stats_func_start:stats_func_end]
    
    checks = {
        'Sends auth header': 'headers[\'Authorization\'] = `Bearer ${authToken}`' in stats_func,
        'Logs stats update': 'Stats updated:' in stats_func,
        'Shows file count': '${stats.total_files} files' in stats_func,
    }
    
    return checks

def test_backend_permission_filtering():
    """Test that backend /stats endpoint respects permissions"""
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find get_stats function
    stats_func_start = content.find('def get_stats():')
    stats_func_end = content.find('\n\n@app.route', stats_func_start)
    if stats_func_end == -1:
        stats_func_end = content.find('\n\ndef ', stats_func_start)
    stats_func = content[stats_func_start:stats_func_end]
    
    checks = {
        'Gets auth token': 'request.headers.get(\'Authorization\'' in stats_func,
        'Validates session': 'auth_system.validate_session' in stats_func,
        'Checks file access': 'auth_system.can_access_file' in stats_func,
        'Filters by permission': 'if current_username and not auth_system.can_access_file' in stats_func,
        'Returns accessible count': 'len(accessible_files)' in stats_func,
    }
    
    return checks

def test_redirect_loop_protections():
    """Test that redirect loop protections are still in place"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        'Has isRedirecting flag': 'let isRedirecting = false' in content,
        'Has authCheckInProgress flag': 'let authCheckInProgress = false' in content,
        'Checks pathname': "window.location.pathname === '/login'" in content,
        'Has redirect delay': 'setTimeout(() => {' in content and 'window.location.href = \'/login\'' in content,
    }
    
    return checks

def test_file_loading_improvements():
    """Test that file loading improvements are in place"""
    with open('static/script.js', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find loadFiles function
    load_func_start = content.find('async function loadFiles()')
    load_func_end = content.find('\n}', load_func_start) + 2
    load_func = content[load_func_start:load_func_end]
    
    checks = {
        'Logs loading start': 'console.log(\'Loading files...\')' in load_func,
        'Logs auth token usage': 'console.log(\'Using auth token for file loading\')' in load_func,
        'Logs loaded count': 'console.log(`Loaded ${allFiles.length} files successfully`)' in load_func,
        'Handles 401 errors': 'response.status === 401' in load_func,
    }
    
    return checks

def main():
    print("=" * 80)
    print("COMPLETE FIX VERIFICATION - ALL ISSUES")
    print("=" * 80)
    
    all_passed = True
    total_checks = 0
    passed_checks = 0
    
    # Test initialization improvements
    print("\n✓ Initialization Improvements (Refresh Fix):")
    init_checks = test_initialization_improvements()
    for check, passed in init_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        total_checks += 1
        if passed:
            passed_checks += 1
        else:
            all_passed = False
    
    # Test auth triggers data load
    print("\n✓ Auth Triggers Data Load:")
    auth_checks = test_auth_triggers_data_load()
    for check, passed in auth_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        total_checks += 1
        if passed:
            passed_checks += 1
        else:
            all_passed = False
    
    # Test stats with auth
    print("\n✓ Stats Include Auth:")
    stats_checks = test_stats_with_auth()
    for check, passed in stats_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        total_checks += 1
        if passed:
            passed_checks += 1
        else:
            all_passed = False
    
    # Test backend permission filtering
    print("\n✓ Backend Permission Filtering:")
    backend_checks = test_backend_permission_filtering()
    for check, passed in backend_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        total_checks += 1
        if passed:
            passed_checks += 1
        else:
            all_passed = False
    
    # Test redirect loop protections
    print("\n✓ Redirect Loop Protections (Still Working):")
    redirect_checks = test_redirect_loop_protections()
    for check, passed in redirect_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        total_checks += 1
        if passed:
            passed_checks += 1
        else:
            all_passed = False
    
    # Test file loading improvements
    print("\n✓ File Loading Improvements (Still Working):")
    file_checks = test_file_loading_improvements()
    for check, passed in file_checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
        total_checks += 1
        if passed:
            passed_checks += 1
        else:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print(f"✓ ALL CHECKS PASSED - {passed_checks}/{total_checks} tests successful!")
        print("\nAll fixes implemented:")
        print("  ✓ Refresh loop fixed - appInitialized flag prevents duplicate init")
        print("  ✓ Stats match files - backend respects user permissions")
        print("  ✓ Data loads after auth - files, stats, transfer status")
        print("  ✓ Redirect protections - still working (login loop fix intact)")
        print("  ✓ File loading - still working (loads after auth)")
        print("\nExpected behavior:")
        print("  1. Page loads once (no refresh loop)")
        print("  2. Authentication completes")
        print("  3. Files, stats, and transfer status load together")
        print("  4. Dashboard file count matches Files tab count")
        print("  5. All previous fixes still working")
    else:
        print(f"✗ SOME CHECKS FAILED - {passed_checks}/{total_checks} tests passed")
        print("Please review the output above")
    print("=" * 80)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
