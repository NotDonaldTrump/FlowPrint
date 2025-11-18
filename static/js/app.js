// WebSocket connection
const socket = io();

// Global state
let currentConfig = {};
let isServiceRunning = false;
let countdownInterval = null;
let nextCheckTime = null;
let pollIntervalSeconds = 30;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadTheme();
    loadConfig();
    loadStatus();
    loadLogs();
    setupWebSocket();
    
    // Auto-cleanup toggle
    document.getElementById('cleanupEnabled').addEventListener('change', function() {
        document.getElementById('cleanupHoursGroup').style.display = this.checked ? 'block' : 'none';
    });
    
    // Load status every 5 seconds as fallback
    setInterval(loadStatus, 5000);
});

// ============================================
// Theme Management
// ============================================

function loadTheme() {
    const saved = localStorage.getItem('flowprint-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
    updateThemeIcon(saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const newTheme = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('flowprint-theme', newTheme);
    updateThemeIcon(newTheme);
    
    // Update config
    currentConfig.theme = newTheme;
    saveConfig();
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    // Simple circle for dark mode, filled circle for light mode
    icon.textContent = theme === 'dark' ? '◐' : '◑';
    icon.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
}

// ============================================
// Configuration Management
// ============================================

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        currentConfig = config;
        pollIntervalSeconds = config.poll_interval_seconds || 30;
        populateConfigForm(config);
    } catch (error) {
        showToast('Failed to load configuration', 'error');
        console.error('Error loading config:', error);
    }
}

function populateConfigForm(config) {
    document.getElementById('imapHost').value = config.imap_host || '';
    document.getElementById('imapPort').value = config.imap_port || 993;
    document.getElementById('imapUseSsl').checked = config.imap_use_ssl !== false;
    document.getElementById('imapUsername').value = config.imap_username || '';
    document.getElementById('imapPassword').value = config.imap_password || '';
    document.getElementById('mailbox').value = config.mailbox || 'Inbox';
    
    document.getElementById('subjectPrefix').value = config.subject_prefix || '[PRINT PACK]';
    document.getElementById('pollInterval').value = config.poll_interval_seconds || 30;
    document.getElementById('autoPrint').checked = config.auto_print_enabled !== false;
    document.getElementById('deleteAfterPrint').checked = config.delete_email_after_print === true;
    
    document.getElementById('chromePath').value = config.chrome_path || '';
    document.getElementById('chromeWait').value = config.chrome_print_wait_seconds || 8;
    document.getElementById('cleanupEnabled').checked = config.temp_file_cleanup_enabled !== false;
    document.getElementById('cleanupHours').value = config.temp_file_cleanup_hours || 6;
    
    // Show/hide cleanup hours based on enabled state
    document.getElementById('cleanupHoursGroup').style.display = 
        (config.temp_file_cleanup_enabled !== false) ? 'block' : 'none';
}

function getConfigFromForm() {
    return {
        imap_host: document.getElementById('imapHost').value.trim(),
        imap_port: parseInt(document.getElementById('imapPort').value),
        imap_use_ssl: document.getElementById('imapUseSsl').checked,
        imap_username: document.getElementById('imapUsername').value.trim(),
        imap_password: document.getElementById('imapPassword').value,
        mailbox: document.getElementById('mailbox').value.trim(),
        subject_prefix: document.getElementById('subjectPrefix').value.trim(),
        poll_interval_seconds: parseInt(document.getElementById('pollInterval').value),
        auto_print_enabled: document.getElementById('autoPrint').checked,
        delete_email_after_print: document.getElementById('deleteAfterPrint').checked,
        chrome_path: document.getElementById('chromePath').value.trim(),
        chrome_print_wait_seconds: parseInt(document.getElementById('chromeWait').value),
        temp_file_cleanup_enabled: document.getElementById('cleanupEnabled').checked,
        temp_file_cleanup_hours: parseInt(document.getElementById('cleanupHours').value),
        printed_uids_file: 'printed_uids.txt',
        log_file: 'flowprint.log',
        theme: document.documentElement.getAttribute('data-theme')
    };
}

async function saveConfig() {
    try {
        const config = getConfigFromForm();
        
        if (!config.imap_host || !config.imap_username || !config.imap_password) {
            showToast('Please fill in all required email settings', 'error');
            return;
        }
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ Configuration saved', 'success');
            currentConfig = config;
            pollIntervalSeconds = config.poll_interval_seconds;
        } else {
            showToast('Failed to save: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Failed to save configuration', 'error');
        console.error('Error saving config:', error);
    }
}

