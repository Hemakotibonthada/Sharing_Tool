# 🚀 NetShare Pro - Ready to Use!

## Quick Start (3 Options)

### Option 1: macOS App Bundle (Recommended)
**Location**: `dist/NetSharePro.app`

**Steps**:
1. Open the `dist` folder
2. Double-click `NetSharePro.app`
3. Browser opens automatically to http://localhost:5001
4. Start sharing files!

**Optional**: Drag `NetSharePro.app` to your Applications folder for permanent installation

---

### Option 2: Simple Double-Click Launcher
**File**: `Start NetShare Pro.command`

**Steps**:
1. Double-click `Start NetShare Pro.command`
2. Terminal opens and server starts
3. Browser opens automatically to http://localhost:5001
4. Start sharing files!

**Note**: First time you may need to right-click → Open to bypass security

---

### Option 3: Traditional Python Method
```bash
python3 app.py
```
Then open http://localhost:5001 in your browser

---

## 📱 Access from Other Devices

Once running, access from any device on your network:

**On the same computer**: http://localhost:5001

**From other devices**: http://192.168.1.5:5001
(The exact IP is shown when the server starts)

**Mobile QR Code**: Scan the QR code shown in the Network tab

---

## 🔐 Login Credentials

**Username**: admin  
**Password**: admin123

(Change these in the settings after first login)

---

## ✨ Features

- ✅ Upload files up to 1TB
- ✅ High-speed transfers (WebSocket)
- ✅ File permissions (Public/Private/Restricted)
- ✅ Text sharing
- ✅ QR code access for mobile
- ✅ Multi-device support
- ✅ Automatic browser opening

---

## 🛑 To Stop

- **App Bundle**: Close the Terminal window that opened
- **Command File**: Press Ctrl+C in the terminal
- **Python Method**: Press Ctrl+C in the terminal

---

## 📦 What's Included

- `NetSharePro.app` - Standalone macOS application
- `Start NetShare Pro.command` - Simple launcher script
- All server files and dependencies
- Full web interface
- Documentation in `Docs/` folder

---

## 🔧 Rebuilding the App

If you make changes to the code:

```bash
./build_macos_app.sh
```

This recreates the `NetSharePro.app` bundle.

---

## 💡 Tips

1. **First Launch**: macOS may show "unverified developer" warning
   - Right-click → Open instead of double-click
   - Or: System Preferences → Security → "Open Anyway"

2. **Firewall**: If others can't access, check macOS Firewall settings
   - System Preferences → Security → Firewall → Allow Python

3. **Port Already in Use**: 
   - Kill other apps using port 5001
   - Or edit app.py to change the port number

4. **Python Not Found**: 
   - Install Python 3 from python.org
   - Or use Homebrew: `brew install python3`

---

## 📞 Support

For issues or questions, check the documentation in the `Docs/` folder:
- `FILE_PERMISSIONS.md` - Permission system guide
- `1TB_FILE_SUPPORT.md` - Large file upload details
- `LARGE_FILE_UPLOAD_FIX.md` - Technical details
- `PERMISSION_UPLOAD_FIX.md` - Permission fixes

---

**Enjoy NetShare Pro! 🎉**
