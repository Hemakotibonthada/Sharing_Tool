# Download Progress UI - Visual Guide

## What You'll See

When you download a file, a sleek progress panel will appear in the bottom-right corner of your screen:

```
┌─────────────────────────────────────────────┐
│  📥 document.pdf              ⏸ ✕          │
│  Downloading...                             │
│  ████████████████░░░░░░░░░░░  45.2%        │
│  45.2%         2.5 MB/s    45 MB / 100 MB  │
└─────────────────────────────────────────────┘
```

### Layout Breakdown:

1. **Header Row**
   - 📥 Download icon
   - Filename (truncated if too long)
   - ⏸ Pause button (to pause download)
   - ✕ Cancel button (to abort download)

2. **Status Row**
   - Shows current state: "Preparing...", "Downloading...", "Paused", "Complete", "Interrupted"
   - Special badges for resuming downloads

3. **Progress Bar**
   - Animated gradient fill (purple to blue)
   - Shimmer effect while downloading
   - Turns green when complete

4. **Details Row**
   - **Percentage**: Exact progress (e.g., 45.2%)
   - **Speed**: Current download speed (e.g., 2.5 MB/s)
   - **Size**: Downloaded vs Total (e.g., 45 MB / 100 MB)

## States

### 1. Active Download
```
┌─────────────────────────────────────────────┐
│  📥 large-video.mp4           ⏸ ✕          │
│  🔄 Downloading...                          │
│  ██████████████████████░░░░░  78.3%        │
│  78.3%         5.2 MB/s   392 MB / 500 MB  │
└─────────────────────────────────────────────┘
```

### 2. Paused
```
┌─────────────────────────────────────────────┐
│  📥 large-video.mp4                         │
│  ⏸ Paused                                   │
│  ██████████████████████░░░░░  78.3%        │
│  78.3%         --          392 MB / 500 MB │
│  ▶ Resume                            ✕     │
└─────────────────────────────────────────────┘
```

### 3. Resuming
```
┌─────────────────────────────────────────────┐
│  📥 large-video.mp4           ⏸ ✕          │
│  ▶ Resuming...                              │
│  ██████████████████████░░░░░  78.3%        │
│  78.5%         4.8 MB/s   393 MB / 500 MB  │
└─────────────────────────────────────────────┘
```

### 4. Complete
```
┌─────────────────────────────────────────────┐
│  📥 large-video.mp4                         │
│  ✅ Complete                                │
│  ████████████████████████████  100%        │
│  100%          --          500 MB / 500 MB │
└─────────────────────────────────────────────┘
```
*Disappears after 3 seconds*

### 5. Interrupted (Network Error)
```
┌─────────────────────────────────────────────┐
│  📥 large-video.mp4                         │
│  ⚠ Interrupted                              │
│  ██████████████████████░░░░░  78.3%        │
│  78.3%         --          392 MB / 500 MB │
│  ▶ Resume                            ✕     │
└─────────────────────────────────────────────┘
```

## Multiple Downloads

You can download multiple files simultaneously. Each gets its own progress item:

```
┌─────────────────────────────────────────────┐
│  📥 document.pdf              ⏸ ✕          │
│  🔄 Downloading...                          │
│  ████████████████░░░░░░░░░░░  45.2%        │
│  45.2%         2.5 MB/s    45 MB / 100 MB  │
├─────────────────────────────────────────────┤
│  📥 presentation.pptx         ⏸ ✕          │
│  🔄 Downloading...                          │
│  ████████░░░░░░░░░░░░░░░░░░░  23.7%        │
│  23.7%         1.8 MB/s    12 MB / 50 MB   │
├─────────────────────────────────────────────┤
│  📥 image.jpg                               │
│  ✅ Complete                                │
│  ████████████████████████████  100%        │
│  100%          --           5 MB / 5 MB    │
└─────────────────────────────────────────────┘
```

## Color Coding

- **Purple/Blue gradient**: Active progress bar
- **Green**: Completed download
- **Blue**: Resume badge/button
- **Orange**: Interrupted/Warning status
- **Red**: Cancel button (on hover)
- **Gray**: Paused/Inactive elements

## Animations

1. **Shimmer effect**: Animated light sweep across progress bar while downloading
2. **Smooth transitions**: Progress bar width changes smoothly (0.3s ease)
3. **Fade out**: Completed items fade out before removal
4. **Slide in**: Panel slides in when first download starts

## Responsive Behavior

- Fixed position in bottom-right corner
- Max height: 400px (scrollable if many downloads)
- Width: 300px
- Auto-hides when no active downloads
- Z-index: 1000 (appears above all content)

## Accessibility

- All buttons have tooltips
- Icons with descriptive aria-labels
- Keyboard accessible (tab navigation)
- Screen reader friendly status updates
