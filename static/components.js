/**
 * Modern UI Components JavaScript
 * NetShare Pro - Circuvent Technologies
 */

// ==================== LOADING OVERLAY ====================

const LoadingOverlay = {
    show(message = 'Loading...', subtitle = '') {
        // Remove existing overlay if any
        this.hide();
        
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = `
            <div class="loading-content">
                <div class="spinner lg"></div>
                <h3>${message}</h3>
                ${subtitle ? `<p>${subtitle}</p>` : ''}
            </div>
        `;
        
        document.body.appendChild(overlay);
        document.body.style.overflow = 'hidden';
    },
    
    hide() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.remove();
            document.body.style.overflow = '';
        }
    },
    
    update(message, subtitle = '') {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            const content = overlay.querySelector('.loading-content');
            content.querySelector('h3').textContent = message;
            const p = content.querySelector('p');
            if (subtitle) {
                if (p) {
                    p.textContent = subtitle;
                } else {
                    const newP = document.createElement('p');
                    newP.textContent = subtitle;
                    content.appendChild(newP);
                }
            } else if (p) {
                p.remove();
            }
        }
    }
};

// ==================== PROGRESS BAR ====================

class ProgressBar {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            size: options.size || 'md', // sm, md, lg, xl
            variant: options.variant || 'default', // default, success, warning, danger, info
            showLabel: options.showLabel !== false,
            animated: options.animated !== false,
            ...options
        };
        
        this.create();
    }
    
    create() {
        if (!this.container) return;
        
        const bar = document.createElement('div');
        bar.className = `progress-bar ${this.options.size}`;
        
        const fill = document.createElement('div');
        fill.className = `progress-bar-fill ${this.options.variant}`;
        fill.style.width = '0%';
        
        if (this.options.showLabel) {
            const label = document.createElement('span');
            label.className = 'progress-label';
            label.textContent = '0%';
            label.style.cssText = 'position: absolute; right: 10px; top: -25px; font-size: 0.85rem; color: var(--text-secondary);';
            bar.style.position = 'relative';
            bar.appendChild(label);
        }
        
        bar.appendChild(fill);
        this.container.innerHTML = '';
        this.container.appendChild(bar);
        
        this.bar = bar;
        this.fill = fill;
        this.label = bar.querySelector('.progress-label');
    }
    
    setProgress(value) {
        value = Math.max(0, Math.min(100, value));
        
        if (this.fill) {
            this.fill.style.width = value + '%';
        }
        
        if (this.label) {
            this.label.textContent = Math.round(value) + '%';
        }
        
        // Change color based on progress
        if (this.options.autoColor) {
            if (value < 30) {
                this.fill.className = 'progress-bar-fill danger';
            } else if (value < 70) {
                this.fill.className = 'progress-bar-fill warning';
            } else {
                this.fill.className = 'progress-bar-fill success';
            }
        }
    }
    
    setIndeterminate(indeterminate = true) {
        if (this.bar) {
            if (indeterminate) {
                this.bar.classList.add('progress-bar-indeterminate');
                if (this.fill) this.fill.style.display = 'none';
            } else {
                this.bar.classList.remove('progress-bar-indeterminate');
                if (this.fill) this.fill.style.display = 'block';
            }
        }
    }
    
    reset() {
        this.setProgress(0);
    }
    
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// ==================== CIRCULAR PROGRESS ====================

class CircularProgress {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            size: options.size || 'md', // sm, md, lg
            showLabel: options.showLabel !== false,
            ...options
        };
        
        this.create();
    }
    
    create() {
        if (!this.container) return;
        
        const progress = document.createElement('div');
        progress.className = `circular-progress ${this.options.size}`;
        progress.style.setProperty('--progress-angle', '0deg');
        
        if (this.options.showLabel) {
            const label = document.createElement('div');
            label.className = 'circular-progress-text';
            label.textContent = '0%';
            progress.appendChild(label);
        }
        
        this.container.innerHTML = '';
        this.container.appendChild(progress);
        
        this.progress = progress;
        this.label = progress.querySelector('.circular-progress-text');
    }
    
    setProgress(value) {
        value = Math.max(0, Math.min(100, value));
        const angle = (value / 100) * 360;
        
        if (this.progress) {
            this.progress.style.setProperty('--progress-angle', angle + 'deg');
        }
        
        if (this.label) {
            this.label.textContent = Math.round(value) + '%';
        }
    }
    
    reset() {
        this.setProgress(0);
    }
    
    destroy() {
        if (this.container) {
            this.container.innerHTML = '';
        }
    }
}

// ==================== UPLOAD PROGRESS CARD ====================

class UploadProgressCard {
    constructor(file, containerId) {
        this.file = file;
        this.container = document.getElementById(containerId);
        this.id = 'upload-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        this.startTime = Date.now();
        this.bytesUploaded = 0;
        
        this.create();
    }
    
