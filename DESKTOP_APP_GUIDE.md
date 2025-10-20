# NetShare Pro - Desktop Application Guide

## 🚀 Quick Start

### Running the Desktop Application (Development Mode)

```bash
# Install dependencies
pip install -r requirements.txt

# Run the desktop app
python desktop_app.py
```

The application will:
1. ✅ Start Flask server automatically
2. ✅ Open in your default browser (or native window if PyQt5/webview installed)
3. ✅ Run on port 5001 (or find next available port)

### Default Login
- **Username:** `admin`
- **Password:** `admin123`

⚠️ **Change these credentials immediately after first login!**

---

## 📦 Building Standalone Applications

### Windows (.exe)

#### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- PowerShell

#### Build Steps

```powershell
# Run the build script
.\build_windows_app.ps1
```

The script will:
1. Install PyInstaller and dependencies
2. Clean previous builds
3. Create standalone `.exe` file
4. Package everything in `NetShare_Pro_Windows` folder

#### Output
- 📁 `NetShare_Pro_Windows/`
  - 📄 `NetShare Pro.exe` - Standalone application
  - 📄 `INSTALLATION.txt` - Installation guide
  - 📄 `.env.example` - Configuration template
  - 📄 `README.md` - Project documentation

#### Distribution
Simply zip the `NetShare_Pro_Windows` folder and share it. Users can run `NetShare Pro.exe` directly - no Python required!

---

### macOS (.app)

#### Prerequisites
- macOS 10.15 (Catalina) or higher
- Python 3.8 or higher
- Xcode Command Line Tools

#### Build Steps

```bash
# Make script executable
chmod +x build_macos_app_v2.sh

# Run the build script
./build_macos_app_v2.sh
```

The script will:
1. Install PyInstaller and dependencies
2. Clean previous builds
3. Create `.app` bundle
4. Optionally create `.dmg` installer
5. Package everything

#### Output
- 📁 `NetShare_Pro_macOS/`
  - 📱 `NetShare Pro.app` - macOS application bundle
  - 📄 `INSTALLATION.txt` - Installation guide
  - 📄 `.env.example` - Configuration template
- 💿 `NetShare_Pro_macOS.dmg` - Disk image installer

#### Distribution
Share either:
1. The `.app` file directly
2. The `.dmg` installer (recommended)

#### First Run on macOS
macOS Gatekeeper may block the app on first run:
1. Right-click `NetShare Pro.app`
2. Select "Open"
3. Click "Open" in the dialog
4. Or go to System Preferences > Security & Privacy > General > Click "Open Anyway"

---

## 🎨 Desktop Application Features

### Native Window Options

The desktop app tries multiple approaches (in order):

1. **PyQt5** (Windows) - Full-featured browser engine
   ```bash
   pip install PyQt5 PyQtWebEngine
   ```

2. **pywebview** (Windows/macOS/Linux) - Lightweight native window
   ```bash
   pip install pywebview
   ```

3. **Browser Fallback** - Opens in default web browser
   - No additional installation needed
   - Works everywhere

### Auto-Port Selection
If port 5001 is busy, the app automatically finds the next available port (5002, 5003, etc.)

### Background Server
Flask server runs in a background thread, so closing the window stops the server.

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and customize:

```bash
# Security
SECRET_KEY=your-secret-key-here

# Server
HOST=127.0.0.1
PORT=5001
DEBUG=False

# File Storage
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=1099511627776  # 1TB

# Features
ENABLE_HIGH_SPEED=True
ENABLE_FILE_VERSIONING=True
```

### Generate Secret Key

```python
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```

---

## 📁 File Structure (Desktop App)

```
NetShare Pro/
├── desktop_app.py          # Desktop launcher
├── app.py                  # Flask application
├── auth_system.py          # Authentication (bcrypt)
├── security.py             # Security utilities
├── logger.py               # Logging system
├── config.py               # Configuration
├── high_speed_transfer.py  # WebSocket transfers
├── requirements.txt        # Python dependencies
├── .env                    # Configuration (create from .env.example)
├── data/                   # User & session data
│   ├── users.json
│   ├── sessions.json
│   └── file_metadata.json
├── uploads/                # Uploaded files
├── logs/                   # Application logs
├── static/                 # CSS, JS, images
└── templates/              # HTML templates
```

---

## 🔧 Troubleshooting

### Application Won't Start

**Problem:** Double-clicking `.exe` or `.app` does nothing

**Solutions:**
1. Run from command line to see errors:
   ```bash
   # Windows
   .\NetShare Pro.exe
   
   # macOS
   open NetShare\ Pro.app
   ```

2. Check if port 5001 is already in use:
   ```bash
   # Windows
   netstat -ano | findstr :5001
   
   # macOS/Linux
   lsof -i :5001
   ```

3. Check logs in `logs/` folder

### Firewall Blocking

**Problem:** Can't access from browser

**Solutions:**
1. Allow app through Windows Firewall
2. Check antivirus settings
3. Try running as administrator (Windows)

### macOS "Damaged" Error

**Problem:** "App is damaged and can't be opened"

**Solution:**
```bash
# Remove quarantine attribute
xattr -cr "/Applications/NetShare Pro.app"
```

### Build Errors

**Problem:** PyInstaller build fails

**Solutions:**
1. Update PyInstaller:
   ```bash
   pip install --upgrade pyinstaller
   ```

