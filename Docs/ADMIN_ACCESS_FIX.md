# Admin Panel Access Fix

## Problem
When accessing `/admin` directly in the browser, users received a "Not Found" error because:
1. The route required authentication via Bearer token in headers
2. Browser navigation doesn't send Authorization headers
3. The decorator returned JSON error instead of redirecting to login

## Solution Implemented

### 1. Updated Admin Route (app.py)
- Removed `@require_permission('delete_any')` decorator
- Added custom authentication check that:
  - Reads token from cookies OR Authorization header
  - Validates the session
  - Redirects to home page (`/`) if not authenticated or not admin
  - Renders admin panel if authenticated

### 2. Cookie-Based Token Storage
To enable server-side authentication checks, the token is now stored in both localStorage AND cookies:

**login.html:**
```javascript
// Save token to cookie for server-side access
document.cookie = `authToken=${data.token}; path=/; max-age=604800`; // 7 days
```

**script.js (checkAuthStatus):**
```javascript
// Ensure token is also in cookie for server-side access
document.cookie = `authToken=${authToken}; path=/; max-age=604800`;
```

### 3. Updated Logout Functions
All logout functions now clear both localStorage AND cookies:

```javascript
localStorage.removeItem('authToken');
document.cookie = 'authToken=; path=/; max-age=0';
```

## How It Works Now

1. **Login Flow:**
   - User logs in via `/login`
   - Token saved to localStorage AND cookie
   - User redirected to home page

2. **Admin Access:**
   - User navigates to `/admin`
   - Server reads token from cookie
   - If valid admin token: shows admin panel
   - If invalid/missing: redirects to home page

3. **API Calls:**
   - Still use Authorization header with Bearer token
   - Server checks both cookies and headers for compatibility

## Testing Steps

1. **Login as Admin:**
   ```
   1. Go to http://192.168.1.14:5001/login
   2. Login with admin credentials
   3. You'll be redirected to home page
   ```

2. **Access Admin Panel:**
   ```
   1. Navigate to http://192.168.1.14:5001/admin
   2. Should see admin panel immediately (no redirect)
   ```

3. **Test Without Login:**
   ```
   1. Logout or open incognito window
   2. Navigate to http://192.168.1.14:5001/admin
   3. Should redirect to home page
   ```

4. **Test Logout:**
   ```
   1. Click logout in admin panel
   2. Should redirect to home page
   3. Try accessing /admin again - should redirect
   ```

## Files Modified

1. `app.py` - Updated `/admin` route with custom auth
2. `templates/login.html` - Added cookie storage on login
3. `templates/admin.html` - Updated logout to clear cookie
4. `static/script.js` - Added cookie sync and logout cleanup

## Benefits

✅ Direct browser access to admin panel works
✅ Authentication persists across page reloads
✅ Server can check auth without JavaScript
✅ Maintains security with token validation
✅ Backward compatible with API calls

## Security Notes

- Cookies have `path=/` to work across all routes
- Cookies expire after 7 days (same as token)
- Both localStorage and cookie cleared on logout
- Server validates token on every request
- Non-admin users are redirected, not shown error
