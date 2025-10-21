// ============================================
// Dashboard JavaScript
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    checkForRunningJobs();
    setupAutoRefresh();
});

// Check if there are any running jobs
function checkForRunningJobs() {
    const runningJobs = document.querySelectorAll('.badge-running');
    
    if (runningJobs.length > 0) {
        console.log(`Found ${runningJobs.length} running job(s)`);
        // Enable auto-refresh if there are running jobs
        return true;
    }
    return false;
}

// Setup auto-refresh for running jobs
function setupAutoRefresh() {
    const hasRunningJobs = checkForRunningJobs();
    
    if (hasRunningJobs) {
        console.log('Auto-refresh enabled (5 seconds)');
        setTimeout(() => {
            window.location.reload();
        }, 5000);
    }
}

// Add status icon mapping
const statusIcons = {
    'completed': 'check',
    'failed': 'times',
    'running': 'spinner fa-spin',
    'pending': 'clock'
};

// Custom template filter for status icons (if needed in JS)
function getStatusIcon(status) {
    return statusIcons[status] || 'question';
}

// Format time duration
function formatDuration(seconds) {
    if (!seconds) return '-';
    return `${seconds.toFixed(2)}s`;
}

// Format relative time
function timeAgo(dateString) {
    const date = new Date(dateString);
    const seconds = Math.floor((new Date() - date) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }
    
    return 'Just now';
}