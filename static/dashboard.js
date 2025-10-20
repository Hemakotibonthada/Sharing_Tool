/**
 * NetShare Pro - Dashboard with Charts and Graphs
 * Provides real-time data visualization and analytics
 */

// Chart.js Configuration
let uploadTrendChart = null;
let fileTypeChart = null;
let transferSpeedChart = null;
let storageUsageChart = null;
let userActivityChart = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeTheme();
    initializeCharts();
    loadDashboardData();
    startRealTimeUpdates();
});

// Theme Management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update charts for new theme
    updateChartsTheme(newTheme);
    
    showToast('Theme changed to ' + newTheme + ' mode', 'info');
}

// Initialize All Charts
function initializeCharts() {
    createUploadTrendChart();
    createFileTypeChart();
    createTransferSpeedChart();
    createStorageUsageChart();
    createUserActivityChart();
}

// Upload Trend Chart (Line Chart)
function createUploadTrendChart() {
    const ctx = document.getElementById('uploadTrendChart');
    if (!ctx) return;
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#eaeaea' : '#212529';
    const gridColor = isDark ? '#2d3748' : '#dee2e6';
    
    uploadTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: getLast7Days(),
            datasets: [{
                label: 'Uploads',
                data: [12, 19, 15, 25, 22, 30, 28],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#667eea'
            }, {
                label: 'Downloads',
                data: [8, 15, 12, 18, 20, 25, 23],
                borderColor: '#43e97b',
                backgroundColor: 'rgba(67, 233, 123, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#43e97b'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: textColor,
                        padding: 15,
                        font: { size: 12, weight: 'bold' }
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? '#16213e' : '#ffffff',
                    titleColor: textColor,
                    bodyColor: textColor,
                    borderColor: gridColor,
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' files';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                },
                x: {
                    grid: { color: gridColor },
                    ticks: { color: textColor }
                }
            }
        }
    });
}

// File Type Distribution (Doughnut Chart)
function createFileTypeChart() {
    const ctx = document.getElementById('fileTypeChart');
    if (!ctx) return;
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#eaeaea' : '#212529';
    
    fileTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Images', 'Documents', 'Videos', 'Archives', 'Other'],
            datasets: [{
                data: [35, 25, 20, 15, 5],
                backgroundColor: [
                    '#667eea',
                    '#764ba2',
                    '#f093fb',
                    '#4facfe',
                    '#43e97b'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        color: textColor,
                        padding: 15,
                        font: { size: 12 },
                        generateLabels: function(chart) {
                            const data = chart.data;
                            return data.labels.map((label, i) => {
                                const value = data.datasets[0].data[i];
                                const total = data.datasets[0].data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return {
                                    text: `${label} (${percentage}%)`,
                                    fillStyle: data.datasets[0].backgroundColor[i],
                                    index: i
                                };
                            });
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const value = context.parsed;
                            const percentage = Math.round((value / total) * 100);
                            return context.label + ': ' + value + ' files (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

// Transfer Speed Chart (Bar Chart)
function createTransferSpeedChart() {
    const ctx = document.getElementById('transferSpeedChart');
    if (!ctx) return;
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#eaeaea' : '#212529';
    const gridColor = isDark ? '#2d3748' : '#dee2e6';
    
    transferSpeedChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
            datasets: [{
                label: 'Average Speed (Mbps)',
                data: [120, 450, 380, 520, 480, 350],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(240, 147, 251, 0.8)',
                    'rgba(79, 172, 254, 0.8)',
                    'rgba(67, 233, 123, 0.8)',
                    'rgba(56, 249, 215, 0.8)'
                ],
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Speed: ' + context.parsed.y + ' Mbps';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: gridColor },
                    ticks: {
                        color: textColor,
                        callback: function(value) {
                            return value + ' Mbps';
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: textColor }
                }
            }
        }
    });
}

// Storage Usage Chart (Gauge/Doughnut)
function createStorageUsageChart() {
    const ctx = document.getElementById('storageUsageChart');
    if (!ctx) return;
    
    const usedStorage = 65; // percentage
    
    storageUsageChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [usedStorage, 100 - usedStorage],
                backgroundColor: [
                    '#667eea',
                    '#e9ecef'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '80%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false }
            }
        }
    });
    
    // Update storage info
    const storageInfo = document.querySelector('.storage-info');
    if (storageInfo) {
        storageInfo.innerHTML = `
            <div class="storage-percentage">${usedStorage}%</div>
            <div class="storage-label">Storage Used</div>
            <div class="storage-details" style="margin-top: 10px; font-size: 0.75rem; color: var(--text-secondary);">
                650 GB / 1 TB
            </div>
        `;
    }
}

// User Activity Chart (Polar Area)
function createUserActivityChart() {
    const ctx = document.getElementById('userActivityChart');
    if (!ctx) return;
    
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#eaeaea' : '#212529';
    
    userActivityChart = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                data: [85, 92, 78, 95, 88, 45, 35],
                backgroundColor: [
                    'rgba(102, 126, 234, 0.6)',
                    'rgba(118, 75, 162, 0.6)',
                    'rgba(240, 147, 251, 0.6)',
                    'rgba(79, 172, 254, 0.6)',
                    'rgba(67, 233, 123, 0.6)',
                    'rgba(237, 137, 54, 0.6)',
                    'rgba(245, 101, 101, 0.6)'
                ],
                borderWidth: 2,
                borderColor: isDark ? '#16213e' : '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'right',
                    labels: {
                        color: textColor,
                        padding: 10,
                        font: { size: 11 }
                    }
                }
            },
            scales: {
                r: {
                    grid: { color: isDark ? '#2d3748' : '#dee2e6' },
                    ticks: { color: textColor, backdropColor: 'transparent' },
                    pointLabels: { color: textColor }
                }
            }
        }
    });
}