async function testConnection() {
    try {
        const config = getConfigFromForm();
        
        if (!config.imap_host || !config.imap_username || !config.imap_password) {
            showToast('Please fill in all email settings first', 'error');
            return;
        }
        
        showToast('Testing connection...', 'warning');
        
        const response = await fetch('/api/test-connection', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ ' + result.message, 'success');
        } else {
            showToast('✗ ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Connection test failed', 'error');
        console.error('Error testing connection:', error);
    }
}

// ============================================
// Service Management
// ============================================

async function startService() {
    try {
        showToast('Starting service...', 'warning');
        
        const response = await fetch('/api/start', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ Service started', 'success');
            loadStatus();
        } else {
            showToast('Failed to start: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Failed to start service', 'error');
        console.error('Error starting service:', error);
    }
}

async function stopService() {
    try {
        showToast('Stopping service...', 'warning');
        
        const response = await fetch('/api/stop', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ Service stopped', 'success');
            loadStatus();
        } else {
            showToast('Failed to stop: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Failed to stop service', 'error');
        console.error('Error stopping service:', error);
    }
}

async function manualCheck() {
    try {
        if (!isServiceRunning) {
            showToast('Service must be running to check inbox', 'error');
            return;
        }
        
        showToast('Checking inbox...', 'warning');
        
        const response = await fetch('/api/manual-check', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ Inbox check triggered', 'success');
        } else {
            showToast('Check failed: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Failed to trigger check', 'error');
        console.error('Error triggering check:', error);
    }
}

async function reprintJob(tempFile) {
    try {
        showToast('Reprinting...', 'warning');
        
        const response = await fetch('/api/reprint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ temp_file: tempFile })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ Job reprinted', 'success');
        } else {
            showToast('Reprint failed: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Failed to reprint', 'error');
        console.error('Error reprinting:', error);
    }
}

async function clearCache() {
    try {
        if (!confirm('This will delete all temporary print files. Continue?')) {
            return;
        }
        
        showToast('Clearing cache...', 'warning');
        
        const response = await fetch('/api/clear-cache', { method: 'POST' });
        const result = await response.json();
        
        if (result.success) {
            showToast('✓ Cache cleared', 'success');
            loadStatus();
        } else {
            showToast('Clear failed: ' + result.error, 'error');
        }
    } catch (error) {
        showToast('Failed to clear cache', 'error');
        console.error('Error clearing cache:', error);
    }
}

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

function updateUI(data) {
    isServiceRunning = data.running;
    
    const statusBanner = document.getElementById('statusBanner');
    const statusText = document.getElementById('statusText');
    const nextCheckDisplay = document.getElementById('nextCheckDisplay');
    const manualCheckBtn = document.getElementById('manualCheckBtn');
    
    statusBanner.className = 'status-banner';
    
    if (data.running) {
        statusBanner.classList.add('status-running');
        statusText.textContent = data.status;
        manualCheckBtn.disabled = false;
    } else {
        statusBanner.classList.add('status-stopped');
        statusText.textContent = 'Service Stopped';
        manualCheckBtn.disabled = true;
    }
    
    document.getElementById('startBtn').disabled = data.running;
    document.getElementById('stopBtn').disabled = !data.running;
    
    if (data.stats) {
        nextCheckDisplay.textContent = data.stats.next_check || '--:--:--';
        
        if (data.running && data.stats.next_check && data.stats.next_check !== 'Pending...' && !data.status.includes('Scanning')) {
            startCountdown(data.stats.next_check);
        } else {
            stopCountdown();
        }
        
        document.getElementById('messagesFound').textContent = data.stats.messages_found || 0;
        document.getElementById('jobsProcessed').textContent = data.stats.jobs_processed || 0;
        document.getElementById('jobsPending').textContent = data.stats.jobs_pending || 0;
        
        updateRecentJobs(data.stats.recent_jobs || []);
        updateErrors(data.stats.errors || []);
    }
}

function updateRecentJobs(jobs) {
    const container = document.getElementById('recentJobs');
    
    if (jobs.length === 0) {
        container.innerHTML = '<div class="empty-state">No jobs yet</div>';
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-item">
            <div class="job-content">
                <div class="job-time">${job.time}</div>
                <div class="job-subject" title="${escapeHtml(job.subject)}">${escapeHtml(job.subject)}</div>
                <div class="job-action">${escapeHtml(job.action)}</div>
            </div>
            <div class="job-actions">
                ${job.can_reprint ? 
                    `<button class="btn-reprint" onclick="reprintJob('${job.temp_file}')">🖨️ Reprint</button>` : 
                    `<button class="btn-reprint" disabled title="File has been cleaned up">🖨️</button>`
                }
            </div>
        </div>
    `).join('');
}

function updateErrors(errors) {
    const container = document.getElementById('recentErrors');
    const card = document.getElementById('errorsCard');
    
    if (errors.length === 0) {
        card.style.display = 'none';
        return;
    }
    
    card.style.display = 'block';
    container.innerHTML = errors.map(error => `
        <div class="error-item">
            <div class="error-time">${error.time}</div>
            <div class="error-message">${escapeHtml(error.message)}</div>
        </div>
    `).join('');
}

// ============================================
// Countdown Timer Functions
// ============================================

function startCountdown(nextCheckTimeStr) {
    const now = new Date();
    const timeParts = nextCheckTimeStr.split(':');
    
    nextCheckTime = new Date();
    nextCheckTime.setHours(parseInt(timeParts[0]));
    nextCheckTime.setMinutes(parseInt(timeParts[1]));
    nextCheckTime.setSeconds(parseInt(timeParts[2]));
    
    if (nextCheckTime < now) {
        nextCheckTime.setDate(nextCheckTime.getDate() + 1);
    }
    
    pollIntervalSeconds = currentConfig.poll_interval_seconds || 30;
    
    document.getElementById('countdownMini').style.display = 'flex';
    
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    
    updateCountdown();
    countdownInterval = setInterval(updateCountdown, 1000);
}

function stopCountdown() {
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    document.getElementById('countdownMini').style.display = 'none';
}

function updateCountdown() {
    if (!nextCheckTime) {
        stopCountdown();
        return;
    }
    
    const now = new Date();
    const diff = nextCheckTime - now;
    
    if (diff <= 0) {
        document.getElementById('countdownTime').textContent = '0s';
        document.getElementById('countdownBar').style.width = '0%';
        return;
    }
    
    const totalSeconds = Math.floor(diff / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    let displayText;
    if (minutes > 0) {
        displayText = `${minutes}m ${seconds}s`;
    } else {
        displayText = `${seconds}s`;
    }
    
    document.getElementById('countdownTime').textContent = displayText;
    
    const percentageRemaining = (totalSeconds / pollIntervalSeconds) * 100;
    document.getElementById('countdownBar').style.width = `${Math.min(100, percentageRemaining)}%`;
    
    const countdownMini = document.getElementById('countdownMini');
    if (totalSeconds <= 10 && totalSeconds > 0) {
        countdownMini.classList.add('urgent');
    } else {
        countdownMini.classList.remove('urgent');
    }
}

// ============================================
// Activity Log
// ============================================

async function loadLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        const container = document.getElementById('activityLog');
        
        if (data.logs && data.logs.length > 0) {
            container.innerHTML = data.logs.map(line => 
                `<div class="log-line">${escapeHtml(line)}</div>`
            ).join('');
            container.scrollTop = container.scrollHeight;
        } else {
            container.innerHTML = '<div class="empty-state">No logs yet</div>';
        }
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

function refreshLogs() {
    loadLogs();
    showToast('Logs refreshed', 'success');
}

// ============================================
// WebSocket Handlers
// ============================================

function setupWebSocket() {
    socket.on('connect', () => console.log('WebSocket connected'));
    socket.on('disconnect', () => console.log('WebSocket disconnected'));
    
    socket.on('status_update', (data) => {
        updateUI({
            running: true,
            status: data.status,
            stats: data.stats
        });
    });
}

// ============================================
// UI Helpers
// ============================================

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tabName + 'Tab').classList.add('active');
    event.target.classList.add('active');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast ' + type;
    
    setTimeout(() => toast.classList.add('show'), 100);
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// Keyboard Shortcuts
// ============================================

document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveConfig();
    }
    
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshLogs();
    }
});

// ============================================
// Cleanup
// ============================================

window.addEventListener('beforeunload', () => stopCountdown());