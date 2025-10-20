/**
 * Enhanced File Manager with Drag & Drop, Grid/List View, and Preview
 * NetShare Pro - Circuvent Technologies
 */

// File Manager State
const fileManager = {
    currentView: 'grid',
    currentFilter: 'all',
    currentSort: 'date-desc',
    selectedFiles: new Set(),
    files: [],
    previewModal: null,
    dropZone: null
};

// Initialize Enhanced File Manager
function initializeFileManager() {
    console.log('Initializing Enhanced File Manager...');
    
    // Setup drag and drop for upload area
    setupDragAndDrop();
    
    // Setup view toggle
    setupViewToggle();
    
    // Setup file filters
    setupFileFilters();
    
    // Setup sort controls
    setupSortControls();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Load files
    loadFiles();
    
    console.log('File Manager initialized successfully');
}

// ==================== DRAG AND DROP ====================

function setupDragAndDrop() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!dropArea) return;
    
    fileManager.dropZone = dropArea;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when dragging over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    
    // Handle file input change
    if (fileInput) {
        fileInput.addEventListener('change', handleFileInputChange, false);
    }
    
    // Make file grid a drop zone too
    const filesGrid = document.getElementById('filesGrid');
    if (filesGrid) {
        ['dragenter', 'dragover'].forEach(eventName => {
            filesGrid.addEventListener(eventName, (e) => {
                preventDefaults(e);
                filesGrid.classList.add('drag-over');
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            filesGrid.addEventListener(eventName, (e) => {
                filesGrid.classList.remove('drag-over');
            }, false);
        });
        
        filesGrid.addEventListener('drop', handleDrop, false);
    }
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    if (fileManager.dropZone) {
        fileManager.dropZone.classList.add('drag-active');
    }
}

function unhighlight(e) {
    if (fileManager.dropZone) {
        fileManager.dropZone.classList.remove('drag-active');
    }
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    handleFiles(files);
}

function handleFileInputChange(e) {
    const files = e.target.files;
    handleFiles(files);
}

function handleFiles(files) {
    if (!files || files.length === 0) return;
    
    console.log(`Processing ${files.length} file(s)...`);
    
    // Show upload queue
    const uploadQueue = document.getElementById('uploadQueue');
    if (uploadQueue) {
        uploadQueue.style.display = 'block';
    }
    
    // Process each file
    Array.from(files).forEach(file => {
        uploadFileWithProgress(file);
    });
    
    // Navigate to upload section
    navigateToSection('upload');
}

// ==================== VIEW TOGGLE ====================

function setupViewToggle() {
    const viewButtons = document.querySelectorAll('.view-btn');
    
    viewButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.getAttribute('data-view');
            switchView(view);
        });
    });
}

function switchView(view) {
    if (!['grid', 'list'].includes(view)) return;
    
    fileManager.currentView = view;
    
    // Update button states
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-view') === view) {
            btn.classList.add('active');
        }
    });
    
    // Update grid class
    const filesGrid = document.getElementById('filesGrid');
    if (filesGrid) {
        filesGrid.className = view === 'grid' ? 'files-grid' : 'files-list';
    }
    
    // Re-render files with new view
    renderFiles();
    
    // Save preference
    localStorage.setItem('fileManagerView', view);
    
    showToast(`Switched to ${view} view`, 'info');
}

// ==================== FILE FILTERS ====================

function setupFileFilters() {
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.getAttribute('data-filter');
            applyFilter(filter);
        });
    });
}

function applyFilter(filter) {
    fileManager.currentFilter = filter;
    
    // Update button states
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-filter') === filter) {
            btn.classList.add('active');
        }
    });
    
    // Re-render files with filter
    renderFiles();
}

