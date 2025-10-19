# NetShare Pro - Advanced Cross-Platform File Sharing

A professional, high-performance file sharing application with maximum transfer speeds and advanced features. Works seamlessly across Windows, macOS, iPhone, and Android devices on the same WiFi network.

## ✨ Key Features

### 🚀 Performance & Speed
- ⚡ **Maximum Transfer Speed**: 8MB chunked streaming for optimal performance
- 🔄 **Parallel Uploads**: Upload up to 5 files simultaneously with intelligent queue management
- 📊 **Real-time Speed Monitoring**: Live transfer speeds (B/s, KB/s, MB/s, GB/s) for each file
- 💾 **Massive File Support**: Upload files up to 1TB (1000GB) per file

### 📦 Bulk Operations
- 📥 **Bulk Download**: Download multiple files as a single ZIP archive
- 📤 **Bulk Upload**: Upload multiple files at once with automatic queueing
- ✅ **Bulk Delete**: Select and delete multiple files in one action
- 🧹 **Clear All**: Remove all files with one click

### 🎨 Modern UI/UX
- 🌐 **Cross-Platform**: Works on Windows, macOS, Linux, iOS, and Android
- 🎨 **Glass-morphism Design**: Beautiful modern UI with smooth animations
- 📱 **QR Code Access**: Easily connect mobile devices by scanning QR code
- 🔄 **Drag & Drop**: Simple drag-and-drop file uploads
- 🎯 **Smart File Management**: Filter, sort, search, and preview files

### 🛡️ Advanced Features
- 🔐 **File Integrity**: MD5 hash verification for uploaded files
- � **Upload Queue**: Automatic queue management for many files
- 🎨 **File Preview**: Preview images and videos directly in browser
- 🔍 **Smart Search**: Find files quickly with instant search
- 📂 **File Filters**: Filter by images, videos, documents, archives, and more
- 🔒 **Network Isolated**: Only accessible on your local network

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- All devices must be connected to the same WiFi network

### Installation

1. Install required Python packages:
```powershell
pip install -r requirements.txt
```

### Running the Application

1. Start the server:
```powershell
python app.py
```

2. The server will display:
   - Local URL (for the host computer)
   - Network URL (for other devices)
   - Shared files location

3. Access the application:
   - **On the same computer**: Open `http://localhost:5001`
   - **On other devices**: Open the network URL shown (e.g., `http://192.168.1.100:5001`)
   - **On mobile**: Scan the QR code displayed on the webpage

## 📖 Usage

### Uploading Files

#### Single or Multiple Files
1. **Drag & Drop**: Simply drag files into the upload area
2. **Browse**: Click "Browse Files" to select multiple files from your device
3. **Progress**: Watch real-time upload progress with live transfer speeds
4. **Parallel Processing**: Up to 5 files upload simultaneously, others queue automatically

#### Upload Queue Features
- Individual progress bars for each file
- Real-time transfer speed for active uploads (KB/s, MB/s, GB/s)
- Color-coded status: Blue (uploading), Green (complete), Red (failed)
- Automatic queue management when uploading many files

### Downloading Files

#### Single File
1. Click the "Download" button on any file card
2. File downloads to your default downloads folder

#### Multiple Files (Bulk Download)
1. Check the boxes next to files you want to download
2. Click "Download Selected" button at the top
3. Multiple files automatically download as a single ZIP archive
4. Single selected file downloads directly (no ZIP)

### Managing Files

#### Bulk Actions
- **Download Selected**: Download one or many files (auto-ZIP for multiple)
- **Delete Selected**: Delete multiple files at once
- **Clear All**: Remove all files from server (requires confirmation)
- **Selection Counter**: Shows how many files are currently selected

#### File Organization
- **Filter**: Click filter buttons (All, Images, Videos, Documents, Archives, Others)
- **Sort**: Sort by date, name, or size (ascending/descending)
- **Search**: Use the search bar to find files instantly
- **Views**: Toggle between grid and list view

### Deleting Files

