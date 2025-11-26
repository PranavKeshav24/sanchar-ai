// Global JavaScript functions
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Notification system
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingAlerts = document.querySelectorAll('.alert-dismissible');
    existingAlerts.forEach(alert => {
        if (alert.parentElement) {
            alert.remove();
        }
    });

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentElement) {
            alertDiv.remove();
        }
    }, 5000);
}

function getIconForType(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'danger': return 'exclamation-triangle';
        case 'warning': return 'exclamation-circle';
        default: return 'info-circle';
    }
}

// File upload validation
function validateFile(input) {
    const file = input.files[0];
    const maxSize = 50 * 1024 * 1024; // 50MB
    const allowedTypes = [
        'video/mp4',
        'video/avi',
        'video/mov',
        'video/wmv',
        'video/mkv',
        'video/flv',
        'video/quicktime'
    ];
    
    if (!file) return true;
    
    if (file.size > maxSize) {
        showNotification('File size exceeds 50MB limit. Please choose a smaller file.', 'danger');
        input.value = '';
        return false;
    }
    
    if (!allowedTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|wmv|mkv|flv)$/i)) {
        showNotification('Please select a valid video file (MP4, AVI, MOV, WMV, MKV, FLV)', 'danger');
        input.value = '';
        return false;
    }
    
    return true;
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Utility function to debounce function calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}