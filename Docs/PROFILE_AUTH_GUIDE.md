# Profile and Authentication Features

## Overview
The application now includes a complete authentication system with profile management, persistent login sessions, and role-based access control.

## Features Implemented

### 1. **Persistent Login Sessions**
- Auth tokens stored in localStorage
- Automatic login on page refresh
- 7-day session expiry (server-side)
- Token validated on every page load

### 2. **Profile Dropdown Menu**
Located in the top-right corner of the interface:

**Components:**
- User avatar icon
- Display name
- User role badge
- Dropdown chevron

**Menu Options:**
- **Profile Header**: Shows user avatar, display name, and username
- **My Files**: Filter to show only files uploaded by current user
- **Settings**: (Coming soon)
- **Admin Panel**: Only visible for admin users
- **Logout**: Clears session and redirects to login page

### 3. **Authentication Flow**

#### Login Process:
1. User enters credentials on `/login` page
2. Server validates and returns auth token
3. Token stored in `localStorage` as `authToken`
4. User redirected to main interface
5. Profile dropdown appears in header

#### Auto-Login:
1. On page load, `checkAuthStatus()` runs
2. Retrieves token from localStorage
3. Validates token with server (`/api/auth/me`)
4. If valid: Shows user profile
5. If invalid: Shows login button

#### Logout Process:
1. User clicks logout in dropdown
2. Confirmation dialog appears
3. If confirmed:
   - Calls `/api/auth/logout` API
   - Clears localStorage
   - Redirects to `/login`

### 4. **Authorization Headers**
All authenticated API calls now include:
```javascript
headers: {
    'Authorization': `Bearer ${authToken}`
}
```

**Protected Operations:**
- File upload
- File deletion
- File listing (filters by permissions)
- Comments
- Delete requests
- Permission changes

### 5. **Role-Based Features**

**Admin Users:**
- Admin Panel button visible in dropdown
- Can delete any file
- Can approve/reject delete requests
- Can manage users
- Can change any file's permissions

**Regular Users:**
- Can upload files
- Can delete own files
- Can request deletion of others' files
- Can comment on accessible files
- Can set permissions on own files

**Viewers:**
- Can view public files
- Can download files
- Limited upload capabilities

### 6. **My Files Filter**
Clicking "My Files" in dropdown:
- Filters files to show only user's uploads
- Uses `file.owner === currentUser.username`
- Displays count of user's files
- Automatically switches to Files section
- Shows toast notification

## UI Components

### Profile Button
```html
<div class="user-profile">
    <button class="profile-btn">
        <div class="profile-avatar">
            <i class="fas fa-user"></i>
        </div>
        <div class="profile-info">
            <span class="profile-name">John Doe</span>
            <span class="profile-role">admin</span>
        </div>
        <i class="fas fa-chevron-down"></i>
    </button>
</div>
```

### Profile Dropdown
- Smooth fade-in/out animation
- Positioned below profile button
- Closes on outside click
- Responsive design

## JavaScript Functions

### Core Authentication
- `checkAuthStatus()` - Validates session on load
- `showUserProfile()` - Displays profile UI
- `showLoginButton()` - Shows login when not authenticated
- `updateUIForUser()` - Adjusts UI based on role
- `logout()` - Handles logout process

### File Management
- `filterMyFiles()` - Shows user's files only
- `deleteFile(filename)` - Deletes file with auth
- `loadFiles()` - Loads files with permissions
- `uploadFile(file)` - Uploads with auth token

## Security Features

1. **Token Storage**: Secure localStorage storage
2. **Token Validation**: Server-side validation on every request
3. **Session Expiry**: Automatic logout after 7 days
4. **CORS Protection**: Proper headers configured
5. **Permission Checks**: Server validates user permissions
6. **XSS Prevention**: HTML escaping in usernames

## User Experience

### First-Time User
1. Lands on main page
2. Sees "Login" button in header
3. Clicks to go to login page
4. Registers or logs in
5. Redirected back to main page
6. Profile appears automatically

### Returning User
1. Visits site
2. Token auto-validated
3. Profile shows immediately
4. No need to login again
5. Works until session expires

### Session Expired
1. User tries to perform action
2. Server returns 401 Unauthorized
3. Frontend clears invalid token
4. Login button appears
5. User redirected to login

## Configuration

### Auth Token Storage
```javascript
// Save token
localStorage.setItem('authToken', token);

// Retrieve token
const token = localStorage.getItem('authToken');

// Clear token
localStorage.removeItem('authToken');
```

### Session Duration
Configured in `auth_system.py`:
```python
SESSION_EXPIRY = timedelta(days=7)
```

## Testing Checklist

- [ ] Login with valid credentials
- [ ] Auto-login on page refresh
- [ ] Profile dropdown opens/closes
- [ ] Display name shows correctly
- [ ] Role badge shows correctly
- [ ] My Files filter works
- [ ] Admin panel visible for admins only
- [ ] Logout confirmation works
- [ ] Token cleared on logout
- [ ] Redirect to login after logout
- [ ] Upload requires authentication
- [ ] Delete requires authentication
- [ ] Permissions enforced properly

## Browser Compatibility

- **localStorage**: All modern browsers
- **Fetch API**: All modern browsers
- **CSS Animations**: All modern browsers
- **ES6 Features**: All modern browsers

## Future Enhancements

1. **Profile Settings**:
   - Change display name
   - Change password
   - Update avatar
   - Email notifications

2. **Admin Panel**:
   - User management interface
   - Permission management
   - Activity logs
   - System settings

3. **Session Management**:
   - Remember me option
   - Multiple device sessions
   - Session activity log
   - Force logout all devices

4. **Security**:
   - Two-factor authentication
   - Password strength requirements
   - Account recovery
   - Login attempt limits

## Troubleshooting

### Profile Not Showing
- Check localStorage for `authToken`
- Check browser console for errors
- Verify server is running
- Check `/api/auth/me` endpoint

### Auto-Logout Issues
- Check token expiry time
- Verify server clock accuracy
- Check session database

### Permission Errors
- Verify user role in database
- Check file ownership
- Review permission settings
- Check server logs

## API Endpoints Used

- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout user
- `GET /files` - List files (with auth)
- `POST /upload` - Upload file (with auth)
- `DELETE /delete/<filename>` - Delete file (with auth)
- `GET /api/users` - Get all users (admin)

## Files Modified

1. `templates/index.html` - Added profile dropdown HTML
2. `static/script.js` - Added auth functions and event listeners
3. `static/style.css` - Profile dropdown styles (already existed)
4. `app.py` - Auth endpoints (already existed)

## Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`
- Role: `admin`

Created automatically on first run.
