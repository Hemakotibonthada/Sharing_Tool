# NetShare Pro - Architecture Overview

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    NETSHARE PRO                              │
│                Desktop Application                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │     desktop_app.py                │
        │  (Cross-platform Launcher)        │
        │                                   │
        │  • Auto-start Flask server        │
        │  • Find free port                 │
        │  • Open native window/browser     │
        │  • Background thread management   │
        └───────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │   PyQt5 Window   │    │  pywebview       │
    │  (Windows best)  │    │  (Cross-platform)│
    └──────────────────┘    └──────────────────┘
                │                       │
                └───────────┬───────────┘
                            │
                            ▼
                ┌──────────────────────┐
                │   Browser Fallback   │
                │  (Always available)  │
                └──────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │         Flask Server               │
        │       (http://127.0.0.1:5001)     │
        │                                   │
        │  app.py - Main application        │
        └───────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────┐
        │                                   │
        ▼                                   ▼
┌──────────────┐                    ┌──────────────┐
│ Auth System  │                    │ File System  │
│              │                    │              │
│ auth_system  │                    │ uploads/     │
│   .py        │                    │ versions/    │
│              │                    │ temp/        │
│ • bcrypt     │                    │              │
│ • Sessions   │                    │ High-speed   │
│ • Roles      │                    │ WebSocket    │
└──────────────┘                    └──────────────┘
        │                                   │
        ▼                                   ▼
┌──────────────┐                    ┌──────────────┐
│  Security    │                    │   Logging    │
│              │                    │              │
│ security.py  │                    │ logger.py    │
│              │                    │              │
│ • Hashing    │                    │ • App Log    │
│ • Validation │                    │ • Security   │
│ • Headers    │                    │ • Audit      │
│ • Rate Limit │                    │ • Perf       │
└──────────────┘                    └──────────────┘
        │                                   │
        ▼                                   ▼
┌──────────────┐                    ┌──────────────┐
│ Config       │                    │   Data       │
│              │                    │              │
│ config.py    │                    │ data/        │
│ .env         │                    │              │
│              │                    │ • users.json │
│ • Dev/Prod   │                    │ • sessions   │
│ • Settings   │                    │ • files      │
└──────────────┘                    └──────────────┘
```

---

## 🔄 Request Flow

```
User Action
    │
    ▼
┌────────────────┐
│   Browser/     │
│   Native Win   │
└────────────────┘
    │
    ▼
┌────────────────┐
│  Flask Route   │
│  @app.route    │
└────────────────┘
    │
    ├─ Authentication Required?
    │  ├─ Yes ──▶ require_login decorator
    │  │              │
    │  │              ▼
    │  │          Validate Token
    │  │              │
    │  │              ├─ Valid ──▶ Continue
    │  │              └─ Invalid ─▶ Return 401
    │  │
    │  └─ No ──▶ Continue
    │
    ├─ Log Request (Performance Logger)
    │
    ├─ Validate Input (Security Module)
    │
    ├─ Process Request
    │      │
    │      ├─ File Operation?
    │      │      │
    │      │      ├─ Upload ──▶ High-Speed Transfer
    │      │      │                    │
    │      │      │                    ├─ Validate File
    │      │      │                    ├─ Save to uploads/
    │      │      │                    ├─ Update metadata
    │      │      │                    └─ Log Operation
    │      │      │
    │      │      ├─ Download ──▶ Permission Check
    │      │      │                    │
    │      │      │                    ├─ Allowed ──▶ Stream File
    │      │      │                    └─ Denied ──▶ Return 403
    │      │      │
    │      │      └─ Delete ──▶ Permission Check
    │      │                         │
    │      │                         ├─ Owner/Admin ──▶ Delete
    │      │                         └─ Other ──▶ Request Approval
    │      │
    │      └─ Auth Operation?
    │             │
    │             ├─ Login ──▶ Authenticate
    │             │               │
    │             │               ├─ Success ──▶ Create Session
    │             │               │                  │
    │             │               │                  └─ Log Success
    │             │               │
    │             │               └─ Failure ──▶ Log Failure
    │             │
    │             └─ Logout ──▶ Delete Session
    │
    ├─ Log Security Event (if applicable)
    │
    ├─ Log Audit Event (for compliance)
    │
    └─ Return Response
         │
         ▼
    User sees result
```

---

## 📁 Data Flow

```
┌─────────────┐
│   Upload    │
│   Request   │
└─────────────┘
        │
        ▼
    Validate
    • File type
    • File size
    • Permissions
        │
        ▼
    WebSocket
    Transfer
    • 8 parallel chunks
    • 2MB chunk size
    • Binary streaming
        │
        ▼
    Save File
    uploads/filename
        │
        ├─▶ Generate MD5 hash
        │
        ├─▶ Update metadata
        │   data/file_metadata.json
        │
        ├─▶ Create version
        │   file_versions/filename_v1
        │
        └─▶ Log operation
            logs/security.log
            logs/audit.log
```

---

## 🔐 Security Layers

```
┌────────────────────────────────────┐
│  Layer 1: Network Isolation        │
│  • Only accessible on local network│
└────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│  Layer 2: Authentication           │
│  • Session token required          │
│  • bcrypt password hashing         │
└────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│  Layer 3: Authorization            │
│  • Role-based access control       │
│  • Permission checks               │
└────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│  Layer 4: Input Validation         │
│  • Username/password strength      │
│  • File type/size validation       │
│  • Path traversal prevention       │
└────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│  Layer 5: Security Headers         │
│  • Content Security Policy         │
│  • X-Frame-Options                 │
│  • HSTS (if HTTPS)                 │
└────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│  Layer 6: Rate Limiting            │
│  • Login attempt limits            │
│  • Request throttling              │
└────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────┐
│  Layer 7: Audit Logging            │
│  • All actions logged              │
│  • 365-day retention               │
│  • Investigation ready             │
└────────────────────────────────────┘
```

---

## 🔄 Build Process

```
Source Code
    │
    ▼
┌─────────────────┐
│  Build Script   │
│                 │
│  Windows:       │
│  .ps1 script    │
│                 │
│  macOS:         │
│  .sh script     │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  PyInstaller    │
│                 │
│  • Collect deps │
│  • Bundle files │
│  • Create exe   │
└─────────────────┘
    │
    ├─▶ Windows
    │       │
    │       ▼
    │   ┌─────────────┐
    │   │ .exe file   │
    │   │ (standalone)│
    │   └─────────────┘
    │
    └─▶ macOS
            │
            ▼
        ┌─────────────┐
        │ .app bundle │
        │ .dmg (opt)  │
        └─────────────┘
```

---

## 📊 Logging Architecture

```
Application Events
    │
    ├─▶ Application Logger
    │       │
    │       ├─ Level: DEBUG/INFO/WARNING/ERROR
    │       ├─ Rotation: 10MB
    │       └─ Output: logs/app.log
    │
    ├─▶ Security Logger
    │       │
    │       ├─ Events: Login/logout/auth
    │       ├─ Rotation: 10MB
    │       └─ Output: logs/security.log
    │
    ├─▶ Audit Logger
    │       │
    │       ├─ Events: All user actions
    │       ├─ Rotation: Daily
    │       ├─ Retention: 365 days
    │       └─ Output: logs/audit.log
    │
    └─▶ Performance Logger
            │
            ├─ Metrics: Response time, transfer speed
            ├─ Rotation: 50MB
            └─ Output: logs/performance.log

All logs ─▶ JSON format
         ─▶ Structured fields
         ─▶ Easy parsing
```

---

## 🎯 User Roles & Permissions

```
┌─────────────┐
│    Admin    │
│   (Full)    │
└─────────────┘
      │
      ├─▶ Upload files
      ├─▶ Download files
      ├─▶ Delete any file
      ├─▶ Manage users
      ├─▶ Approve delete requests
      ├─▶ View all statistics
      └─▶ Change settings

┌─────────────┐
│    User     │
│  (Standard) │
└─────────────┘
      │
      ├─▶ Upload files
      ├─▶ Download files
      ├─▶ Delete own files
      ├─▶ Request delete (others' files)
      ├─▶ Comment on files
      └─▶ View own statistics

┌─────────────┐
│   Viewer    │
│ (Read-only) │
└─────────────┘
      │
      ├─▶ Download files
      ├─▶ View comments
      └─▶ View file list
```

---

## 🚀 High-Speed Transfer

```
File Upload Request
    │
    ▼
WebSocket Connection
    │
    ├─ Split into 8 chunks (2MB each)
    │
    ├─ Parallel Transfer
    │   │
    │   ├─▶ Chunk 1 ─┐
    │   ├─▶ Chunk 2 ─┤
    │   ├─▶ Chunk 3 ─┤
    │   ├─▶ Chunk 4 ─┼─▶ Server receives
    │   ├─▶ Chunk 5 ─┤   and assembles
    │   ├─▶ Chunk 6 ─┤
    │   ├─▶ Chunk 7 ─┤
    │   └─▶ Chunk 8 ─┘
    │
    ├─ Progress tracking
    │   • Bytes transferred
    │   • Transfer speed
    │   • Time remaining
    │
    └─ Complete
        │
        ├─▶ MD5 verification
        ├─▶ Save to disk
        └─▶ Update metadata

Target Speed: 500+ Mbps
Actual Speed: Depends on network
```

---

## 💾 Data Storage

```
data/
├── users.json
│   └── {
│         "username": {
│           "password": "bcrypt_hash",
│           "role": "admin|user|viewer",
│           "display_name": "Name",
│           "created_at": "ISO8601",
│           "last_login": "ISO8601"
│         }
│       }
│
├── sessions.json
│   └── {
│         "token": {
│           "username": "user",
│           "role": "admin",
│           "created_at": "ISO8601",
│           "expires_at": "ISO8601"
│         }
│       }
│
└── file_metadata.json
    └── {
          "filename": {
            "owner": "username",
            "created_at": "ISO8601",
            "permission": "public|private|restricted",
            "allowed_users": ["user1", "user2"],
            "size": 1024,
            "type": "image/png"
          }
        }
```

---

## 🔧 Configuration Hierarchy

```
1. Environment Variables (.env)
   ↓ (highest priority)
   
2. Config Class (config.py)
   ↓
   
3. Environment Profile
   ├─▶ Development (debug=True)
   ├─▶ Production (debug=False, secure)
   └─▶ Testing (isolated)
   ↓
   
4. Default Values
   (lowest priority)

Loading Process:
1. Check .env file
2. Load config profile
3. Apply environment-specific settings
4. Fall back to defaults
```

---

## 📱 Platform Support

```
┌──────────────────────────────────┐
│        NetShare Pro              │
└──────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
    ▼                   ▼
┌─────────┐         ┌─────────┐
│ Desktop │         │   Web   │
└─────────┘         └─────────┘
    │                   │
    ├─▶ Windows         ├─▶ Any browser
    │   • .exe          │   • Chrome
    │   • PyQt5         │   • Firefox
    │                   │   • Safari
    ├─▶ macOS           │   • Edge
    │   • .app          │
    │   • .dmg          └─▶ Mobile
    │   • webview           • iPhone
    │                       • Android
    └─▶ Linux               • Tablet
        • .AppImage (future)
        • webview
```

---

**This architecture delivers:**
- ✅ Security through multiple layers
- ✅ Performance through optimized transfers
- ✅ Reliability through comprehensive logging
- ✅ Usability through cross-platform support
- ✅ Maintainability through modular design

---

**Made with ❤️ for Circuvent Technologies**
