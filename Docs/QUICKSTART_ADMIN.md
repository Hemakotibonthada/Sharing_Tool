# 🚀 Quick Start Guide - Admin Panel

## Step 1: Start the Server

```powershell
cd c:\Users\hemak\OneDrive\Documents\WorkSpace\Sharing
python app.py
```

**Expected Output:**
```
============================================================
🚀 Circuvent Technologies - NetShare Pro v2.0
   Advanced File Sharing Server
============================================================

📱 Access from this device: http://localhost:5001
🌐 Access from network: http://192.168.1.14:5001

💡 Scan the QR code on the webpage to access from mobile devices
...
```

## Step 2: Create Admin User

### Option A: Via API
```powershell
# Using curl (if installed)
curl -X POST http://localhost:5001/api/auth/register -H "Content-Type: application/json" -d '{\"username\":\"admin\",\"password\":\"admin123\",\"display_name\":\"System Admin\",\"role\":\"admin\"}'
```

### Option B: Via Browser Console
1. Open `http://localhost:5001` in browser
2. Open Developer Tools (F12)
3. Go to Console tab
4. Run:
```javascript
fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'admin',
        password: 'admin123',
        display_name: 'System Admin',
        role: 'admin'
    })
}).then(r => r.json()).then(console.log)
```

## Step 3: Login

1. Go to `http://localhost:5001`
2. Click "Login" button
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
4. Click "Login"

**You should see:**
- Profile dropdown in top-right corner
- Your avatar with username "System Admin"
- Role badge showing "admin"

## Step 4: Access Admin Panel

### Method 1: Via Dropdown
1. Click on your profile in top-right
2. Click "Admin Panel" option

### Method 2: Direct URL
```
http://localhost:5001/admin
```

## Step 5: Explore Admin Panel

### Dashboard Overview
You'll see 4 main statistics cards:
- **Total Users**: Number of registered users
- **Total Files**: Count of stored files
- **Storage Used**: Total disk space
- **Active Transfers**: Current uploads/downloads

### Available Panels
1. **Users Management** - View and manage all users
2. **Recent Activity** - See what's happening in real-time
3. **Active Transfers** - Monitor ongoing uploads/downloads
4. **Transfer Speed** - Live Mbps display
5. **Files Management** - Complete file listing
6. **Performance Chart** - Transfer speed visualization

## 🧪 Test the Features

### Test User Management
1. Create another test user:
```javascript
fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username: 'testuser',
        password: 'test123',
        display_name: 'Test User',
        role: 'user'
    })
}).then(r => r.json()).then(console.log)
```

2. Refresh admin panel - you should see 2 users

### Test File Upload with Speed Monitoring
1. Open main page in another tab
2. Upload a large file (100MB+)
3. Watch admin panel:
   - Active Transfers updates in real-time
   - Speed shows in Mbps
   - Progress bars update
   - Chart shows upload speed

### Test Real-time Updates
1. Keep admin panel open
2. In another tab, upload a file
3. Watch the admin panel update automatically
4. See the performance chart update

## 🎯 Common Actions

### View All Users
- Scroll to "Users Management" section
- See username, role, file count, last active
- Role badges: Admin (orange), User (blue), Viewer (green)

### Delete a User
1. Find user in Users Management table
2. Click red trash icon (🗑️)
3. Confirm deletion
4. User removed instantly

### View All Files
- Scroll to "Files Management" section
- See filename, owner, size, upload date, downloads
- Search for specific files in search box

### Delete a File
1. Find file in Files Management table
2. Click red trash icon (🗑️)
3. Confirm deletion
4. File removed instantly

### Monitor Transfers
- "Active Transfers" panel shows ongoing uploads/downloads
- Real-time progress bars
- Live speed in Mbps
- Type (upload/download)

### View Performance Chart
- Scroll to "Transfer Performance" panel
- Blue line = Upload speed
- Purple line = Download speed
- Hover over points for exact values
- Auto-updates in real-time

## 🔄 Auto-Refresh

The admin panel automatically refreshes:
- **Dashboard data**: Every 5 seconds
- **Transfer stats**: Every 2 seconds (WebSocket)
- **Charts**: Real-time on new data

You can also manually refresh by clicking the "🔄 Refresh" button.

## 🚪 Logout

Click "Logout" button in:
- Top-right corner (admin panel)
- Profile dropdown menu
- Both will clear your session

## 🎨 UI Features

### Glassmorphism Design
- Frosted glass effect on panels
- Smooth backdrop blur
- Modern gradient backgrounds

### Responsive Layout
- Desktop: Full multi-column layout
- Tablet: Stacked panels
- Mobile: Single column view

### Interactive Elements
- Hover effects on all cards
- Smooth transitions
- Pulse animations on live indicators
- Icon-based buttons

### Real-time Indicators
- Green "System Online" badge with pulse
- Live Mbps counter
- Animated progress bars
- Auto-updating charts

## 🐛 Troubleshooting

### Admin Panel Shows "Access Denied"
- **Cause**: Not logged in as admin
- **Solution**: Login with admin role user

### No Real-time Updates
- **Cause**: WebSocket not connected
- **Solution**: Check browser console, refresh page

### Stats Show 0
- **Cause**: No data yet
- **Solution**: Create users, upload files first

### Can't Delete User
- **Cause**: Trying to delete yourself
- **Solution**: Create another admin, login as them

## 📊 What to Expect

### Initial State (No Data)
- Total Users: 1 (admin)
- Total Files: 0
- Storage Used: 0 GB
- Active Transfers: 0

### After Some Activity
- Multiple users visible
- Files listed with metadata
- Recent activity shows events
- Charts show transfer patterns

### During Large Upload (100MB+)
- Active Transfers: 1
- Current Speed: 500-700 Mbps (on gigabit)
- Progress bar: 0% → 100%
- Chart: Real-time speed line

## ✅ Verification Checklist

- [ ] Server started successfully
- [ ] Admin user created
- [ ] Successfully logged in
- [ ] Profile dropdown visible
- [ ] Admin Panel option visible
- [ ] Admin panel accessible at `/admin`
- [ ] Dashboard statistics showing
- [ ] All panels visible
- [ ] Real-time updates working
- [ ] Can view users and files
- [ ] Performance chart displaying

## 🎊 You're All Set!

Your admin panel is now fully functional with:
- ✅ Real-time monitoring
- ✅ User management
- ✅ File management  
- ✅ Performance analytics
- ✅ Beautiful UI

**Enjoy your high-speed file sharing system with professional admin tools!** 🚀

---

**Circuvent Technologies - NetShare Pro v2.0**