    create() {
        if (!this.container) return;
        
        const card = document.createElement('div');
        card.className = 'upload-progress-card';
        card.id = this.id;
        
        const fileIcon = this.getFileIcon(this.file.name);
        const fileSize = this.formatFileSize(this.file.size);
        
        card.innerHTML = `
            <div class="upload-progress-header">
                <div class="upload-file-info">
                    <div class="upload-file-icon">
                        <i class="${fileIcon}"></i>
                    </div>
                    <div class="upload-file-details">
                        <h4>${this.truncateFilename(this.file.name, 40)}</h4>
                        <p>${fileSize}</p>
                    </div>
                </div>
                <div class="upload-progress-actions">
                    <button class="btn-icon btn-sm" onclick="uploadProgressCards['${this.id}'].pause()" title="Pause">
                        <i class="fas fa-pause"></i>
                    </button>
                    <button class="btn-icon btn-sm btn-danger" onclick="uploadProgressCards['${this.id}'].cancel()" title="Cancel">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
            <div class="upload-progress-body">
                <div class="upload-stats">
                    <span class="upload-percentage">0%</span>
                    <span class="upload-speed">0 MB/s</span>
                    <span class="upload-eta">Calculating...</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: 0%"></div>
                </div>
            </div>
        `;
        
        this.container.appendChild(card);
        this.card = card;
        
        // Store reference
        if (!window.uploadProgressCards) {
            window.uploadProgressCards = {};
        }
        window.uploadProgressCards[this.id] = this;
    }
    
    updateProgress(bytesUploaded, totalBytes) {
        this.bytesUploaded = bytesUploaded;
        const percentage = (bytesUploaded / totalBytes) * 100;
        
        // Update progress bar
        const fill = this.card.querySelector('.progress-bar-fill');
        if (fill) {
            fill.style.width = percentage + '%';
        }
        
        // Update percentage
        const percentText = this.card.querySelector('.upload-percentage');
        if (percentText) {
            percentText.textContent = Math.round(percentage) + '%';
        }
        
        // Calculate speed
        const elapsed = (Date.now() - this.startTime) / 1000; // seconds
        const speed = bytesUploaded / elapsed; // bytes per second
        const speedMB = (speed / (1024 * 1024)).toFixed(2);
        
        const speedText = this.card.querySelector('.upload-speed');
        if (speedText) {
            speedText.textContent = speedMB + ' MB/s';
        }
        
        // Calculate ETA
        const remaining = totalBytes - bytesUploaded;
        const eta = remaining / speed; // seconds
        
        const etaText = this.card.querySelector('.upload-eta');
        if (etaText) {
            if (isFinite(eta) && eta > 0) {
                etaText.textContent = this.formatTime(eta);
            } else {
                etaText.textContent = 'Calculating...';
            }
        }
    }
    
    complete() {
        if (this.card) {
            this.card.classList.add('completed');
            
            const actions = this.card.querySelector('.upload-progress-actions');
            if (actions) {
                actions.innerHTML = `
                    <button class="btn-icon btn-sm" onclick="uploadProgressCards['${this.id}'].remove()" title="Remove">
                        <i class="fas fa-check-circle" style="color: #43e97b;"></i>
                    </button>
                `;
            }
            
            const speedText = this.card.querySelector('.upload-speed');
            if (speedText) {
                speedText.innerHTML = '<i class="fas fa-check"></i> Completed';
                speedText.style.color = '#43e97b';
            }
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.remove();
        }, 5000);
    }
    
    error(message) {
        if (this.card) {
            this.card.classList.add('error');
            
            const speedText = this.card.querySelector('.upload-speed');
            if (speedText) {
                speedText.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + message;
                speedText.style.color = '#f56565';
            }
            
            const fill = this.card.querySelector('.progress-bar-fill');
            if (fill) {
                fill.className = 'progress-bar-fill danger';
            }
        }
    }
    
    pause() {
        console.log('Pause upload:', this.file.name);
        // Implement pause logic
    }
    
    cancel() {
        console.log('Cancel upload:', this.file.name);
        this.remove();
        // Implement cancel logic
    }
    
    remove() {
        if (this.card) {
            this.card.style.animation = 'slideUp 0.3s ease reverse';
            setTimeout(() => {
                if (this.card) {
                    this.card.remove();
                }
                delete window.uploadProgressCards[this.id];
            }, 300);
        }
    }
    
    // Helper methods
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const iconMap = {
            jpg: 'fas fa-file-image', jpeg: 'fas fa-file-image', png: 'fas fa-file-image',
            gif: 'fas fa-file-image', bmp: 'fas fa-file-image',
            mp4: 'fas fa-file-video', avi: 'fas fa-file-video', mov: 'fas fa-file-video',
            pdf: 'fas fa-file-pdf', doc: 'fas fa-file-word', docx: 'fas fa-file-word',
            xls: 'fas fa-file-excel', xlsx: 'fas fa-file-excel',
            zip: 'fas fa-file-archive', rar: 'fas fa-file-archive',
            mp3: 'fas fa-file-audio', wav: 'fas fa-file-audio',
        };
        return iconMap[ext] || 'fas fa-file';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    formatTime(seconds) {
        if (seconds < 60) return Math.round(seconds) + 's';
        if (seconds < 3600) return Math.round(seconds / 60) + 'm';
        return Math.round(seconds / 3600) + 'h';
    }
    
    truncateFilename(filename, maxLength) {
        if (filename.length <= maxLength) return filename;
        const ext = filename.split('.').pop();
        const name = filename.substring(0, filename.length - ext.length - 1);
        return name.substring(0, maxLength - ext.length - 4) + '...' + '.' + ext;
    }
}