// Update Charts Theme
function updateChartsTheme(theme) {
    const isDark = theme === 'dark';
    const textColor = isDark ? '#eaeaea' : '#212529';
    const gridColor = isDark ? '#2d3748' : '#dee2e6';
    
    const charts = [uploadTrendChart, fileTypeChart, transferSpeedChart, storageUsageChart, userActivityChart];
    
    charts.forEach(chart => {
        if (chart && chart.options) {
            // Update text colors
            if (chart.options.plugins && chart.options.plugins.legend) {
                chart.options.plugins.legend.labels.color = textColor;
            }
            
            // Update scale colors
            if (chart.options.scales) {
                Object.keys(chart.options.scales).forEach(scale => {
                    if (chart.options.scales[scale].grid) {
                        chart.options.scales[scale].grid.color = gridColor;
                    }
                    if (chart.options.scales[scale].ticks) {
                        chart.options.scales[scale].ticks.color = textColor;
                    }
                    if (chart.options.scales[scale].pointLabels) {
                        chart.options.scales[scale].pointLabels.color = textColor;
                    }
                });
            }
            
            chart.update();
        }
    });
}

// Load Dashboard Data
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/stats', {
            headers: {
                'Authorization': 'Bearer ' + getAuthToken()
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateDashboardStats(data);
            updateActivityFeed(data.recentActivity);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

// Update Dashboard Stats
function updateDashboardStats(data) {
    // Update stat cards with animation
    animateValue('total-files', 0, data.totalFiles || 0, 1000);
    animateValue('total-users', 0, data.totalUsers || 0, 1000);
    animateValue('total-storage', 0, data.totalStorage || 0, 1000);
    animateValue('avg-speed', 0, data.avgSpeed || 0, 1000);
}

// Animate Number
function animateValue(id, start, end, duration) {
    const element = document.getElementById(id);
    if (!element) return;
    
    const range = end - start;
    const increment = range / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current).toLocaleString();
    }, 16);
}

// Update Activity Feed
function updateActivityFeed(activities) {
    const feed = document.getElementById('activity-feed');
    if (!feed || !activities) return;
    
    feed.innerHTML = activities.map(activity => `
        <div class="activity-item fade-in">
            <div class="activity-icon ${activity.type}">
                ${getActivityIcon(activity.type)}
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-description">${activity.description}</div>
                <div class="activity-time">${formatTime(activity.timestamp)}</div>
            </div>
        </div>
    `).join('');
}

// Get Activity Icon
function getActivityIcon(type) {
    const icons = {
        upload: '📤',
        download: '📥',
        delete: '🗑️',
        user: '👤',
        settings: '⚙️'
    };
    return icons[type] || '📄';
}

// Format Time
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = Math.floor((now - date) / 1000);
    
    if (diff < 60) return 'Just now';
    if (diff < 3600) return Math.floor(diff / 60) + ' minutes ago';
    if (diff < 86400) return Math.floor(diff / 3600) + ' hours ago';
    return Math.floor(diff / 86400) + ' days ago';
}

// Get Last 7 Days
function getLast7Days() {
    const days = [];
    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    return days;
}

// Real-Time Updates
function startRealTimeUpdates() {
    // Update every 30 seconds
    setInterval(loadDashboardData, 30000);
    
    // Update clock
    setInterval(updateClock, 1000);
}

// Update Clock
function updateClock() {
    const clockElement = document.getElementById('dashboard-clock');
    if (clockElement) {
        const now = new Date();
        clockElement.textContent = now.toLocaleTimeString();
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.querySelector('.toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-icon">${getToastIcon(type)}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ',
        warning: '⚠'
    };
    return icons[type] || 'ℹ';
}

// Chart Filter (Time Range)
function filterChart(chartName, timeRange) {
    // Update chart data based on time range
    showToast(`Chart filtered to ${timeRange}`, 'info');
    
    // Set active button
    document.querySelectorAll(`.chart-filter button`).forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
}

// Export Chart
function exportChart(chartId) {
    const chart = eval(chartId); // Get chart instance
    if (chart) {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${chartId}-${Date.now()}.png`;
        link.href = url;
        link.click();
        showToast('Chart exported successfully', 'success');
    }
}

// Get Auth Token
function getAuthToken() {
    return localStorage.getItem('authToken') || document.cookie.split('authToken=')[1]?.split(';')[0] || '';
}

// Refresh Dashboard
function refreshDashboard() {
    showToast('Refreshing dashboard...', 'info');
    loadDashboardData();
    
    // Refresh all charts
    [uploadTrendChart, fileTypeChart, transferSpeedChart, storageUsageChart, userActivityChart].forEach(chart => {
        if (chart) chart.update();
    });
}