function getFileCategory(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    
    const categories = {
        images: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp', 'ico'],
        videos: ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm', 'm4v'],
        documents: ['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'ppt', 'pptx'],
        archives: ['zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz'],
    };
    
    for (const [category, extensions] of Object.entries(categories)) {
        if (extensions.includes(ext)) {
            return category;
        }
    }
    
    return 'others';
}

function filterFiles() {
    if (fileManager.currentFilter === 'all') {
        return fileManager.files;
    }
    
    return fileManager.files.filter(file => {
        const category = getFileCategory(file.name);
        return category === fileManager.currentFilter;
    });
}

// ==================== SORT CONTROLS ====================

function setupSortControls() {
    const sortSelect = document.getElementById('sortBy');
    
    if (sortSelect) {
        sortSelect.addEventListener('change', (e) => {
            fileManager.currentSort = e.target.value;
            renderFiles();
        });
    }
}

function sortFiles(files) {
    const sorted = [...files];
    
    switch (fileManager.currentSort) {
        case 'date-desc':
            return sorted.sort((a, b) => new Date(b.uploaded_at || 0) - new Date(a.uploaded_at || 0));
        case 'date-asc':
            return sorted.sort((a, b) => new Date(a.uploaded_at || 0) - new Date(b.uploaded_at || 0));
        case 'name-asc':
            return sorted.sort((a, b) => a.name.localeCompare(b.name));
        case 'name-desc':
            return sorted.sort((a, b) => b.name.localeCompare(a.name));
        case 'size-desc':
            return sorted.sort((a, b) => (b.size || 0) - (a.size || 0));
        case 'size-asc':
            return sorted.sort((a, b) => (a.size || 0) - (b.size || 0));
        default:
            return sorted;
    }
}

// ==================== FILE RENDERING ====================

function renderFiles() {
    const filesGrid = document.getElementById('filesGrid');
    const emptyState = document.getElementById('emptyState');
    
    if (!filesGrid) return;
    
    // Filter and sort files
    let filtered = filterFiles();
    filtered = sortFiles(filtered);
    
    // Clear current files
    filesGrid.innerHTML = '';
    
    if (filtered.length === 0) {
        if (emptyState) emptyState.style.display = 'flex';
        return;
    }
    
    if (emptyState) emptyState.style.display = 'none';
    
    // Render based on current view
    if (fileManager.currentView === 'grid') {
        renderGridView(filtered, filesGrid);
    } else {
        renderListView(filtered, filesGrid);
    }
    
    // Update selection info
    updateSelectionInfo();
}

function renderGridView(files, container) {
    files.forEach(file => {
        const fileCard = createFileCard(file);
        container.appendChild(fileCard);
    });
}

function renderListView(files, container) {
    files.forEach(file => {
        const fileRow = createFileRow(file);
        container.appendChild(fileRow);
    });
}

function createFileCard(file) {
    const card = document.createElement('div');
    card.className = 'file-card glass-effect';
    card.setAttribute('data-filename', file.name);
    
    const isSelected = fileManager.selectedFiles.has(file.name);
    if (isSelected) {
        card.classList.add('selected');
    }
    
    const category = getFileCategory(file.name);
    const icon = getFileIcon(file.name);
    const sizeFormatted = formatFileSize(file.size || 0);
    const dateFormatted = formatDate(file.uploaded_at);
    
    // Create thumbnail or icon
    const previewHtml = canPreviewImage(file.name) 
        ? `<img src="/download/${encodeURIComponent(file.name)}" alt="${file.name}" class="file-thumbnail" onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
           <div class="file-icon" style="display:none;"><i class="${icon}"></i></div>`
        : `<div class="file-icon"><i class="${icon}"></i></div>`;
    
    card.innerHTML = `
        <div class="file-card-header">
            <input type="checkbox" class="file-checkbox" ${isSelected ? 'checked' : ''} 
                   onchange="toggleFileSelection('${file.name}', this.checked)">
            <span class="file-category-badge ${category}">${category}</span>
        </div>
        <div class="file-preview" onclick="previewFile('${file.name}')">
            ${previewHtml}
        </div>
        <div class="file-info">
            <div class="file-name" title="${file.name}">${truncateFilename(file.name, 25)}</div>
            <div class="file-meta">
                <span><i class="fas fa-hdd"></i> ${sizeFormatted}</span>
                <span><i class="fas fa-clock"></i> ${dateFormatted}</span>
            </div>
        </div>
        <div class="file-actions">
            <button class="btn-icon" onclick="downloadFile('${file.name}')" title="Download">
                <i class="fas fa-download"></i>
            </button>
            <button class="btn-icon" onclick="shareFile('${file.name}')" title="Share">
                <i class="fas fa-share-alt"></i>
            </button>
            <button class="btn-icon btn-danger" onclick="showDeleteModal('${file.name}')" title="Delete">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Add context menu
    card.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showContextMenu(e, file.name);
    });
    
    return card;
}

function createFileRow(file) {
    const row = document.createElement('div');
    row.className = 'file-row glass-effect';
    row.setAttribute('data-filename', file.name);
    
    const isSelected = fileManager.selectedFiles.has(file.name);
    if (isSelected) {
        row.classList.add('selected');
    }
    
    const category = getFileCategory(file.name);
    const icon = getFileIcon(file.name);
    const sizeFormatted = formatFileSize(file.size || 0);
    const dateFormatted = formatDate(file.uploaded_at);
    
    row.innerHTML = `
        <div class="file-row-checkbox">
            <input type="checkbox" class="file-checkbox" ${isSelected ? 'checked' : ''} 
                   onchange="toggleFileSelection('${file.name}', this.checked)">
        </div>
        <div class="file-row-icon">
            <i class="${icon}"></i>
        </div>
        <div class="file-row-name" onclick="previewFile('${file.name}')" style="cursor: pointer;">
            <div class="file-name">${file.name}</div>
            <div class="file-category-badge ${category}">${category}</div>
        </div>
        <div class="file-row-size">${sizeFormatted}</div>
        <div class="file-row-date">${dateFormatted}</div>
        <div class="file-row-actions">
            <button class="btn-icon" onclick="downloadFile('${file.name}')" title="Download">
                <i class="fas fa-download"></i>
            </button>
            <button class="btn-icon" onclick="shareFile('${file.name}')" title="Share">
                <i class="fas fa-share-alt"></i>
            </button>
            <button class="btn-icon btn-danger" onclick="showDeleteModal('${file.name}')" title="Delete">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Add context menu
    row.addEventListener('contextmenu', (e) => {
        e.preventDefault();
        showContextMenu(e, file.name);
    });
    
    return row;
}

// ==================== FILE PREVIEW ====================

function canPreviewImage(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp'].includes(ext);
}

function canPreviewVideo(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return ['mp4', 'webm', 'ogg'].includes(ext);
}

function canPreviewAudio(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return ['mp3', 'wav', 'ogg'].includes(ext);
}

function canPreviewText(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    return ['txt', 'md', 'json', 'xml', 'html', 'css', 'js', 'py', 'java', 'c', 'cpp', 'h'].includes(ext);
}

function previewFile(filename) {
    const modal = document.getElementById('previewModal');
    const previewContent = document.getElementById('previewContent');
    const previewFileName = document.getElementById('previewFileName');
    
    if (!modal || !previewContent || !previewFileName) {
        console.error('Preview modal elements not found');
        return;
    }
    
    previewFileName.textContent = filename;
    previewContent.innerHTML = '<div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading preview...</div>';
    
    modal.style.display = 'flex';
    fileManager.previewModal = filename;
    
    // Determine preview type and load content
    if (canPreviewImage(filename)) {
        previewImage(filename, previewContent);
    } else if (canPreviewVideo(filename)) {
        previewVideo(filename, previewContent);
    } else if (canPreviewAudio(filename)) {
        previewAudio(filename, previewContent);
    } else if (canPreviewText(filename)) {
        previewText(filename, previewContent);
    } else {
        previewContent.innerHTML = `
            <div class="preview-unsupported">
                <i class="fas fa-file" style="font-size: 4rem; color: var(--text-secondary); margin-bottom: 1rem;"></i>
                <h3>Preview not available</h3>
                <p>This file type cannot be previewed in the browser</p>
                <button class="btn btn-primary" onclick="downloadFile('${filename}')">
                    <i class="fas fa-download"></i> Download File
                </button>
            </div>
        `;
    }
}

function previewImage(filename, container) {
    container.innerHTML = `
        <div class="preview-image-container">
            <img src="/download/${encodeURIComponent(filename)}" alt="${filename}" class="preview-image" 
                 onload="this.parentElement.querySelector('.loading').style.display='none'"
                 onerror="this.parentElement.innerHTML='<div class=\\'preview-error\\'>Failed to load image</div>'">
            <div class="loading"><i class="fas fa-spinner fa-spin"></i> Loading...</div>
            <div class="preview-controls">
                <button class="btn-icon" onclick="zoomPreview('in')" title="Zoom In">
                    <i class="fas fa-search-plus"></i>
                </button>
                <button class="btn-icon" onclick="zoomPreview('out')" title="Zoom Out">
                    <i class="fas fa-search-minus"></i>
                </button>
                <button class="btn-icon" onclick="downloadFile('${filename}')" title="Download">
                    <i class="fas fa-download"></i>
                </button>
            </div>
        </div>
    `;
}

function previewVideo(filename, container) {
    container.innerHTML = `
        <div class="preview-video-container">
            <video controls class="preview-video">
                <source src="/download/${encodeURIComponent(filename)}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
            <div class="preview-controls">
                <button class="btn-icon" onclick="downloadFile('${filename}')" title="Download">
                    <i class="fas fa-download"></i>
                </button>
            </div>
        </div>
    `;
}

function previewAudio(filename, container) {
    container.innerHTML = `
        <div class="preview-audio-container">
            <i class="fas fa-music" style="font-size: 4rem; color: var(--color-primary); margin-bottom: 2rem;"></i>
            <audio controls class="preview-audio">
                <source src="/download/${encodeURIComponent(filename)}">
                Your browser does not support the audio tag.
            </audio>
            <div class="preview-controls">
                <button class="btn-icon" onclick="downloadFile('${filename}')" title="Download">
                    <i class="fas fa-download"></i>
                </button>
            </div>
        </div>
    `;
}

function previewText(filename, container) {
    fetch(`/download/${encodeURIComponent(filename)}`)
        .then(response => response.text())
        .then(text => {
            container.innerHTML = `
                <div class="preview-text-container">
                    <pre class="preview-text">${escapeHtml(text)}</pre>
                    <div class="preview-controls">
                        <button class="btn-icon" onclick="copyTextContent()" title="Copy">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="btn-icon" onclick="downloadFile('${filename}')" title="Download">
                            <i class="fas fa-download"></i>
                        </button>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            container.innerHTML = '<div class="preview-error">Failed to load file content</div>';
        });
}

function closePreviewModal() {
    const modal = document.getElementById('previewModal');
    if (modal) {
        modal.style.display = 'none';
        fileManager.previewModal = null;
    }
}

function zoomPreview(direction) {
    const img = document.querySelector('.preview-image');
    if (!img) return;
    
    const currentScale = parseFloat(img.style.transform?.match(/scale\(([\d.]+)\)/)?.[1] || '1');
    const newScale = direction === 'in' ? currentScale * 1.2 : currentScale / 1.2;
    
    img.style.transform = `scale(${Math.max(0.5, Math.min(3, newScale))})`;
}

function copyTextContent() {
    const textElement = document.querySelector('.preview-text');
    if (!textElement) return;
    
    navigator.clipboard.writeText(textElement.textContent)
        .then(() => showToast('Text copied to clipboard', 'success'))
        .catch(() => showToast('Failed to copy text', 'error'));
}

// ==================== FILE SELECTION ====================

function toggleFileSelection(filename, selected) {
    if (selected) {
        fileManager.selectedFiles.add(filename);
    } else {
        fileManager.selectedFiles.delete(filename);
    }
    
    // Update UI
    const element = document.querySelector(`[data-filename="${filename}"]`);
    if (element) {
        if (selected) {
            element.classList.add('selected');
        } else {
            element.classList.remove('selected');
        }
    }
    
    updateSelectionInfo();
}

function selectAllFiles() {
    const filtered = filterFiles();
    filtered.forEach(file => {
        fileManager.selectedFiles.add(file.name);
    });
    
    // Update all checkboxes
    document.querySelectorAll('.file-checkbox').forEach(cb => {
        cb.checked = true;
    });
    
    // Update all cards/rows
    document.querySelectorAll('.file-card, .file-row').forEach(el => {
        el.classList.add('selected');
    });
    
    updateSelectionInfo();
    showToast(`Selected ${fileManager.selectedFiles.size} files`, 'info');
}

function deselectAllFiles() {
    fileManager.selectedFiles.clear();
    
    // Update all checkboxes
    document.querySelectorAll('.file-checkbox').forEach(cb => {
        cb.checked = false;
    });
    
    // Update all cards/rows
    document.querySelectorAll('.file-card, .file-row').forEach(el => {
        el.classList.remove('selected');
    });
    
    updateSelectionInfo();
}

function updateSelectionInfo() {
    const count = fileManager.selectedFiles.size;
    const infoElement = document.getElementById('selectionInfo');
    const downloadBtn = document.getElementById('downloadSelectedBtn');
    const deleteBtn = document.getElementById('deleteSelectedBtn');
    
    if (infoElement) {
        infoElement.textContent = `${count} file${count !== 1 ? 's' : ''} selected`;
    }
    
    // Enable/disable bulk action buttons
    if (downloadBtn) {
        downloadBtn.disabled = count === 0;
    }
    if (deleteBtn) {
        deleteBtn.disabled = count === 0;
    }
}

// ==================== CONTEXT MENU ====================

function showContextMenu(event, filename) {
    // Remove existing context menu
    const existing = document.querySelector('.context-menu');
    if (existing) {
        existing.remove();
    }
    
    // Create context menu
    const menu = document.createElement('div');
    menu.className = 'context-menu glass-effect';
    menu.innerHTML = `
        <div class="context-menu-item" onclick="previewFile('${filename}'); closeContextMenu();">
            <i class="fas fa-eye"></i> Preview
        </div>
        <div class="context-menu-item" onclick="downloadFile('${filename}'); closeContextMenu();">
            <i class="fas fa-download"></i> Download
        </div>
        <div class="context-menu-item" onclick="shareFile('${filename}'); closeContextMenu();">
            <i class="fas fa-share-alt"></i> Share
        </div>
        <div class="context-menu-divider"></div>
        <div class="context-menu-item" onclick="renameFile('${filename}'); closeContextMenu();">
            <i class="fas fa-edit"></i> Rename
        </div>
        <div class="context-menu-item danger" onclick="showDeleteModal('${filename}'); closeContextMenu();">
            <i class="fas fa-trash"></i> Delete
        </div>
    `;
    
    // Position menu
    menu.style.left = event.pageX + 'px';
    menu.style.top = event.pageY + 'px';
    
    document.body.appendChild(menu);
    
    // Close menu when clicking outside
    setTimeout(() => {
        document.addEventListener('click', closeContextMenu);
    }, 10);
}

function closeContextMenu() {
    const menu = document.querySelector('.context-menu');
    if (menu) {
        menu.remove();
    }
    document.removeEventListener('click', closeContextMenu);
}

// ==================== FILE OPERATIONS ====================

function shareFile(filename) {
    const url = `${window.location.origin}/download/${encodeURIComponent(filename)}`;
    
    if (navigator.share) {
        navigator.share({
            title: filename,
            text: `Check out this file: ${filename}`,
            url: url
        })
        .then(() => showToast('Shared successfully', 'success'))
        .catch(() => copyToClipboard(url));
    } else {
        copyToClipboard(url);
    }
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => showToast('Link copied to clipboard', 'success'))
        .catch(() => showToast('Failed to copy link', 'error'));
}

function renameFile(filename) {
    const newName = prompt('Enter new filename:', filename);
    if (!newName || newName === filename) return;
    
    fetch('/rename', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ oldName: filename, newName: newName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('File renamed successfully', 'success');
            loadFiles();
        } else {
            showToast(data.message || 'Failed to rename file', 'error');
        }
    })
    .catch(error => {
        showToast('Failed to rename file', 'error');
    });
}

// ==================== KEYBOARD SHORTCUTS ====================

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + A: Select all files
        if ((e.ctrlKey || e.metaKey) && e.key === 'a' && document.activeElement.tagName !== 'INPUT') {
            e.preventDefault();
            selectAllFiles();
        }
        
        // Escape: Deselect all files or close modal
        if (e.key === 'Escape') {
            if (fileManager.previewModal) {
                closePreviewModal();
            } else {
                deselectAllFiles();
            }
        }
        
        // Delete: Delete selected files
        if (e.key === 'Delete' && fileManager.selectedFiles.size > 0) {
            deleteSelected();
        }
    });
}

// ==================== UTILITY FUNCTIONS ====================

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    
    const iconMap = {
        // Images
        jpg: 'fas fa-file-image', jpeg: 'fas fa-file-image', png: 'fas fa-file-image',
        gif: 'fas fa-file-image', bmp: 'fas fa-file-image', svg: 'fas fa-file-image',
        
        // Videos
        mp4: 'fas fa-file-video', avi: 'fas fa-file-video', mov: 'fas fa-file-video',
        wmv: 'fas fa-file-video', flv: 'fas fa-file-video', mkv: 'fas fa-file-video',
        
        // Documents
        pdf: 'fas fa-file-pdf', doc: 'fas fa-file-word', docx: 'fas fa-file-word',
        xls: 'fas fa-file-excel', xlsx: 'fas fa-file-excel',
        ppt: 'fas fa-file-powerpoint', pptx: 'fas fa-file-powerpoint',
        txt: 'fas fa-file-alt',
        
        // Archives
        zip: 'fas fa-file-archive', rar: 'fas fa-file-archive', '7z': 'fas fa-file-archive',
        tar: 'fas fa-file-archive', gz: 'fas fa-file-archive',
        
        // Code
        js: 'fas fa-file-code', html: 'fas fa-file-code', css: 'fas fa-file-code',
        py: 'fas fa-file-code', java: 'fas fa-file-code', cpp: 'fas fa-file-code',
        
        // Audio
        mp3: 'fas fa-file-audio', wav: 'fas fa-file-audio', ogg: 'fas fa-file-audio',
    };
    
    return iconMap[ext] || 'fas fa-file';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    // Less than a minute
    if (diff < 60000) {
        return 'Just now';
    }
    
    // Less than an hour
    if (diff < 3600000) {
        const minutes = Math.floor(diff / 60000);
        return `${minutes} min${minutes > 1 ? 's' : ''} ago`;
    }
    
    // Less than a day
    if (diff < 86400000) {
        const hours = Math.floor(diff / 3600000);
        return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    }
    
    // Less than a week
    if (diff < 604800000) {
        const days = Math.floor(diff / 86400000);
        return `${days} day${days > 1 ? 's' : ''} ago`;
    }
    
    // Default format
    return date.toLocaleDateString();
}

function truncateFilename(filename, maxLength) {
    if (filename.length <= maxLength) return filename;
    
    const ext = filename.split('.').pop();
    const name = filename.substring(0, filename.length - ext.length - 1);
    const truncated = name.substring(0, maxLength - ext.length - 4) + '...';
    
    return truncated + '.' + ext;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== LOAD FILES ====================

function loadFiles() {
    fetch('/files')
        .then(response => response.json())
        .then(data => {
            fileManager.files = data.files || [];
            renderFiles();
        })
        .catch(error => {
            console.error('Error loading files:', error);
            showToast('Failed to load files', 'error');
        });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeFileManager);
} else {
    initializeFileManager();
}

// Export for use in other scripts
window.fileManager = fileManager;
window.previewFile = previewFile;
window.closePreviewModal = closePreviewModal;
window.toggleFileSelection = toggleFileSelection;
window.selectAllFiles = selectAllFiles;
