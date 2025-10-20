# NetShare Pro - Network Connection Troubleshooting Guide

## 🔧 Problem: Cannot Connect from Other Devices

If you can access the server on your computer (localhost) but other devices cannot connect using the IP address or QR code, follow these steps:

---

## ✅ Quick Fixes (Try These First)

### 1. **Use the Enhanced Startup Script**
We've created an improved startup script that automatically configures your firewall:

**Windows:**
- Right-click `START_SERVER.bat` → Select **"Run as Administrator"**
- Or double-click `START_SERVER.ps1` (it will auto-request admin privileges)

This will:
- ✓ Check if port 5001 is available
- ✓ Configure Windows Firewall automatically
- ✓ Show your network IP address
- ✓ Start the server properly

### 2. **Verify Network Connection**
- ✓ Make sure your computer is connected to Wi-Fi or Ethernet
- ✓ Check that other devices are on the **same network**
- ✓ Disable VPN if active (VPNs can block local network access)

### 3. **Check the IP Address**
When the server starts, it shows:
```
📍 SERVER ADDRESSES:
   • Local access:   http://localhost:5001
   • Network access: http://192.168.1.XXX:5001
```

- ✓ Use the **Network access** URL from other devices
- ✓ The IP should start with `192.168.` or `10.` (not `127.0.0.1`)
- ✓ If you see `127.0.0.1`, you're not connected to a network

---

## 🔥 Windows Firewall Configuration

### Automatic Method (Recommended)
Run the server as Administrator using `START_SERVER.bat` or `START_SERVER.ps1`

### Manual Method
If automatic configuration doesn't work:

1. **Open Windows Defender Firewall:**
   - Press `Win + R`
   - Type: `wf.msc`
   - Press Enter

2. **Create Inbound Rule:**
   - Click **"Inbound Rules"** (left panel)
   - Click **"New Rule..."** (right panel)
   - Select **"Port"** → Click Next
   - Select **"TCP"**
   - Enter port: **5001**
   - Click Next
   - Select **"Allow the connection"** → Next
   - Check all profiles (Domain, Private, Public) → Next
   - Name: **"NetShare Pro"**
   - Click Finish

3. **Restart the Server**

---

## 🌐 Network Diagnostics

### Check Your IP Address
Run this in Command Prompt or PowerShell:
```bash
ipconfig
```

Look for **"IPv4 Address"** under your active connection (Wi-Fi or Ethernet):
- ✓ Good: `192.168.1.XXX`, `10.0.0.XXX`, `172.16-31.XXX`
- ✗ Bad: `127.0.0.1` (localhost only), `169.254.XXX` (no network)

### Test Server is Running
Open browser on the server computer:
```
http://localhost:5001
```

If this works but `http://YOUR-IP:5001` doesn't, it's a firewall issue.

### Check Port is Listening
Run in PowerShell:
```powershell
netstat -an | findstr :5001
```

You should see:
```
TCP    0.0.0.0:5001    0.0.0.0:0    LISTENING
```

If not, the server isn't running properly.

---

## 📱 Mobile Device Connection

### From Another Device:
1. **Connect to Same Wi-Fi** as the computer running NetShare Pro
2. **Open Browser** (Chrome, Safari, Firefox, etc.)
3. **Enter the Network URL:**
   ```
   http://192.168.1.XXX:5001
   ```
   Replace `XXX` with the actual IP shown when server started

### Using QR Code:
1. Start the server
2. Open the **Network** tab on the server's browser
3. Scan the QR code with your mobile device
4. It will automatically open the correct URL

---

## 🚫 Common Issues and Solutions

### Issue 1: "This site can't be reached" or "Connection refused"

**Cause:** Windows Firewall is blocking the connection

**Solution:**
1. Run server as Administrator
2. Or manually configure firewall (see above)
3. Temporarily disable firewall to test:
   - Open Windows Security → Firewall → Turn off (for testing only!)
   - If it works, the firewall was the issue
   - Turn firewall back on and configure properly

### Issue 2: IP Address shows `127.0.0.1`

**Cause:** Not connected to a network

**Solution:**
1. Connect to Wi-Fi or plug in Ethernet cable
2. Restart the server
3. Check `ipconfig` to verify you have a network IP

### Issue 3: Port 5001 already in use

**Cause:** Another application is using port 5001

**Solution:**
1. Close other web servers (XAMPP, WAMP, etc.)
2. Find what's using the port:
   ```powershell
   netstat -ano | findstr :5001
   ```
3. Kill the process using Task Manager
4. Or change NetShare Pro to use a different port (edit `app.py`, line 1723)

### Issue 4: Works on home Wi-Fi but not work/school network

**Cause:** Corporate/school networks often block device-to-device connections

**Solution:**
1. This is a security feature of the network
2. Ask IT department to allow local connections
3. Or use a personal hotspot from your phone
4. Connect both devices to the phone's hotspot

### Issue 5: Firewall rule won't add (Access Denied)

**Cause:** Script not running as Administrator

**Solution:**
1. **Right-click** `START_SERVER.bat`
2. Select **"Run as Administrator"**
3. Click "Yes" on the UAC prompt

---

## 🔍 Advanced Troubleshooting

### Check Server Logs
Look at the terminal/PowerShell window where the server is running for any error messages.

### Test with cURL (from another device)
Install cURL or use Git Bash:
```bash
curl http://192.168.1.XXX:5001
```

If you get HTML back, the server is reachable.

### Disable Antivirus Temporarily
Some antivirus software blocks local servers. Try disabling it temporarily to test.

### Check Router Settings
- Some routers have "AP Isolation" or "Client Isolation" enabled
- This prevents devices from talking to each other
- Check router settings and disable isolation

### Use Network Scanner
Download a network scanner app on your mobile device:
- **Fing** (iOS/Android)
- **Network Analyzer** (iOS)
- **PingTools** (Android)

Scan your network to verify:
1. Your computer shows up
2. Port 5001 is open on your computer's IP

---

## ✅ Verification Checklist

Before asking for help, verify:

- [ ] Server starts without errors
- [ ] You can access `http://localhost:5001` on the server computer
- [ ] Your computer has a valid network IP (not 127.0.0.1)
- [ ] Other device is on the **same Wi-Fi network**
- [ ] Windows Firewall rule for port 5001 exists
- [ ] You're using the correct IP address (check what server printed)
- [ ] Port 5001 is not blocked by antivirus
- [ ] No VPN is active on either device

---

## 📧 Still Having Issues?

If you've tried everything above and still can't connect:

1. **Take a screenshot** of:
   - The server startup messages (showing IP address)
   - The error message on the other device
   - Output of `ipconfig` on server computer

2. **Provide details:**
   - Operating system versions (server and client)
   - Network type (home Wi-Fi, work network, hotspot, etc.)
   - Exact error message
   - What troubleshooting steps you've tried

3. **Check firewall logs:**
   - Windows Security → Firewall → Advanced settings
   - Monitoring → Firewall logs
   - Look for blocked connections to port 5001

---

## 🎯 Success Indicators

You'll know it's working when:
- ✅ Server shows: `0.0.0.0:5001` in the startup message
- ✅ You can access from localhost
- ✅ Other devices can reach `http://YOUR-IP:5001`
- ✅ QR code scanning opens the page immediately
- ✅ Files upload and download successfully
- ✅ Network tab shows connected devices

---

**Remember:** The most common issue is Windows Firewall blocking port 5001. Using the provided `START_SERVER.bat` or `START_SERVER.ps1` scripts as Administrator will fix this automatically!
