# Admin Panel Documentation

## 🎯 Overview

The Admin Panel provides comprehensive system monitoring and management capabilities for administrators of the Circuvent Technologies NetShare Pro platform.

## 🔐 Access Requirements

- **Role Required**: Administrator (`admin` role)
- **URL**: `/admin`
- **Authentication**: Must be logged in with admin privileges

## 📊 Features

### 1. **Real-Time Dashboard**
- Live statistics on users, files, storage, and active transfers
- Real-time transfer speed monitoring (Mbps)
- Visual performance charts with Chart.js

### 2. **User Management**
- View all registered users
- See user roles (Admin, User, Viewer)
- Track user activity and file counts
- Delete users (admin only)
- User information includes:
  - Username and display name
  - Role and permissions
  - File count
  - Last active time

### 3. **File Management**
- Complete file listing with metadata
- View file owner, size, upload date
- Track download counts
- Search functionality
- Delete files (admin only)
- Bulk operations support

### 4. **Transfer Monitoring**
- Live view of active uploads/downloads
- Real-time progress tracking
- Speed monitoring (Mbps)
- Transfer type identification
- Historical performance data

### 5. **Activity Log**
- Recent system activity
- Upload/download tracking
- User actions
- Timestamped events

## 🎨 Dashboard Components

### Statistics Cards
- **Total Users**: Number of registered users
- **Total Files**: Count of stored files
- **Storage Used**: Total disk space consumed
- **Active Transfers**: Current uploads/downloads in progress

### Users Table
Columns:
- User (avatar + username)
- Role (with color-coded badges)
- Files (file count)
- Last Active
- Actions (edit/delete)

### Files Table
Columns:
- File Name
- Owner
- Size (formatted)
- Uploaded (timestamp)
- Downloads (count)
- Actions (download/delete)

### Recent Activity Feed
- Activity type icon (upload/download/delete)
- Activity description
- User who performed action
- File details
- Timestamp

### Transfer Speed Monitor
- Real-time Mbps display
- Current transfer speed gauge
- Upload/download speed differentiation

### Performance Chart
- Line chart showing transfer speeds over time
- Upload speed (blue line)
- Download speed (purple line)
- Last 20 data points
- Auto-updating every 2 seconds

## 🚀 WebSocket Integration

The admin panel uses WebSocket for real-time updates:

### Events Listened:
- `transfer_update`: Real-time transfer progress and speed
- `active_transfers`: List of all active transfers
- `connected`: WebSocket connection status

### Data Flow:
```
Server → WebSocket → Admin Panel
   ↓
Real-time updates every 2 seconds
   ↓
Chart and UI updates
```

## 🎛️ API Endpoints

### Dashboard Data
```
GET /api/admin/dashboard
Response:
{
  "stats": {
    "total_users": 10,
    "total_files": 150,
    "storage_used": 5368709120,
    "active_transfers": 2
  },
  "users": [...],
  "files": [...],
  "recent_activity": [...]
}
```

### Delete User
```
DELETE /api/admin/users/{username}
Response: {"success": true}
```

### Delete File
```
DELETE /api/admin/files/{filename}
Response: {"success": true}
```

## 🎨 UI Features

### Design Elements:
- Modern glassmorphism design
- Gradient backgrounds
- Smooth animations
- Responsive layout
- Mobile-friendly
- Dark mode ready

### Color Scheme:
- Primary: `#667eea` (purple-blue)
- Secondary: `#764ba2` (purple)
- Success: `#48bb78` (green)
- Danger: `#f56565` (red)
- Warning: `#fbd38d` (orange)

### Interactive Elements:
- Hover effects on cards
- Smooth transitions
- Pulse animations
- Real-time counters
- Progress bars

## 📱 Responsive Breakpoints

- **Desktop**: 1024px+ (full layout)
- **Tablet**: 768px-1023px (stacked panels)
- **Mobile**: <768px (single column)

## 🔄 Auto-Refresh

- Dashboard data refreshes every 5 seconds
- Transfer stats update every 2 seconds
- Charts update in real-time
- Activity feed updates automatically

## 🛡️ Security

### Access Control:
- Admin role verification on every request
- Session validation via JWT tokens
- CSRF protection
- XSS prevention

### User Management:
- Cannot delete yourself
- Cascading deletions (sessions cleanup)
- Audit trail maintained

### File Management:
- Metadata cleanup on deletion
- Orphaned file detection
- Storage quota monitoring

## 📈 Performance

### Optimization:
- WebSocket for real-time data (low overhead)
- Efficient data structures
- Minimal DOM updates
- Lazy loading for large lists
- Pagination support (future)

### Monitoring:
- Transfer speed tracking
- System resource usage
- User activity patterns
- Storage trends

## 🔧 Configuration

Located in `app.py`:
```python
# Enable admin features
ENABLE_AUTH = True  # Must be enabled

# Admin role in auth_system.py
ROLES = {
    'admin': ['upload', 'download', 'delete', 
              'delete_any', 'manage_users', 'approve_delete']
}
```

## 🎯 Usage Examples

### Creating Admin User:
```bash
# Register with admin role via API or initial setup
POST /api/auth/register
{
  "username": "admin",
  "password": "secure_password",
  "display_name": "System Admin",
  "role": "admin"
}
```

### Accessing Admin Panel:
1. Login as admin user
2. Click profile dropdown
3. Select "Admin Panel"
4. Or navigate to `/admin`

### Monitoring Transfers:
- Watch the "Active Transfers" section
- View real-time speed in Mbps
- Track progress percentages
- See transfer type (upload/download)

### Managing Users:
1. Go to "Users Management" section
2. View all users and their roles
3. Click edit to modify user details
4. Click delete to remove user

### Managing Files:
1. Go to "Files Management" section
2. Search for specific files
3. View file metadata
4. Download or delete files
5. Track download counts

## 🐛 Troubleshooting

### Admin Panel Not Accessible:
- Verify user has admin role
- Check authentication is enabled
- Ensure logged in with valid session

### Real-time Updates Not Working:
- Check WebSocket connection
- Verify Socket.IO is loaded
- Check browser console for errors

### Charts Not Displaying:
- Ensure Chart.js is loaded
- Check canvas element exists
- Verify data format

## 🚀 Future Enhancements

- [ ] User editing modal
- [ ] Bulk file operations
- [ ] Advanced search/filtering
- [ ] Export reports (CSV/PDF)
- [ ] Email notifications
- [ ] Backup/restore functionality
- [ ] System health monitoring
- [ ] API usage analytics
- [ ] Custom dashboards
- [ ] Role creation wizard

## 📝 Notes

- The admin panel requires authentication to be enabled
- Only users with `admin` role can access
- Real-time features require WebSocket support
- Mobile view provides essential features
- All actions are logged in activity feed

## 🎊 Summary

The Admin Panel provides a comprehensive, real-time monitoring and management interface for system administrators. With WebSocket integration for live updates, beautiful UI, and powerful management features, it makes system administration efficient and enjoyable.

**Key Highlights:**
- ⚡ Real-time monitoring (500+ Mbps transfers visible)
- 👥 Complete user management
- 📁 Advanced file operations
- 📊 Performance analytics
- 🎨 Modern, responsive design
- 🔒 Secure access control

**Access URL**: `/admin` (requires admin role)
