# 🚀 NetShare Pro - Quick Start Card

## Starting the Server

### Windows (Recommended Method)
```batch
# Right-click → "Run as Administrator"
START_SERVER.bat
```

This will automatically:
- ✅ Configure Windows Firewall
- ✅ Check port availability
- ✅ Show your network IP
- ✅ Start the server

### Alternative Methods
```bash
# PowerShell (auto-requests admin)
START_SERVER.ps1

# Manual
python start_server.py

# Direct (basic)
python app.py
```

---

## Accessing the Server

### From Your Computer
```
http://localhost:5001
```

### From Other Devices (Phone, Tablet, etc.)
```
http://YOUR-IP-ADDRESS:5001
```

**Example:**
```
http://192.168.1.105:5001
```

> **Note:** Your actual IP address is shown when the server starts

### Using QR Code
1. Start the server on your computer
2. Go to the **Network** tab
3. Scan the QR code with your phone
4. Browser opens automatically!

---

## Default Login
```
Username: admin
Password: admin123
```

Change these in `app.py` (search for `AUTH_USERNAME`)

---

## Troubleshooting

### ❌ Can't connect from phone/other device?

**Most likely:** Windows Firewall is blocking port 5001

**Solution:** Run `START_SERVER.bat` as Administrator (right-click)

### ❌ Port already in use?

Another app is using port 5001. Check what's using it:
```powershell
netstat -ano | findstr :5001
```

### ❌ Server won't start?

1. Make sure Python is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### ❌ IP shows 127.0.0.1?

You're not connected to a network. Connect to Wi-Fi or Ethernet and restart.

---

## Features Quick Reference

### Upload
- Drag & drop files
- Or click "Choose Files"
- Supports files up to 1TB
- Parallel uploads (5 at a time)

### Download
- Click file name to download
- Click ⬇ icon for direct download
- Select multiple → Download as ZIP

### Organize
- Create folders
- Rename files/folders
- Move files between folders
- Delete files/folders

### Share
- Generate share links
- Set expiration dates
- Password protect
- Track downloads

### Permissions
- Public: Everyone can access
- Private: Only you
- Restricted: Specific users only

---

## Network Setup Checklist

- [ ] Server running on computer
- [ ] Windows Firewall configured (run as Admin)
- [ ] Other device on **same Wi-Fi network**
- [ ] Using network IP (not 127.0.0.1)
- [ ] No VPN active
- [ ] Correct URL: `http://IP:5001`

---

## File Locations

```
WorkSpace/FileShare/
├── uploads/          # Your uploaded files
├── data/             # User data, sessions
├── logs/             # Server logs
└── static/           # Web interface files
```

---

## Common Commands

**Check server status:**
```powershell
netstat -an | findstr :5001
```

**See your IP:**
```powershell
ipconfig
```

**Kill process on port 5001:**
```powershell
# Find PID
netstat -ano | findstr :5001

# Kill it (replace 1234 with actual PID)
taskkill /PID 1234 /F
```

**Reinstall dependencies:**
```bash
pip install -r requirements.txt --force-reinstall
```

---

## Performance Tips

- **Fastest uploads:** Use Chrome or Edge browser
- **Large files:** Enable resumable uploads in settings
- **Multiple files:** Queue uploads, they'll process automatically
- **Network speed:** Use Ethernet instead of Wi-Fi on server
- **Mobile upload:** Use the phone's browser, not file manager

---

## Security Notes

- 🔒 Only use on **trusted networks** (home Wi-Fi)
- 🔑 Change default password immediately
- 🚫 Don't expose to internet without proper security
- 🔐 Enable authentication in production
- 📝 Check logs regularly for suspicious activity

---

## Getting Help

1. **Read:** [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md)
2. **Check:** Server console for error messages
3. **Verify:** Firewall settings in Windows
4. **Test:** Can you access localhost:5001?
5. **Confirm:** Both devices on same network

---

## Support

**Common Issues:** See [NETWORK_TROUBLESHOOTING.md](NETWORK_TROUBLESHOOTING.md)

**Full Documentation:** See [README.md](README.md)

**Advanced Features:** See [Docs/](Docs/) folder

---

**Version:** 2.0
**Port:** 5001
**Protocol:** HTTP (HTTPS optional)

**Made with ❤️ by Circuvent Technologies**
