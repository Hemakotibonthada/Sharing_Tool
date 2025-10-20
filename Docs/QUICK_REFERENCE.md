# 🚀 Quick Reference - NetShare Pro UI Features

## 📁 File Manager

### View Modes
- **Grid View**: Visual cards with thumbnails
- **List View**: Detailed table layout
- **Toggle**: Click icons in top-right corner

### Actions
| Action | Method |
|--------|--------|
| Upload | Drag & drop anywhere or click "Browse Files" |
| Preview | Click on any file card or filename |
| Download | Click download button or right-click → Download |
| Rename | Right-click → Rename (or use context menu) |
| Delete | Select files → Delete Selected button |
| Share | Click share button or right-click → Share |

### Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + A` | Select all files |
| `Escape` | Deselect all or close modal |
| `Delete` | Delete selected files |

### Filters
- **All Files**: Show everything
- **Images**: JPG, PNG, GIF, etc.
- **Videos**: MP4, AVI, MOV, etc.
- **Documents**: PDF, DOC, TXT, etc.
- **Archives**: ZIP, RAR, 7Z, etc.
- **Others**: Everything else

### Sorting
- Latest First / Oldest First
- Name (A-Z / Z-A)
- Largest First / Smallest First

---

## 📊 Dashboard

### Charts Available
1. **Upload/Download Trends** (Line Chart)
   - Shows last 7 days activity
   - Export as PNG
   
2. **File Type Distribution** (Doughnut Chart)
   - Percentage breakdown
   - 5 categories
   
3. **Transfer Speed History** (Bar Chart)
   - 6 time periods
   - Speed in Mbps
   
4. **Storage Usage** (Gauge)
   - Used vs Available
   - Color-coded warnings
   
5. **User Activity Pattern** (Polar Area)
   - Weekly activity
   - Mon-Sun visualization

### Dashboard Features
- **Theme Toggle**: Switch light/dark mode (top-right)
- **Auto-Refresh**: Updates every 30 seconds
- **Export Charts**: Click export icon on any chart
- **Stat Cards**: Total Files, Users, Storage, Speed

### Accessing Dashboard
- Click "Dashboard" in navigation, OR
- Navigate to: `http://127.0.0.1:5001/dashboard`

---

## 🎨 UI Components

### Progress Indicators

#### Linear Progress Bar
```javascript
const pb = new ProgressBar('containerId', {
    size: 'lg',           // sm, md, lg, xl
    variant: 'success',   // default, success, warning, danger, info
    showLabel: true
});
pb.setProgress(75);       // Set to 75%
pb.reset();               // Reset to 0%
```

#### Circular Progress
```javascript
const cp = new CircularProgress('containerId', { size: 'lg' });
cp.setProgress(50);
```

#### Upload Progress Card
```javascript
const file = { name: 'video.mp4', size: 104857600 }; // 100MB
const card = new UploadProgressCard(file, 'uploadQueue');

// Update progress
card.updateProgress(52428800, 104857600); // 50% done

// Mark complete
card.complete();

// Show error
card.error('Upload failed');
```

### Loading States

#### Loading Overlay
```javascript
// Show
LoadingOverlay.show('Uploading files...', 'Please wait');

// Update
LoadingOverlay.update('Processing...', 'Almost done');

// Hide
LoadingOverlay.hide();
```

#### Skeleton Loaders
```javascript
// File cards
SkeletonLoader.showFileCards('filesGrid', 6);

// Stat cards
SkeletonLoader.showStatCards('statsGrid', 4);

// List items
SkeletonLoader.showList('activityFeed', 5);

// Hide
SkeletonLoader.hide('filesGrid');
```

### Spinners

#### Default Spinner
```html
<div class="spinner lg"></div>
```

#### Dot Spinner
```html
<div class="dot-spinner">
    <span></span>
    <span></span>
    <span></span>
</div>
```

#### Pulse Loader
```html
<div class="pulse-loader"></div>
```

### Step Progress
```javascript
const steps = new StepProgress('container', [
    'Upload',
    'Process',
    'Complete'
]);

steps.next();    // Move to next step
steps.prev();    // Go back
steps.reset();   // Back to first step
```

