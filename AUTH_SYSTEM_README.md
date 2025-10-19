# Authentication & Authorization System - Implementation Summary

## 🎯 Features Implemented

### 1. **User Authentication System**
- ✅ User registration with username, password, display name
- ✅ Secure login with session tokens (7-day expiry)
- ✅ Password hashing using SHA-256
- ✅ Session management with token validation
- ✅ Logout functionality
- ✅ Guest mode (view-only access without login)

### 2. **User Roles & Permissions**
Three predefined roles with different permission levels:

#### **Admin Role**
- Upload files
- Download files
- Delete any file
- Approve/reject delete requests
- Manage users
- Create admin accounts

#### **User Role**  
- Upload files
- Download files
- Delete own files only
- Request deletion of others' files
- Comment on files

#### **Viewer Role**
- Download files only
- View public files

### 3. **File Ownership & Metadata**
- ✅ Track file owner (who uploaded)
- ✅ Display owner name with each file
- ✅ Show creation date and time
- ✅ Store file type and size
- ✅ Maintain upload history per user

### 4. **File Permissions System**
Three permission levels for each file:

#### **Public**
- Anyone can view and download
- Default permission for new uploads

#### **Private**
- Only the owner can access
- Hidden from other users' file lists

#### **Restricted**
- Owner can specify which users can access
- Comma-separated list of allowed users

### 5. **Delete Request System**
- ✅ Non-owners can request file deletion
- ✅ Request includes reason field
- ✅ Admin approval required
- ✅ Admins can approve or reject requests
- ✅ Rejection includes reason
- ✅ Track request status (pending/approved/rejected)
- ✅ Automatic file deletion on approval

### 6. **Comment System**
- ✅ Add comments to files
- ✅ Mention other users with @ symbol
- ✅ Track comment author and timestamp
- ✅ View all comments per file
- ✅ Comments respect file permissions

## 📁 New Files Created

### 1. `auth_system.py`
Complete authentication and authorization module:
- User management (create, authenticate, validate)
- Session handling
- Permission checking
- File metadata storage
- Delete request management
- Comment system

### 2. `templates/login.html`
Beautiful login/register page:
- Modern gradient design
- Toggle between login and register
- Form validation
- Error/success messages
- Guest mode option

### 3. `data/` Directory
JSON database files (auto-created):
- `users.json` - User accounts
- `sessions.json` - Active sessions
- `file_metadata.json` - File ownership & permissions
- `comments.json` - File comments
- `delete_requests.json` - Deletion requests

## 🔧 Modified Files

### `app.py` - Enhanced with:
1. **New Endpoints:**
   - `POST /api/auth/register` - User registration
   - `POST /api/auth/login` - User login
   - `POST /api/auth/logout` - User logout
   - `GET /api/auth/me` - Get current user
   - `GET /api/users` - List all users (admin)
   - `GET /api/files/<filename>/permissions` - Get file permissions
   - `PUT /api/files/<filename>/permissions` - Update file permissions
   - `POST /api/files/<filename>/delete-request` - Request deletion
   - `GET /api/delete-requests` - List delete requests (admin)
   - `POST /api/delete-requests/<id>/approve` - Approve deletion (admin)
   - `POST /api/delete-requests/<id>/reject` - Reject deletion (admin)
   - `GET /api/files/<filename>/comments` - Get file comments
   - `POST /api/files/<filename>/comments` - Add comment
   - `GET /login` - Login page

2. **Modified Endpoints:**
   - `/upload` - Now requires login, saves owner & permissions
   - `/files` - Filters by permissions, adds metadata
   - `/delete/<filename>` - Checks owner/admin permissions

## 🚀 How to Use

### **First Time Setup**
1. Start the server
2. Navigate to `http://localhost:5000/login`
3. Default admin account:
   - Username: `admin`
   - Password: `admin123`
4. Login and change the password immediately!

### **Creating Users**
1. Register as regular user, OR
2. Admin can create users via API:
```javascript
fetch('/api/auth/register', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer <admin_token>'
    },
    body: JSON.stringify({
        username: 'john',
        password: 'securepass123',
        display_name: 'John Doe',
        role: 'user'  // or 'admin' or 'viewer'
    })
})
```

### **Uploading Files with Permissions**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('permission', 'restricted');  // public/private/restricted
formData.append('allowed_users', 'john,jane,bob');  // for restricted files

fetch('/upload', {
    method: 'POST',
    headers: {
        'Authorization': 'Bearer <token>'
    },
    body: formData
})
```

### **Requesting File Deletion**
```javascript
fetch('/api/files/example.pdf/delete-request', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer <token>'
    },
    body: JSON.stringify({
        reason: 'This file contains outdated information'
    })
})
```

### **Adding Comments**
```javascript
fetch('/api/files/example.pdf/comments', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer <token>'
    },
    body: JSON.stringify({
        comment: 'Great file! @john please review',
        mentions: ['john']
    })
})
```

## 🎨 Frontend Integration Required

The backend is complete, but you need to update `static/script.js` to:

1. **Add Login/Logout UI**
   - Show login button when not authenticated
   - Display current user info when logged in
   - Add logout button

2. **Send Auth Token with Requests**
   - Add `Authorization: Bearer <token>` header to all API calls
   - Redirect to /login if 401 Unauthorized

3. **Update File Cards**
   - Show owner name and creation date
   - Add permission badge (Public/Private/Restricted)
   - Show "Delete" button only if can_delete === true
   - Add "Request Delete" button for non-owners
   - Add permissions editor for owners
   - Add comments section

4. **Add Admin Panel**
   - Show delete requests list
   - Approve/Reject buttons
   - User management UI

## 📊 Database Structure

### Users
```json
{
  "admin": {
    "password": "hashed_password",
    "role": "admin",
    "display_name": "Admin User",
    "created_at": "2025-10-20T...",
    "last_login": "2025-10-20T..."
  }
}
```

### File Metadata
```json
{
  "example.pdf": {
    "owner": "john",
    "created_at": "2025-10-20T...",
    "permission": "restricted",
    "allowed_users": ["jane", "bob"],
    "size": 1024000,
    "type": "application/pdf"
  }
}
```

### Comments
```json
{
  "example.pdf": [
    {
      "id": 1,
      "username": "john",
      "comment": "Great work!",
      "mentions": [],
      "created_at": "2025-10-20T..."
    }
  ]
}
```

### Delete Requests
```json
{
  "example.pdf_john_1698765432": {
    "filename": "example.pdf",
    "requester": "john",
    "reason": "Outdated content",
    "status": "pending",
    "created_at": "2025-10-20T..."
  }
}
```

## ⚠️ Security Notes

1. **Change Default Admin Password** immediately after first login
2. **Use HTTPS in production** (set ENABLE_SSL=True)
3. **Consider using bcrypt** instead of SHA-256 for passwords
4. **Add rate limiting** to prevent brute force attacks
5. **Implement CSRF protection** for web forms
6. **Session tokens** expire after 7 days

## 🔄 Next Steps

To complete the implementation, you need to:

1. **Update `script.js`** - Add frontend code for all new features
2. **Test thoroughly** - Create users, upload files, test permissions
3. **Style the UI** - Make permission badges, comment boxes, etc.
4. **Add notifications** - Email/toast when mentioned in comments
5. **Implement search** - Filter files by owner, permission, etc.

## 📝 API Usage Examples

See the implementation for complete API documentation. All endpoints require Bearer token authentication except /login and /register.

**Authorization Header Format:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Store the token in `localStorage` and include it with every request!