1. **Single File**: Click the "Delete" button on any file card
2. **Multiple Files**: Select files with checkboxes, click "Delete Selected"
3. **All Files**: Click "Clear All" button (requires confirmation)
4. Deleted files are permanently removed from the server

### Accessing from Mobile Devices

1. Open the web interface on your computer
2. Scan the QR code with your phone's camera
3. Your phone's browser will open the file sharing interface
4. Upload/download files just like on desktop

## 🎨 Features Explained

### Network Access Card
- Shows the server URL
- Displays QR code for easy mobile access
- Copy URL button for sharing

### Upload Area
- Drag and drop files directly
- Browse button for traditional file selection
- Visual feedback when dragging files
- Progress bar with percentage

### Files Grid
- Cards showing all shared files
- File icons based on file type
- File size and modification date
- Download and delete actions
- Smooth hover animations

### Toast Notifications
- Success/error messages
- Auto-dismiss after 3 seconds
- Non-intrusive design

## 🔧 Configuration

### Change Port
Edit `app.py` and modify the port number:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Change Upload Folder
Edit `app.py` and modify the upload folder:
```python
UPLOAD_FOLDER = 'shared_files'
```

### Change Max File Size
Edit `app.py` and modify the max file size (in bytes):
```python
MAX_FILE_SIZE = 1024 * 1024 * 1024 * 1024  # 1TB (default)
```

### Adjust Parallel Upload Limit
Edit `static/script.js` and modify:
```javascript
const MAX_PARALLEL_UPLOADS = 5; // Upload 5 files simultaneously
```

### Change Chunk Size (for speed optimization)
Edit `app.py` and modify:
```python
CHUNK_SIZE = 8192 * 1024  # 8MB chunks (default, optimal for most networks)
```

## 🛡️ Security Notes

- The server is only accessible on your local network
- No authentication is implemented (suitable for trusted networks)
- Files are stored unencrypted in the `shared_files` folder
- For public/untrusted networks, consider adding authentication

## 🎯 Supported File Types

The application supports **all file types** up to 1TB, with special features for:

### With Preview Support
- 🖼️ **Images**: JPG, PNG, GIF, BMP, WebP (in-browser preview)
- � **Videos**: MP4, WebM, OGG (in-browser preview)

### With Special Icons & Filtering
- 📄 **Documents**: PDF, Word, Excel, PowerPoint, TXT
- � **Audio**: MP3, WAV, FLAC, AAC
- 📦 **Archives**: ZIP, RAR, 7z, TAR, GZ
- 💿 **Disk Images**: ISO, IMG
- 💻 **Code**: JS, PY, HTML, CSS, JSON, etc.
- 📝 **Text**: TXT, MD, LOG, etc.

### File Integrity
- MD5 hash verification available via file info endpoint
- Access at: `/file-info/<filename>` for detailed metadata

## 🌟 Technologies Used

### Backend
- **Framework**: Flask 3.0.0 with Werkzeug
- **File Handling**: Chunked streaming (8MB chunks)
- **Compression**: Zipfile with ZIP_DEFLATED
- **Security**: MD5 hashing, thread-safe operations
- **QR Codes**: qrcode 7.4.2 with Pillow 10.1.0

### Frontend
- **Core**: HTML5, CSS3, Vanilla JavaScript (ES6+)
- **Design**: Glass-morphism effects, CSS Grid, Flexbox
- **Icons**: Font Awesome 6.4.0
- **Features**: Drag & Drop API, File API, Fetch API, FormData

### Performance
- **Threading**: Thread-safe statistics with mutex locks
- **Streaming**: HTTP chunked transfer encoding
- **Parallel**: Up to 5 concurrent uploads
- **Memory**: Efficient streaming (no full file loading)

## 🐛 Troubleshooting

### Can't access from other devices
- Ensure all devices are on the same WiFi network
- Check firewall settings (allow Python/port 5001)
- Verify the IP address is correct