---

## 🎨 Theming

### Toggle Theme
- Click theme button in dashboard header
- Preference saved automatically

### CSS Variables
```css
:root {
    --color-primary: #667eea;
    --bg-primary: #f5f7fa;
    --text-primary: #2d3748;
}

[data-theme="dark"] {
    --bg-primary: #1a1d2e;
    --text-primary: #e2e8f0;
}
```

### Apply Theme Programmatically
```javascript
document.body.setAttribute('data-theme', 'dark');
localStorage.setItem('theme', 'dark');
```

---

## 🔧 API Endpoints

### File Operations
```bash
# Upload file
POST /upload

# Download file
GET /download/<filename>

# Delete file
DELETE /delete/<filename>

# Rename file (NEW)
POST /rename
Body: { "oldName": "old.txt", "newName": "new.txt" }

# Delete multiple
POST /delete-multiple
Body: { "filenames": ["file1.txt", "file2.txt"] }
```

### Dashboard Data
```bash
# Get dashboard stats
GET /api/dashboard/stats

# Export report
GET /api/export/report
```

### Response Example
```json
{
  "totalFiles": 156,
  "totalUsers": 12,
  "fileTypes": {
    "images": 45,
    "documents": 78,
    "videos": 12
  },
  "uploadTrend": {
    "labels": ["Nov 14", "Nov 15", ...],
    "uploads": [12, 19, 15, ...],
    "downloads": [15, 23, 18, ...]
  }
}
```

---

## 📱 Responsive Breakpoints

| Device | Width | Columns |
|--------|-------|---------|
| Mobile | < 768px | 1 column |
| Tablet | 768px - 1024px | 2 columns |
| Desktop | 1024px - 1440px | 3 columns |
| Large | > 1440px | 4 columns |

---

## 🐛 Troubleshooting

### Charts Not Showing
1. Check browser console for errors
2. Ensure Chart.js CDN loaded
3. Verify `/api/dashboard/stats` returns data

### File Preview Not Working
1. Check file type is supported
2. Ensure file exists on server
3. Check browser console for 404 errors

### Drag & Drop Not Working
1. Ensure JavaScript is enabled
2. Check for browser compatibility
3. Try uploading via "Browse Files" button

### Theme Not Persisting
1. Check localStorage is enabled
2. Clear browser cache
3. Check browser console for errors

---

## 💡 Tips

### Performance
- Use skeleton loaders while fetching data
- Implement pagination for large file lists
- Enable lazy loading for images
- Cache API responses

### User Experience
- Always show loading states
- Provide clear error messages
- Use toast notifications for feedback
- Enable keyboard navigation

### Accessibility
- Add ARIA labels
- Test with keyboard only
- Use semantic HTML
- Provide text alternatives

---

## 📚 Documentation

- [Full UI Features Guide](UI_FEATURES_GUIDE.md)
- [Implementation Complete](UI_IMPLEMENTATION_COMPLETE.md)
- [Desktop App Guide](DESKTOP_APP_GUIDE.md)
- [Quick Start](../QUICK_START.md)

---

## 🎯 Common Use Cases

### Upload Multiple Files
```javascript
// Via drag & drop
// Just drag files to upload area or file grid

// Via JavaScript
const files = document.getElementById('fileInput').files;
Array.from(files).forEach(file => {
    const card = new UploadProgressCard(file, 'uploadQueue');
    // ... upload logic
});
```

### Show Progress During Long Operation
```javascript
LoadingOverlay.show('Processing...', 'This may take a moment');

// Your long operation
await someAsyncOperation();

LoadingOverlay.hide();
```

### Create Custom Progress Indicator
```javascript
const pb = new ProgressBar('myProgress', {
    size: 'xl',
    variant: 'info',
    autoColor: true  // Changes color based on progress
});

// Simulate progress
let progress = 0;
const interval = setInterval(() => {
    progress += 10;
    pb.setProgress(progress);
    
    if (progress >= 100) {
        clearInterval(interval);
    }
}, 500);
```

---

**Quick Reference v1.0** - NetShare Pro  
*All features at your fingertips!* ⚡
