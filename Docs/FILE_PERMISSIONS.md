# File Permission System

## Overview
The file sharing application now includes a comprehensive permission system that allows users to control who can access their uploaded files.

## Permission Levels

### 1. **Public** 🌐
- **Access**: Everyone can view and download
- **Use Case**: Files intended for sharing with all users
- **Default**: Legacy files without metadata are treated as public
- **Badge**: Green badge with globe icon

### 2. **Private** 🔒
- **Access**: Only the file owner can view and download
- **Use Case**: Personal files not intended for sharing
- **Security**: Complete isolation from other users
- **Badge**: Red badge with lock icon

### 3. **Restricted** 👥
- **Access**: Only the owner and specified users can view and download
- **Use Case**: Selective sharing with specific team members
- **Configuration**: Owner can specify a comma-separated list of usernames
- **Badge**: Orange badge with users icon

## How to Use

### Uploading Files with Permissions

1. **Select File**: Choose a file to upload
2. **Choose Permission**: Select from the dropdown:
   - "Public - Everyone can view"
   - "Private - Only me"
   - "Restricted - Specific users"
3. **Specify Users** (for Restricted only):
   - Enter comma-separated usernames
   - Example: `john, sarah, mike`
   - Only these users (plus the owner) can access the file
4. **Upload**: Click the upload button

### Visual Indicators

Each file card displays a permission badge showing:
- 🌐 **Public**: Green badge
- 🔒 **Private**: Red badge
- 👥 **Restricted**: Orange badge

The badge appears in the file metadata section below the file name.

## Implementation Details

### Frontend Components

#### Upload UI (`templates/index.html`)
```html
<select id="permissionSelect" class="input-field">
    <option value="public">Public - Everyone can view</option>
    <option value="private">Private - Only me</option>
    <option value="restricted">Restricted - Specific users</option>
</select>

<input type="text" id="allowedUsers" placeholder="Enter usernames (comma-separated)">
```

#### Permission Badges (`static/script.js`)
- Dynamically added to each file card
- Shows icon and text label
- Tooltip displays permission description

#### Styling (`static/style.css`)
- Color-coded badges (green/red/orange)
- Semi-transparent backgrounds
- Consistent with glassmorphism design

### Backend Components

#### Permission Storage (`auth_system.py`)
```python
def save_file_metadata(self, filename, owner, permission='public', allowed_users=None):
    """Save file metadata including permissions"""
```

#### Access Control (`auth_system.py`)
```python
def can_access_file(self, filename, username):
    """Check if user can access file based on permissions"""
    - Public: Always returns True
    - Private: Returns True only for owner
    - Restricted: Returns True for owner or allowed users
```

#### Protected Endpoints (`app.py`)
- `/download/<filename>`: Requires `@require_auth`, checks `can_access_file`
- `/preview/<filename>`: Requires `@require_auth`, checks `can_access_file`
- `/files`: Filters files based on user permissions

#### Upload Endpoints
- **HTTP Upload** (`uploadFileHTTP` in `script.js`):
  - Sends permission and allowed_users in FormData
  - Fallback method for Mac compatibility

- **WebSocket Upload** (`uploadFile` in `highspeed.js`):
  - Sends permission and allowed_users in start_upload event
  - High-speed transfer with chunking

### File Metadata Structure

```json
{
  "filename": "document.pdf",
  "owner": "john",
  "permission": "restricted",
  "allowed_users": ["sarah", "mike"],
  "created_at": "2024-01-15 10:30:45",
  "size": 2048576,
  "type": "application/pdf"
}
```

## Security Features

### 1. **Authentication Required**
- All download and preview endpoints require valid authentication
- Token validation via cookies or Bearer tokens
- Session management prevents unauthorized access

### 2. **Permission Enforcement**
- Backend validates permissions before serving files
- Users cannot bypass restrictions through direct URLs
- API endpoints filter file lists based on permissions

### 3. **Owner Privileges**
- File owners can always access their own files
- Owners can delete their files (regardless of permission)
- Admin users can delete any file

### 4. **Metadata Protection**
- Permissions stored in separate metadata file
- Cannot be modified through file upload
- Persistent across server restarts

## User Experience

### For File Uploaders
1. Choose appropriate permission level during upload
2. Visual confirmation via permission badge
3. Can see permission in file details
4. Default is "Public" for backward compatibility

### For File Viewers
1. Only see files they have permission to access
2. Cannot see private files of other users
3. Cannot see restricted files unless explicitly allowed
4. Clear visual indication of permission level

### For Administrators
- Can see and delete all files
- Has `delete_any` permission
- Can manage user permissions
- Full access to file metadata

## Testing the System

### Test Public Files
1. Upload a file with "Public" permission
2. Log in as different user
3. Verify file appears in file list
4. Confirm download/preview works

### Test Private Files
1. Upload a file with "Private" permission
2. Log in as different user
3. Verify file does NOT appear in file list
4. Confirm direct URL access is blocked (403 error)

### Test Restricted Files
1. Upload a file with "Restricted" permission
2. Specify user "john" in allowed users
3. Log in as "john" - verify access granted
4. Log in as "mike" - verify access denied

## API Response Examples

### Successful Access
```json
{
  "success": true,
  "file": "document.pdf"
}
```

### Permission Denied
```json
{
  "error": "You do not have permission to access this file"
}
```

### File List with Permissions
```json
[
  {
    "name": "public_doc.pdf",
    "owner": "john",
    "permission": "public",
    "can_delete": false
  },
  {
    "name": "my_private.txt",
    "owner": "john",
    "permission": "private",
    "can_delete": true
  }
]
```

## Troubleshooting

### Permission Not Saving
- Check that auth_system.save_file_metadata is called in finalize_upload
- Verify data/file_metadata.json is writable
- Check browser console for upload errors

### Badge Not Appearing
- Clear browser cache and refresh
- Check that file metadata includes permission field
- Verify CSS classes are loaded (permission-badge)

### Access Denied Errors
- Confirm user is logged in
- Check that username exactly matches allowed_users
- Verify file metadata has correct permission value

### Restricted Users Not Working
- Ensure usernames are comma-separated
- Check for extra spaces (should be trimmed)
- Verify users exist in the system

## Future Enhancements

### Potential Features
1. **Permission Editing**: Allow owners to change file permissions after upload
2. **Group Permissions**: Create user groups for easier management
3. **Expiring Links**: Time-limited access for temporary sharing
4. **Download Notifications**: Alert owners when files are accessed
5. **Permission Templates**: Save common permission configurations
6. **Audit Log**: Track who accessed which files and when

### UI Improvements
1. Filter files by permission level
2. Bulk permission updates
3. Permission preview before upload
4. Visual indicators in upload progress
5. Permission history/changes log

## Conclusion

The file permission system provides flexible, secure control over file sharing. Users can choose the appropriate level of privacy for each file, from completely public to highly restricted access. The system integrates seamlessly with the existing authentication framework and maintains backward compatibility with existing files.
