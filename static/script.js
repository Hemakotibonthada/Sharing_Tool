// Global state
let allFiles = [];
let selectedFiles = new Set();
let currentFilter = 'all';
let currentView = 'grid';
let currentSort = 'date-desc';
let activeUploads = [];
let uploadQueue = [];
const MAX_PARALLEL_UPLOADS = 5; // Upload 5 files simultaneously
let transferStats = {
    uploadSpeed: 0,
    downloadSpeed: 0
};
let downloadProgress = {};  // Track download progress
let resumableUploads = {};  // Track resumable uploads
let enableCompression = false;  // Compression before upload
let enableVersioning = false;  // File versioning

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initParticles();
    initSidebar();
    initNavigation();
    loadFiles();
    setupEventListeners();
    updateStats();
    updateTransferStatus();
    setInterval(updateStats, 5000); // Update stats every 5 seconds
    setInterval(updateTransferStatus, 2000); // Update transfer status every 2 seconds
});

// Create animated background particles
function initParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 15 + 's';
        particle.style.animationDuration = (15 + Math.random() * 10) + 's';
        particlesContainer.appendChild(particle);
    }
}

// Initialize sidebar
function initSidebar() {
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    
    menuBtn.addEventListener('click', () => {
        sidebar.classList.toggle('active');
    });
    
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.remove('active');
    });
}

// Initialize navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const section = item.dataset.section;
            navigateToSection(section);
        });
    });
}