// ==================== SKELETON LOADER ====================

const SkeletonLoader = {
    showFileCards(containerId, count = 6) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-file-card';
            skeleton.innerHTML = `
                <div class="skeleton-file-preview"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text short"></div>
            `;
            container.appendChild(skeleton);
        }
    },
    
    showStatCards(containerId, count = 4) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-stat-card';
            skeleton.innerHTML = `
                <div class="skeleton-circle"></div>
                <div style="flex: 1;">
                    <div class="skeleton-text medium"></div>
                    <div class="skeleton-text short"></div>
                </div>
            `;
            container.appendChild(skeleton);
        }
    },
    
    showList(containerId, count = 5) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        container.innerHTML = '';
        
        for (let i = 0; i < count; i++) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-card';
            skeleton.innerHTML = `
                <div class="skeleton-text"></div>
                <div class="skeleton-text medium"></div>
                <div class="skeleton-text short"></div>
            `;
            container.appendChild(skeleton);
        }
    },
    
    hide(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
        }
    }
};

// ==================== STEP PROGRESS ====================

class StepProgress {
    constructor(containerId, steps) {
        this.container = document.getElementById(containerId);
        this.steps = steps; // Array of step labels
        this.currentStep = 0;
        
        this.create();
    }
    
    create() {
        if (!this.container) return;
        
        const progress = document.createElement('div');
        progress.className = 'step-progress';
        
        this.steps.forEach((label, index) => {
            const step = document.createElement('div');
            step.className = 'step';
            step.innerHTML = `
                <div class="step-circle">${index + 1}</div>
                <div class="step-label">${label}</div>
            `;
            progress.appendChild(step);
        });
        
        this.container.innerHTML = '';
        this.container.appendChild(progress);
        
        this.progress = progress;
        this.updateStep(0);
    }
    
    updateStep(stepIndex) {
        if (!this.progress) return;
        
        this.currentStep = stepIndex;
        const steps = this.progress.querySelectorAll('.step');
        
        steps.forEach((step, index) => {
            step.classList.remove('active', 'completed');
            
            if (index < stepIndex) {
                step.classList.add('completed');
                step.querySelector('.step-circle').innerHTML = '<i class="fas fa-check"></i>';
            } else if (index === stepIndex) {
                step.classList.add('active');
                step.querySelector('.step-circle').textContent = index + 1;
            } else {
                step.querySelector('.step-circle').textContent = index + 1;
            }
        });
    }
    
    next() {
        if (this.currentStep < this.steps.length - 1) {
            this.updateStep(this.currentStep + 1);
        }
    }
    
    prev() {
        if (this.currentStep > 0) {
            this.updateStep(this.currentStep - 1);
        }
    }
    
    reset() {
        this.updateStep(0);
    }
}

// Export for global use
window.LoadingOverlay = LoadingOverlay;
window.ProgressBar = ProgressBar;
window.CircularProgress = CircularProgress;
window.UploadProgressCard = UploadProgressCard;
window.SkeletonLoader = SkeletonLoader;
window.StepProgress = StepProgress;

// Example usage function
function demonstrateComponents() {
    console.log('Modern UI Components loaded!');
    
    // Example: Show loading overlay
    // LoadingOverlay.show('Processing...', 'Please wait while we complete your request');
    
    // Example: Create progress bar
    // const pb = new ProgressBar('myProgressContainer', { size: 'lg', variant: 'success' });
    // pb.setProgress(75);
    
    // Example: Create upload progress card
    // const file = { name: 'example.pdf', size: 1024 * 1024 * 5 }; // 5MB
    // const card = new UploadProgressCard(file, 'uploadQueue');
    // card.updateProgress(2621440, 5242880); // 50% uploaded
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', demonstrateComponents);
} else {
    demonstrateComponents();
}