### Upload fails
- Check file size (must be under 1TB by default)
- Ensure sufficient disk space on server
- Check folder permissions for `shared_files/`
- If parallel uploads fail, try reducing `MAX_PARALLEL_UPLOADS`

### Server won't start
- Verify Python is installed correctly
- Check if port 5001 is already in use
- Install required packages: `pip install -r requirements.txt`

## 📝 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Feel free to fork, modify, and improve this project!

## 📊 What's New in Version 2.0

### Major Features
- ✅ Parallel upload queue (5 simultaneous uploads)
- ✅ Real-time transfer speed display (B/s to GB/s)
- ✅ Bulk download as ZIP archive
- ✅ File integrity checking with MD5 hash
- ✅ Clear all files function
- ✅ Transfer status monitoring endpoint
- ✅ Enhanced bulk actions UI
- ✅ 8MB chunked streaming for optimal speed
- ✅ Thread-safe statistics tracking
- ✅ Increased max file size to 1TB

### UI/UX Improvements
- New bulk action buttons (Download Selected, Delete Selected, Clear All)
- Selection counter showing number of selected files
- Individual file upload speeds
- Color-coded upload status indicators
- Glass-morphism design enhancements
- Responsive design improvements

### Performance Enhancements
- 8MB chunk size for maximum transfer speed
- Parallel upload processing
- Memory-efficient streaming
- Optimized download with HTTP range support
- Real-time transfer speed calculation

---

**NetShare Pro** - Made with ❤️ for seamless, high-speed file sharing across all your devices

**Version**: 2.0 Advanced  
**License**: Open Source  
**Server**: Flask 3.0.0 | Python 3.13+  
**Max File Size**: 1TB  
**Parallel Uploads**: 5 simultaneous

## 🚀 Advanced Features

### API Endpoints

The application provides several REST API endpoints:

#### File Operations
- `GET /` - Main web interface
- `GET /files` - List all files (JSON)
- `POST /upload` - Upload single file
- `POST /bulk-upload` - Upload multiple files
- `GET /download/<filename>` - Download file
- `POST /bulk-download` - Download multiple files as ZIP
- `POST /delete/<filename>` - Delete single file
- `POST /delete-multiple` - Delete multiple files
- `POST /clear-all` - Delete all files

#### Information & Stats
- `GET /stats` - Get upload/download statistics
- `GET /file-info/<filename>` - Get file metadata with MD5 hash
- `GET /transfer-status` - Get real-time transfer speeds

### Performance Tips

#### Maximum Upload Speed
1. Use wired Ethernet connection when possible (faster than WiFi)
2. Upload multiple files to leverage parallel uploads (up to 5 simultaneous)
3. Close other network-intensive applications
4. Ensure server has SSD storage for better I/O performance

#### Maximum Download Speed
1. Use bulk download for multiple files (ZIP compression reduces transfer time)
2. Download during off-peak network hours
3. Use wired connection on both server and client
4. Ensure sufficient RAM on server for concurrent operations

#### Large File Transfers (>1GB)
1. Chunked streaming automatically manages memory (no crashes)
2. Monitor transfer speed via real-time indicators
3. Avoid interrupting transfers (resume not yet in UI)
4. Verify file integrity using `/file-info` endpoint after transfer

### Dashboard Features

The dashboard provides:
- **Total Files**: Count of all shared files
- **Storage Used**: Current disk space used (out of 1TB available)
- **Uploads**: Total number of successful uploads
- **Downloads**: Total number of downloads
- **Quick Actions**: Fast access to common operations
- **Recent Files**: Shows latest uploaded files

## 🎯 Use Cases

### Personal Use
- Share photos from phone to computer
- Transfer videos between devices
- Quick file exchange between laptop and desktop
- Access files from any device on home network

### Professional Use
- Share presentations in meetings
- Distribute files to team members on same network
- Quick collaboration without cloud services
- Office file sharing without external dependencies

### Development & Testing
- Transfer builds between development machines
- Share test files with QA team
- Quick log file sharing
- Database dumps and backups transfer