// Navigate to section
function navigateToSection(section) {
    // Update nav items
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.section === section) {
            item.classList.add('active');
        }
    });
    
    // Update content sections
    document.querySelectorAll('.content-section').forEach(sec => {
        sec.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${section}-section`);
    if (targetSection) {
        targetSection.classList.add('active');
    }
    
    // Close sidebar on mobile
    document.getElementById('sidebar').classList.remove('active');
    
    // Load data if needed
    if (section === 'files') {
        loadFiles();
    } else if (section === 'dashboard') {
        loadRecentFiles();
        updateStats();
    }
}

// Setup event listeners
function setupEventListeners() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const searchInput = document.getElementById('searchInput');
    const refreshBtn = document.getElementById('refreshBtn');
    const themeToggle = document.getElementById('themeToggle');
    const sortBy = document.getElementById('sortBy');

    // Click to browse
    dropArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFiles);

    // Drag and drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.add('drag-over');
        });
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, () => {
            dropArea.classList.remove('drag-over');
        });
    });

    dropArea.addEventListener('drop', handleDrop);
    
    // Search
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            searchFiles(e.target.value);
        }, 300);
    });
    
    // Refresh
    refreshBtn.addEventListener('click', () => {
        refreshBtn.querySelector('i').style.animation = 'spin 0.5s linear';
        setTimeout(() => {
            refreshBtn.querySelector('i').style.animation = '';
        }, 500);
        loadFiles();
        updateStats();
    });
    
    // Theme toggle (placeholder)
    themeToggle.addEventListener('click', () => {
        showToast('Theme toggle coming soon!', 'info');
    });
    
    // Sort
    sortBy.addEventListener('change', (e) => {
        currentSort = e.target.value;
        renderFiles();
    });
    
    // File filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderFiles();
        });
    });
    
    // View toggle
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentView = btn.dataset.view;
            const filesGrid = document.getElementById('filesGrid');
            if (currentView === 'list') {
                filesGrid.classList.add('list-view');
            } else {
                filesGrid.classList.remove('list-view');
            }
        });
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles({ target: { files } });
}

// Handle file upload with parallel processing
function handleFiles(e) {
    const files = e.target.files;
    
    if (files.length === 0) return;

    document.getElementById('uploadQueue').style.display = 'block';
    
    // Add all files to queue
    Array.from(files).forEach((file, index) => {
        const uploadId = Date.now() + index;
        uploadQueue.push({ file, uploadId });
    });
    
    // Process queue with parallel uploads
    processUploadQueue();
    
    // Reset file input
    document.getElementById('fileInput').value = '';
}

function processUploadQueue() {
    // Start parallel uploads up to MAX_PARALLEL_UPLOADS
    while (uploadQueue.length > 0 && activeUploads.length < MAX_PARALLEL_UPLOADS) {
        const { file, uploadId } = uploadQueue.shift();
        uploadFile(file, uploadId);
    }
}

function uploadFile(file, uploadId, resumeOffset = 0) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('compress', enableCompression);
    formData.append('version', enableVersioning);

    const uploadItem = createUploadItem(file, uploadId);
    document.getElementById('uploadItems').appendChild(uploadItem);
    
    activeUploads.push(uploadId);

    const xhr = new XMLHttpRequest();
    const startTime = Date.now();
    let lastLoaded = resumeOffset;
    let lastTime = startTime;

    // Set resume header if resuming
    if (resumeOffset > 0) {
        xhr.setRequestHeader('X-Upload-Offset', resumeOffset);
    }

    // Upload progress with speed calculation
    xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
            const percentComplete = ((e.loaded + resumeOffset) / (e.total + resumeOffset)) * 100;
            const currentTime = Date.now();
            const timeDiff = (currentTime - lastTime) / 1000; // seconds
            const bytesDiff = e.loaded - lastLoaded;
            
            if (timeDiff > 0) {
                const speed = bytesDiff / timeDiff;
                updateUploadProgress(uploadId, percentComplete, speed);
                lastLoaded = e.loaded;
                lastTime = currentTime;
            } else {
                updateUploadProgress(uploadId, percentComplete, 0);
            }
            
            // Save progress for resume capability
            resumableUploads[file.name] = {
                uploadId: uploadId,
                file: file,
                bytesUploaded: e.loaded + resumeOffset,
                totalBytes: e.total + resumeOffset
            };
        }
    });

    // Upload complete
    xhr.addEventListener('load', () => {
        // Remove from active uploads
        activeUploads = activeUploads.filter(id => id !== uploadId);
        
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            const speed = response.speed || 'N/A';
            const resumedMsg = response.resumed_from ? ' (resumed)' : '';
            showToast(`${file.name} uploaded at ${speed}${resumedMsg}`, 'success');
            completeUpload(uploadId);
            
            // Clear resume data
            delete resumableUploads[file.name];
            
            setTimeout(() => {
                uploadItem.remove();
                loadFiles();
                updateStats();
                
                // Process next file in queue
                processUploadQueue();
            }, 1000);
        } else {
            const error = JSON.parse(xhr.responseText);
            showToast(error.error || 'Upload failed', 'error');
            failUpload(uploadId);
            activeUploads = activeUploads.filter(id => id !== uploadId);
            processUploadQueue();
        }
    });

    // Upload error - enable resume
    xhr.addEventListener('error', () => {
        showToast(`Upload interrupted: ${file.name} - Click Resume to continue`, 'warning');
        failUpload(uploadId, true);  // true = resumable
        activeUploads = activeUploads.filter(id => id !== uploadId);
        
        // Add resume button
        const uploadItem = document.getElementById(`upload-${uploadId}`);
        if (uploadItem && resumableUploads[file.name]) {
            const resumeBtn = document.createElement('button');
            resumeBtn.className = 'btn btn-small btn-primary';
            resumeBtn.innerHTML = '<i class="fas fa-play"></i> Resume';
            resumeBtn.onclick = () => {
                const savedProgress = resumableUploads[file.name];
                uploadFile(savedProgress.file, savedProgress.uploadId, savedProgress.bytesUploaded);
                resumeBtn.remove();
            };
            uploadItem.querySelector('.upload-item-header').appendChild(resumeBtn);
        }
    });

    xhr.open('POST', '/upload');
    xhr.send(formData);
}

function createUploadItem(file, uploadId) {
    const item = document.createElement('div');
    item.className = 'upload-item';
    item.id = `upload-${uploadId}`;
    
    item.innerHTML = `
        <div class="upload-item-header">
            <span>${escapeHtml(file.name)}</span>
            <div class="upload-stats">
                <span id="upload-speed-${uploadId}" class="upload-speed">0 KB/s</span>
                <span id="upload-percent-${uploadId}">0%</span>
            </div>
        </div>
        <div class="upload-progress-bar">
            <div class="upload-progress-fill" id="upload-progress-${uploadId}" style="width: 0%"></div>
        </div>
    `;
    
    return item;
}

function updateUploadProgress(uploadId, percent, speed) {
    const progressFill = document.getElementById(`upload-progress-${uploadId}`);
    const percentText = document.getElementById(`upload-percent-${uploadId}`);
    const speedText = document.getElementById(`upload-speed-${uploadId}`);
    
    if (progressFill && percentText) {
        progressFill.style.width = percent + '%';
        percentText.textContent = Math.round(percent) + '%';
    }
    
    if (speedText && speed > 0) {
        speedText.textContent = formatSpeed(speed);
    }
}

function completeUpload(uploadId) {
    const item = document.getElementById(`upload-${uploadId}`);
    if (item) {
        item.style.background = 'rgba(16, 185, 129, 0.1)';
        item.style.borderLeft = '3px solid var(--success)';
        const speedText = document.getElementById(`upload-speed-${uploadId}`);
        if (speedText) speedText.textContent = '✓ Complete';
    }
}

function failUpload(uploadId, resumable = false) {
    const item = document.getElementById(`upload-${uploadId}`);
    if (item) {
        item.style.background = resumable ? 'rgba(251, 191, 36, 0.1)' : 'rgba(239, 68, 68, 0.1)';
        item.style.borderLeft = resumable ? '3px solid #f59e0b' : '3px solid var(--danger)';
        const speedText = document.getElementById(`upload-speed-${uploadId}`);
        if (speedText) speedText.textContent = resumable ? '⏸ Paused' : '✗ Failed';
    }
}

// Load files from server
async function loadFiles() {
    try {
        const response = await fetch('/files');
        allFiles = await response.json();
        renderFiles();
        loadRecentFiles();
    } catch (error) {
        console.error('Error loading files:', error);
        showToast('Failed to load files', 'error');
    }
}

// Render files
function renderFiles() {
    let files = [...allFiles];
    
    // Apply filter
    if (currentFilter !== 'all') {
        files = files.filter(file => matchesFilter(file, currentFilter));
    }
    
    // Apply sort
    files = sortFiles(files, currentSort);
    
    const filesGrid = document.getElementById('filesGrid');
    const emptyState = document.getElementById('emptyState');

    if (files.length === 0) {
        filesGrid.style.display = 'none';
        emptyState.style.display = 'block';
    } else {
        filesGrid.style.display = 'grid';
        emptyState.style.display = 'none';
        
        filesGrid.innerHTML = files.map(file => createFileCard(file)).join('');
    }
    
    updateBulkActionsUI();
}

function matchesFilter(file, filter) {
    const type = file.type || '';
    const name = file.name.toLowerCase();
    
    switch(filter) {
        case 'images':
            return type.startsWith('image/');
        case 'videos':
            return type.startsWith('video/');
        case 'documents':
            return type.includes('pdf') || type.includes('document') || 
                   type.includes('word') || type.includes('text') ||
                   name.endsWith('.doc') || name.endsWith('.docx') || 
                   name.endsWith('.txt') || name.endsWith('.pdf');
        case 'archives':
            return type.includes('zip') || type.includes('archive') ||
                   name.endsWith('.zip') || name.endsWith('.rar') || 
                   name.endsWith('.7z');
        case 'others':
            return !matchesFilter(file, 'images') && 
                   !matchesFilter(file, 'videos') && 
                   !matchesFilter(file, 'documents') && 
                   !matchesFilter(file, 'archives');
        default:
            return true;
    }
}

function sortFiles(files, sortType) {
    switch(sortType) {
        case 'date-desc':
            return files.sort((a, b) => new Date(b.modified) - new Date(a.modified));
        case 'date-asc':
            return files.sort((a, b) => new Date(a.modified) - new Date(b.modified));
        case 'name-asc':
            return files.sort((a, b) => a.name.localeCompare(b.name));
        case 'name-desc':
            return files.sort((a, b) => b.name.localeCompare(a.name));
        case 'size-desc':
            return files.sort((a, b) => b.size - a.size);
        case 'size-asc':
            return files.sort((a, b) => a.size - b.size);
        default:
            return files;
    }
}

// Create file card HTML
function createFileCard(file) {
    const icon = getFileIcon(file.type, file.name);
    const size = formatFileSize(file.size);
    const isImage = file.type && file.type.startsWith('image/');
    const isVideo = file.type && file.type.startsWith('video/');
    const isAudio = file.type && file.type.startsWith('audio/');
    const isPDF = file.type && file.type.includes('pdf');
    const isText = file.type && (file.type.startsWith('text/') || file.type.includes('json') || file.type.includes('javascript'));
    const canPreview = isImage || isVideo || isAudio || isPDF || isText;
    
    return `
        <div class="file-card ${selectedFiles.has(file.name) ? 'selected' : ''}" data-filename="${escapeHtml(file.name)}">
            <input type="checkbox" class="file-checkbox" onchange="toggleFileSelection('${escapeHtml(file.name)}')" ${selectedFiles.has(file.name) ? 'checked' : ''}>
            <div class="file-icon">
                <i class="${icon}"></i>
            </div>
            <div class="file-name">${escapeHtml(file.name)}</div>
            <div class="file-meta">
                <div><i class="fas fa-hdd"></i> ${size}</div>
                <div><i class="fas fa-clock"></i> ${file.modified}</div>
            </div>
            <div class="file-actions">
                <button class="btn-download" onclick="downloadFileWithProgress('${escapeHtml(file.name)}')">
                    <i class="fas fa-download"></i>
                    Download
                </button>
                ${canPreview ? `
                <button class="btn-preview" onclick="previewFile('${escapeHtml(file.name)}')">
                    <i class="fas fa-eye"></i>
                    Preview
                </button>
                ` : ''}
                <button class="btn-secondary" onclick="showFileVersions('${escapeHtml(file.name)}')">
                    <i class="fas fa-history"></i>
                    Versions
                </button>
                <button class="btn-delete" onclick="deleteFile('${escapeHtml(file.name)}')">
                    <i class="fas fa-trash"></i>
                    Delete
                </button>
            </div>
        </div>
    `;
}

// Get file icon based on type
function getFileIcon(type, name) {
    if (!type) {
        const ext = name.split('.').pop().toLowerCase();
        const extIcons = {
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'docx': 'fas fa-file-word',
            'xls': 'fas fa-file-excel',
            'xlsx': 'fas fa-file-excel',
            'ppt': 'fas fa-file-powerpoint',
            'pptx': 'fas fa-file-powerpoint',
            'zip': 'fas fa-file-archive',
            'rar': 'fas fa-file-archive',
            '7z': 'fas fa-file-archive',
            'txt': 'fas fa-file-alt',
            'csv': 'fas fa-file-csv'
        };
        return extIcons[ext] || 'fas fa-file';
    }

    if (type.startsWith('image/')) return 'fas fa-file-image';
    if (type.startsWith('video/')) return 'fas fa-file-video';
    if (type.startsWith('audio/')) return 'fas fa-file-audio';
    if (type.includes('pdf')) return 'fas fa-file-pdf';
    if (type.includes('word')) return 'fas fa-file-word';
    if (type.includes('excel') || type.includes('spreadsheet')) return 'fas fa-file-excel';
    if (type.includes('powerpoint') || type.includes('presentation')) return 'fas fa-file-powerpoint';
    if (type.includes('zip') || type.includes('compressed')) return 'fas fa-file-archive';
    if (type.includes('text')) return 'fas fa-file-alt';
    
    return 'fas fa-file';
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format transfer speed
function formatSpeed(bytesPerSecond) {
    if (bytesPerSecond < 1024) {
        return `${bytesPerSecond.toFixed(0)} B/s`;
    } else if (bytesPerSecond < 1024 * 1024) {
        return `${(bytesPerSecond / 1024).toFixed(2)} KB/s`;
    } else if (bytesPerSecond < 1024 * 1024 * 1024) {
        return `${(bytesPerSecond / (1024 * 1024)).toFixed(2)} MB/s`;
    } else {
        return `${(bytesPerSecond / (1024 * 1024 * 1024)).toFixed(2)} GB/s`;
    }
}

// Load recent files for dashboard
async function loadRecentFiles() {
    const recentFilesContainer = document.getElementById('recentFiles');
    
    if (!allFiles || allFiles.length === 0) {
        await loadFiles();
    }
    
    const recentFiles = allFiles.slice(0, 5);
    
    if (recentFiles.length === 0) {
        recentFilesContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No files yet</p>';
        return;
    }
    
    recentFilesContainer.innerHTML = recentFiles.map(file => `
        <div class="recent-file-item">
            <div class="recent-file-icon">
                <i class="${getFileIcon(file.type, file.name)}"></i>
            </div>
            <div class="recent-file-info">
                <div class="recent-file-name">${escapeHtml(file.name)}</div>
                <div class="recent-file-meta">${formatFileSize(file.size)} • ${file.modified}</div>
            </div>
        </div>
    `).join('');
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/stats');
        const stats = await response.json();
        
        document.getElementById('statTotalFiles').textContent = stats.total_files;
        document.getElementById('statTotalSize').textContent = formatFileSize(stats.total_size);
        document.getElementById('statUploads').textContent = stats.total_uploads;
        document.getElementById('statDownloads').textContent = stats.total_downloads;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Update transfer status
async function updateTransferStatus() {
    try {
        const response = await fetch('/transfer-status');
        const status = await response.json();
        
        // You can display this in the UI if needed
        transferStats = status;
    } catch (error) {
        console.error('Error updating transfer status:', error);
    }
}

// Search files
async function searchFiles(query) {
    if (!query.trim()) {
        renderFiles();
        return;
    }
    
    try {
        const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
        allFiles = await response.json();
        renderFiles();
    } catch (error) {
        console.error('Error searching files:', error);
        showToast('Search failed', 'error');
    }
}

// File selection
function toggleFileSelection(filename) {
    if (selectedFiles.has(filename)) {
        selectedFiles.delete(filename);
    } else {
        selectedFiles.add(filename);
    }
    
    const card = document.querySelector(`[data-filename="${filename}"]`);
    if (card) {
        card.classList.toggle('selected');
    }
    
    updateBulkActionsUI();
}

function updateBulkActionsUI() {
    const count = selectedFiles.size;
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    const downloadBtn = document.getElementById('downloadSelectedBtn');
    const selectionInfo = document.getElementById('selectionInfo');
    
    if (deleteBtn) {
        deleteBtn.disabled = count === 0;
    }
    
    if (downloadBtn) {
        downloadBtn.disabled = count === 0;
    }
    
    if (selectionInfo) {
        selectionInfo.textContent = count === 0 ? 'No files selected' : 
                                   count === 1 ? '1 file selected' : 
                                   `${count} files selected`;
    }
}

function selectAllFiles() {
    const checkboxes = document.querySelectorAll('.file-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
        const filename = cb.closest('.file-card').dataset.filename;
        if (!allChecked) {
            selectedFiles.add(filename);
        } else {
            selectedFiles.delete(filename);
        }
    });
    
    renderFiles();
    showToast(allChecked ? 'All files deselected' : 'All files selected', 'success');
}

// Delete selected files
async function deleteSelected() {
    if (selectedFiles.size === 0) {
        showToast('No files selected', 'warning');
        return;
    }
    
    if (!confirm(`Delete ${selectedFiles.size} selected files?`)) {
        return;
    }
    
    try {
        const response = await fetch('/delete-multiple', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filenames: Array.from(selectedFiles)
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showToast(result.message, 'success');
            selectedFiles.clear();
            loadFiles();
            updateStats();
        } else {
            showToast(result.error || 'Delete failed', 'error');
        }
    } catch (error) {
        console.error('Error deleting files:', error);
        showToast('Delete failed', 'error');
    }
}

// Download file
function downloadFile(filename) {
    window.location.href = `/download/${encodeURIComponent(filename)}`;
    showToast(`Downloading ${filename}`, 'success');
}

// Download file with progress tracking
async function downloadFileWithProgress(filename) {
    try {
        const downloadId = Date.now();
        
        // Create progress indicator
        showDownloadProgress(filename, downloadId);
        
        const response = await fetch(`/download-progress/${encodeURIComponent(filename)}`, {
            headers: {
                'Range': downloadProgress[filename] ? `bytes=${downloadProgress[filename]}-` : undefined
            }
        });
        
        if (!response.ok) {
            throw new Error('Download failed');
        }
        
        const reader = response.body.getReader();
        const contentLength = +response.headers.get('Content-Length');
        let receivedLength = downloadProgress[filename] || 0;
        const chunks = [];
        
        while (true) {
            const {done, value} = await reader.read();
            
            if (done) break;
            
            chunks.push(value);
            receivedLength += value.length;
            
            // Update progress
            const percentComplete = (receivedLength / contentLength) * 100;
            updateDownloadProgress(downloadId, percentComplete, receivedLength, contentLength);
            
            // Save progress for resume
            downloadProgress[filename] = receivedLength;
        }
        
        // Combine chunks
        const blob = new Blob(chunks);
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Clear progress
        delete downloadProgress[filename];
        hideDownloadProgress(downloadId);
        showToast(`Downloaded ${filename}`, 'success');
        
    } catch (error) {
        console.error('Download error:', error);
        showToast(`Download interrupted: ${filename} - Click to resume`, 'warning');
    }
}

function showDownloadProgress(filename, downloadId) {
    const container = document.getElementById('downloadProgressContainer') || createDownloadProgressContainer();
    
    const item = document.createElement('div');
    item.className = 'download-progress-item';
    item.id = `download-${downloadId}`;
    item.innerHTML = `
        <div class="download-header">
            <i class="fas fa-download"></i>
            <span>${escapeHtml(filename)}</span>
            <span id="download-percent-${downloadId}">0%</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" id="download-progress-${downloadId}" style="width: 0%"></div>
        </div>
    `;
    
    container.appendChild(item);
}

function updateDownloadProgress(downloadId, percent, received, total) {
    const progressFill = document.getElementById(`download-progress-${downloadId}`);
    const percentText = document.getElementById(`download-percent-${downloadId}`);
    
    if (progressFill && percentText) {
        progressFill.style.width = percent + '%';
        percentText.textContent = Math.round(percent) + '%';
    }
}

function hideDownloadProgress(downloadId) {
    const item = document.getElementById(`download-${downloadId}`);
    if (item) {
        setTimeout(() => item.remove(), 2000);
    }
}

function createDownloadProgressContainer() {
    const container = document.createElement('div');
    container.id = 'downloadProgressContainer';
    container.className = 'download-progress-container glass-effect';
    container.style.cssText = 'position: fixed; bottom: 20px; right: 20px; width: 300px; max-height: 400px; overflow-y: auto; z-index: 1000; padding: 1rem; display: none;';
    document.body.appendChild(container);
    return container;
}

// Folder upload support
async function uploadFolder() {
    const input = document.createElement('input');
    input.type = 'file';
    input.webkitdirectory = true;
    input.directory = true;
    input.multiple = true;
    
    input.onchange = async (e) => {
        const files = Array.from(e.target.files);
        
        if (files.length === 0) return;
        
        showToast(`Uploading folder with ${files.length} files...`, 'info');
        
        const formData = new FormData();
        const paths = [];
        
        files.forEach(file => {
            formData.append('files', file);
            paths.push(file.webkitRelativePath || file.name);
        });
        
        paths.forEach(path => {
            formData.append('paths', path);
        });
        
        try {
            const response = await fetch('/upload-folder', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                showToast(`Uploaded ${result.uploaded} files successfully`, 'success');
                if (result.failed > 0) {
                    showToast(`${result.failed} files failed`, 'warning');
                }
                loadFiles();
                updateStats();
            } else {
                showToast('Folder upload failed', 'error');
            }
        } catch (error) {
            console.error('Folder upload error:', error);
            showToast('Folder upload failed', 'error');
        }
    };
    
    input.click();
}

// File preview support
async function previewFile(filename) {
    const modal = document.getElementById('previewModal') || createPreviewModal();
    const previewContent = document.getElementById('previewContent');
    
    // Determine file type
    const ext = filename.split('.').pop().toLowerCase();
    const previewTypes = {
        image: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'],
        video: ['mp4', 'webm', 'ogg'],
        audio: ['mp3', 'wav', 'ogg', 'flac', 'aac'],
        pdf: ['pdf'],
        text: ['txt', 'md', 'json', 'js', 'py', 'html', 'css', 'xml']
    };
    
    let previewHTML = '';
    
    if (previewTypes.image.includes(ext)) {
        previewHTML = `<img src="/preview/${encodeURIComponent(filename)}" style="max-width: 100%; max-height: 80vh;" alt="${escapeHtml(filename)}">`;
    } else if (previewTypes.video.includes(ext)) {
        previewHTML = `<video controls style="max-width: 100%; max-height: 80vh;">
            <source src="/preview/${encodeURIComponent(filename)}" type="video/${ext}">
            Your browser does not support video playback.
        </video>`;
    } else if (previewTypes.audio.includes(ext)) {
        previewHTML = `<audio controls style="width: 100%;">
            <source src="/preview/${encodeURIComponent(filename)}" type="audio/${ext}">
            Your browser does not support audio playback.
        </audio>`;
    } else if (previewTypes.pdf.includes(ext)) {
        previewHTML = `<iframe src="/preview/${encodeURIComponent(filename)}" style="width: 100%; height: 80vh; border: none;"></iframe>`;
    } else if (previewTypes.text.includes(ext)) {
        try {
            const response = await fetch(`/preview/${encodeURIComponent(filename)}`);
            const text = await response.text();
            previewHTML = `<pre style="max-height: 80vh; overflow: auto; padding: 1rem; background: #1a1a1a; color: #fff; border-radius: 8px;">${escapeHtml(text)}</pre>`;
        } catch (error) {
            previewHTML = '<p>Failed to load preview</p>';
        }
    } else {
        previewHTML = '<p>Preview not available for this file type</p>';
    }
    
    previewContent.innerHTML = previewHTML;
    modal.style.display = 'flex';
}

function createPreviewModal() {
    const modal = document.createElement('div');
    modal.id = 'previewModal';
    modal.className = 'modal';
    modal.style.cssText = 'display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 2000; align-items: center; justify-content: center;';
    
    modal.innerHTML = `
        <div style="position: relative; max-width: 90%; max-height: 90%; padding: 2rem;">
            <button onclick="document.getElementById('previewModal').style.display='none'" style="position: absolute; top: 10px; right: 10px; background: #fff; border: none; padding: 10px 15px; border-radius: 50%; cursor: pointer; font-size: 1.2rem;">×</button>
            <div id="previewContent"></div>
        </div>
    `;
    
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    };
    
    document.body.appendChild(modal);
    return modal;
}

// File versioning
async function showFileVersions(filename) {
    try {
        const response = await fetch(`/file-versions/${encodeURIComponent(filename)}`);
        const data = await response.json();
        
        if (data.versions.length === 0) {
            showToast('No previous versions available', 'info');
            return;
        }
        
        // Show versions modal
        const modal = createVersionsModal(filename, data.versions);
        modal.style.display = 'flex';
        
    } catch (error) {
        console.error('Error fetching versions:', error);
        showToast('Failed to load versions', 'error');
    }
}

function createVersionsModal(filename, versions) {
    const modal = document.getElementById('versionsModal') || document.createElement('div');
    modal.id = 'versionsModal';
    modal.className = 'modal';
    modal.style.cssText = 'display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 2000; align-items: center; justify-content: center;';
    
    const versionsList = versions.map(v => `
        <div class="version-item glass-effect" style="padding: 1rem; margin: 0.5rem 0; display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>Version ${v.version}</strong>
                <p style="margin: 0.25rem 0; font-size: 0.9rem; opacity: 0.8;">${new Date(v.timestamp).toLocaleString()}</p>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.7;">${formatFileSize(v.size)}</p>
            </div>
            <button class="btn btn-primary" onclick="restoreVersion('${escapeHtml(filename)}', ${v.version})">
                <i class="fas fa-undo"></i> Restore
            </button>
        </div>
    `).join('');
    
    modal.innerHTML = `
        <div class="glass-effect" style="max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; padding: 2rem; border-radius: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h2 style="margin: 0;">File Versions: ${escapeHtml(filename)}</h2>
                <button onclick="document.getElementById('versionsModal').style.display='none'" style="background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #fff;">×</button>
            </div>
            ${versionsList}
        </div>
    `;
    
    if (!document.getElementById('versionsModal')) {
        document.body.appendChild(modal);
    }
    
    return modal;
}

async function restoreVersion(filename, version) {
    if (!confirm(`Restore ${filename} to version ${version}? Current file will be backed up.`)) {
        return;
    }
    
    try {
        const response = await fetch('/restore-version', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename, version})
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            document.getElementById('versionsModal').style.display = 'none';
            loadFiles();
        } else {
            showToast(result.error || 'Restore failed', 'error');
        }
    } catch (error) {
        console.error('Restore error:', error);
        showToast('Restore failed', 'error');
    }
}

// Toggle compression
function toggleCompression() {
    enableCompression = !enableCompression;
    const btn = document.getElementById('compressionToggle');
    if (btn) {
        btn.classList.toggle('active');
        btn.innerHTML = enableCompression ? 
            '<i class="fas fa-compress"></i> Compression: ON' : 
            '<i class="fas fa-compress"></i> Compression: OFF';
    }
    showToast(`Compression ${enableCompression ? 'enabled' : 'disabled'}`, 'info');
}

// Toggle versioning
function toggleVersioning() {
    enableVersioning = !enableVersioning;
    const btn = document.getElementById('versioningToggle');
    if (btn) {
        btn.classList.toggle('active');
        btn.innerHTML = enableVersioning ? 
            '<i class="fas fa-history"></i> Versioning: ON' : 
            '<i class="fas fa-history"></i> Versioning: OFF';
    }
    showToast(`File versioning ${enableVersioning ? 'enabled' : 'disabled'}`, 'info');
}

// Copy URL to clipboard
function copyUrl() {
    const urlInput = document.getElementById('serverUrl');
    urlInput.select();
    urlInput.setSelectionRange(0, 99999);

    try {
        document.execCommand('copy');
        showToast('URL copied to clipboard!', 'success');
    } catch (err) {
        navigator.clipboard.writeText(urlInput.value).then(() => {
            showToast('URL copied to clipboard!', 'success');
        }).catch(() => {
            showToast('Failed to copy URL', 'error');
        });
    }
}

// Show toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    
    const icon = toast.querySelector('i');
    const colors = {
        'success': { icon: 'fas fa-check-circle', bg: '#10b981' },
        'error': { icon: 'fas fa-exclamation-circle', bg: '#ef4444' },
        'warning': { icon: 'fas fa-exclamation-triangle', bg: '#f59e0b' },
        'info': { icon: 'fas fa-info-circle', bg: '#3b82f6' }
    };
    
    const style = colors[type] || colors.success;
    icon.className = style.icon;
    toast.style.background = style.bg;
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    const deleteModal = document.getElementById('deleteModal');
    const previewModal = document.getElementById('previewModal');
    
    if (e.target === deleteModal) {
        closeDeleteModal();
    }
    if (e.target === previewModal) {
        closePreviewModal();
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Escape to close modals
    if (e.key === 'Escape') {
        closeDeleteModal();
        closePreviewModal();
    }
    
    // Ctrl/Cmd + A to select all
    if ((e.ctrlKey || e.metaKey) && e.key === 'a' && document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        selectAllFiles();
    }
});

// Add spin animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