2. Clear PyInstaller cache:
   ```bash
   pyinstaller --clean --noconfirm desktop_app.py
   ```

3. Install missing dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🔒 Security Notes

### Password Security
- ✅ Now uses **bcrypt** (secure)
- ✅ Automatic migration from old SHA-256 hashes
- ✅ Password strength validation enforced

### Default Admin
**IMPORTANT:** Change default admin password immediately!

```python
# In the app, go to:
Settings → Change Password
```

### Session Security
- Sessions expire after 7 days
- Secure session cookies enabled
- HTTPS recommended for production

---

## 📊 Performance

### High-Speed Transfer System
- **Target:** 500+ Mbps
- **Method:** WebSocket with binary streaming
- **Parallel Chunks:** 8 simultaneous transfers
- **Chunk Size:** 2MB (optimized)

### Resource Usage
- **RAM:** ~100-200MB (idle)
- **CPU:** <5% (idle), varies with transfers
- **Disk:** Based on uploaded files

---

## 🎯 Features

### Core Features
- ✅ High-speed file transfers (500+ Mbps)
- ✅ Multi-user authentication with roles
- ✅ Admin panel with real-time monitoring
- ✅ File versioning system
- ✅ Text sharing
- ✅ QR code for mobile access
- ✅ File permissions (public/private/restricted)
- ✅ Delete requests with approval workflow

### Security Enhancements
- ✅ bcrypt password hashing
- ✅ Input validation (username, password, files)
- ✅ Security headers
- ✅ Audit logging
- ✅ Session management

### Admin Features
- 👥 User management (create/delete/role assignment)
- 📊 Real-time statistics
- 📁 File management
- 🔒 Permission control
- ✅ Delete request approval

---

## 🌐 Access Methods

### Local Access
```
http://127.0.0.1:5001
```

### Network Access
```
http://<your-ip-address>:5001
```

Get your IP:
```bash
# Windows
ipconfig

# macOS/Linux
ifconfig
```

### Mobile Access
1. Scan QR code displayed in app
2. Or manually enter IP address
3. Login with credentials

---

## 📱 User Roles

### Admin
- Full access to everything
- User management
- Delete any file
- Approve delete requests
- View all statistics

### User
- Upload files
- Download files
- Delete own files
- Request delete (for others' files)
- Comment on files

### Viewer
- Download files only
- View comments
- No upload/delete permissions

---

## 🔄 Upgrade from Web Version

If you were running the web version (python app.py):

1. **Stop the web server**
2. **Backup your data:**
   ```bash
   cp -r data data_backup
   cp -r uploads uploads_backup
   ```

3. **Run desktop app:**
   ```bash
   python desktop_app.py
   ```

All data is preserved! Your users, sessions, and files remain intact.

---

## 💡 Tips & Best Practices

### For Administrators
1. 🔑 Change default admin password immediately
2. 📝 Create separate accounts for each user
3. 🗑️ Set up regular backups of `data/` folder
4. 📊 Monitor logs in `logs/` folder
5. 🔒 Use HTTPS in production (see deployment docs)

### For Users
1. 📁 Use descriptive file names
2. 🏷️ Set appropriate file permissions
3. 💬 Add comments for team collaboration
4. 📦 Use file versioning for important files
5. 🔄 Check for updates regularly

### For Developers
1. 📖 Read `AUDIT_REPORT.md` for security details
2. 🛠️ Follow `IMPLEMENTATION_GUIDE.md` for customization
3. 🧪 Run tests: `python test_modules.py`
4. 📝 Check logs for debugging
5. 🔍 Use audit logs for investigating issues

---

## 📚 Additional Documentation

- 📋 [AUDIT_REPORT.md](AUDIT_REPORT.md) - Comprehensive security audit
- 🛠️ [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Integration guide
- ⚡ [ENHANCEMENTS_SUMMARY.md](ENHANCEMENTS_SUMMARY.md) - What's new
- 📑 [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - All docs index

---

## 🆘 Getting Help

### Check Logs
```
logs/
├── app.log          # General application logs
├── security.log     # Security events
├── audit.log        # Audit trail
└── performance.log  # Performance metrics
```

### Common Issues
1. **Port already in use** - App finds next available port automatically
2. **Permission denied** - Run as administrator (Windows) or check file permissions
3. **Can't connect** - Check firewall settings
4. **Slow transfers** - Check network connection and antivirus

### Report Issues
- GitHub: [https://github.com/Hemakotibonthada/Sharing_Tool](https://github.com/Hemakotibonthada/Sharing_Tool)
- Include: OS, Python version, error logs

---

## 🎉 What's Next?

### Planned Features (see todo list)
- 🌙 Dark mode
- ♿ Accessibility improvements
- 📱 Progressive Web App (PWA)
- 🔐 Two-factor authentication (2FA)
- 🔑 OAuth integration
- 🗄️ Database migration (SQLite/PostgreSQL)
- 📧 Email notifications
- 🔍 Advanced search
- 🎨 Customizable themes

### Contributing
Contributions welcome! See `IMPLEMENTATION_GUIDE.md` for development setup.

---

## 📄 License

See LICENSE file for details.

---

## 👏 Acknowledgments

Built with:
- Flask - Web framework
- Socket.IO - Real-time communication
- bcrypt - Password hashing
- PyInstaller - App bundling
- And many more awesome open-source projects!

---

**Made with ❤️ for Circuvent Technologies**

**Happy Sharing! 🚀**
