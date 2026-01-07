/**
 * MINDSETHAPPYBOT Admin Panel JavaScript
 */

// State
let isLoggedIn = false;
let currentPage = 'overview';
let usersOffset = 0;
let messagesOffset = 0;
const pageSize = 50;

// DOM Elements
const loginScreen = document.getElementById('login-screen');
const dashboardScreen = document.getElementById('dashboard-screen');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');
const logoutBtn = document.getElementById('logout-btn');
const healthStatus = document.getElementById('health-status');
const navLinks = document.querySelectorAll('.nav-link');
const pages = document.querySelectorAll('.page');

// API Helper
async function api(endpoint, options = {}) {
    const response = await fetch(`/api${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

// Format date helper
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString();
}

function formatRelativeTime(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
}

// Authentication
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    loginError.textContent = '';

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        await api('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        isLoggedIn = true;
        localStorage.setItem('adminLoggedIn', 'true');
        showDashboard();
    } catch (error) {
        loginError.textContent = error.message;
    }
});

logoutBtn.addEventListener('click', () => {
    isLoggedIn = false;
    localStorage.removeItem('adminLoggedIn');
    showLogin();
});

function showLogin() {
    loginScreen.classList.add('active');
    dashboardScreen.classList.remove('active');
}

function showDashboard() {
    loginScreen.classList.remove('active');
    dashboardScreen.classList.add('active');
    loadOverview();
    checkHealth();
}

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        navigateTo(page);
    });
});

function navigateTo(page) {
    currentPage = page;

    // Update nav links
    navLinks.forEach(link => {
        link.classList.toggle('active', link.dataset.page === page);
    });

    // Update pages
    pages.forEach(p => {
        p.classList.toggle('active', p.id === `page-${page}`);
    });

    // Load page data
    switch (page) {
        case 'overview':
            loadOverview();
            break;
        case 'users':
            loadUsers();
            break;
        case 'messages':
            loadMessages();
            break;
        case 'logs':
            loadLogs();
            break;
        case 'notifications':
            loadNotifications();
            break;
        case 'feedback':
            loadFeedback();
            break;
    }
}

// Health Check
async function checkHealth() {
    try {
        const health = await api('/system/health');
        healthStatus.textContent = health.status.toUpperCase();
        healthStatus.className = `health-badge ${health.status}`;
    } catch (error) {
        healthStatus.textContent = 'ERROR';
        healthStatus.className = 'health-badge unhealthy';
    }
}

// Overview Page
async function loadOverview() {
    try {
        // Load stats
        const stats = await api('/stats');
        document.getElementById('stat-total-users').textContent = stats.total_users;
        document.getElementById('stat-active-24h').textContent = stats.active_users_24h;
        document.getElementById('stat-active-7d').textContent = stats.active_users_7d;
        document.getElementById('stat-total-moments').textContent = stats.total_moments;
        document.getElementById('stat-moments-today').textContent = stats.moments_today;
        document.getElementById('stat-moments-week').textContent = stats.moments_week;

        // Load recent activity
        const { conversations } = await api('/conversations?limit=10');
        const activityList = document.getElementById('recent-activity');

        if (conversations.length === 0) {
            activityList.innerHTML = '<p class="loading">No recent activity</p>';
        } else {
            activityList.innerHTML = conversations.map(conv => `
                <div class="activity-item">
                    <span class="activity-type ${conv.message_type}">${conv.message_type.replace('_', ' ')}</span>
                    <div class="activity-content">
                        <div class="activity-user">${conv.username || conv.first_name || `User #${conv.user_id}`}</div>
                        <div class="activity-text">${escapeHtml(conv.content)}</div>
                    </div>
                    <div class="activity-time">${formatRelativeTime(conv.created_at)}</div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Users Page
async function loadUsers(offset = 0, search = '') {
    usersOffset = offset;
    const tbody = document.querySelector('#users-table tbody');
    tbody.innerHTML = '<tr><td colspan="9" class="loading">Loading...</td></tr>';

    try {
        const params = new URLSearchParams({ limit: pageSize, offset });
        if (search) params.append('search', search);

        const { users, total } = await api(`/users?${params}`);

        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="loading">No users found</td></tr>';
        } else {
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.telegram_id}</td>
                    <td>${user.username || '-'}</td>
                    <td>${user.first_name || '-'}</td>
                    <td>${user.language_code}</td>
                    <td>${user.total_moments}</td>
                    <td>${user.current_streak}</td>
                    <td>${formatRelativeTime(user.last_active_at)}</td>
                    <td class="actions">
                        <button class="btn btn-primary btn-small" onclick="showUserDetail(${user.id})">View</button>
                    </td>
                </tr>
            `).join('');
        }

        renderPagination('users-pagination', total, offset, pageSize, (newOffset) => loadUsers(newOffset, search));
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = `<tr><td colspan="9" class="loading">Error: ${error.message}</td></tr>`;
    }
}

// User search
document.getElementById('user-search').addEventListener('input', debounce((e) => {
    loadUsers(0, e.target.value);
}, 300));

document.getElementById('refresh-users').addEventListener('click', () => {
    loadUsers(usersOffset, document.getElementById('user-search').value);
});

// User Detail Modal
async function showUserDetail(userId) {
    const modal = document.getElementById('user-modal');
    const modalBody = document.getElementById('user-modal-body');

    modal.classList.add('active');
    modalBody.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const user = await api(`/users/${userId}`);
        const { moments } = await api(`/users/${userId}/moments?limit=5`);

        modalBody.innerHTML = `
            <div class="user-detail-grid">
                <div class="detail-item">
                    <div class="detail-label">Telegram ID</div>
                    <div class="detail-value">${user.telegram_id}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Username</div>
                    <div class="detail-value">${user.username || '-'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Name</div>
                    <div class="detail-value">${user.first_name || '-'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Language</div>
                    <div class="detail-value">${user.language_code}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Address Form</div>
                    <div class="detail-value">${user.formal_address ? 'Formal (вы)' : 'Informal (ты)'}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Timezone</div>
                    <div class="detail-value">${user.timezone}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Active Hours</div>
                    <div class="detail-value">${user.active_hours_start} - ${user.active_hours_end}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Notification Interval</div>
                    <div class="detail-value">${user.notification_interval_hours}h</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Notifications</div>
                    <div class="detail-value">
                        <span class="status-badge ${user.notifications_enabled ? 'enabled' : 'disabled'}">
                            ${user.notifications_enabled ? 'Enabled' : 'Disabled'}
                        </span>
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Onboarding</div>
                    <div class="detail-value">
                        <span class="status-badge ${user.onboarding_completed ? 'enabled' : 'pending'}">
                            ${user.onboarding_completed ? 'Completed' : 'Pending'}
                        </span>
                    </div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Created</div>
                    <div class="detail-value">${formatDate(user.created_at)}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">Last Active</div>
                    <div class="detail-value">${formatDate(user.last_active_at)}</div>
                </div>
            </div>
            <div class="detail-section">
                <h4>Statistics</h4>
                <div class="user-detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">Total Moments</div>
                        <div class="detail-value">${user.total_moments}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Current Streak</div>
                        <div class="detail-value">${user.current_streak} days</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Longest Streak</div>
                        <div class="detail-value">${user.longest_streak} days</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Questions Sent</div>
                        <div class="detail-value">${user.total_questions_sent}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Questions Answered</div>
                        <div class="detail-value">${user.total_questions_answered}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Response Rate</div>
                        <div class="detail-value">${user.total_questions_sent > 0
                            ? Math.round((user.total_questions_answered / user.total_questions_sent) * 100)
                            : 0}%</div>
                    </div>
                </div>
            </div>
            ${moments.length > 0 ? `
                <div class="detail-section">
                    <h4>Recent Moments</h4>
                    <div class="activity-list">
                        ${moments.map(m => `
                            <div class="activity-item">
                                <span class="activity-type ${m.source_type}">${m.source_type}</span>
                                <div class="activity-content">
                                    <div class="activity-text">${escapeHtml(m.content)}</div>
                                </div>
                                <div class="activity-time">${formatRelativeTime(m.created_at)}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
    } catch (error) {
        modalBody.innerHTML = `<p class="error-message">Error loading user details: ${error.message}</p>`;
    }
}

// Modal close
document.querySelector('.modal-close').addEventListener('click', () => {
    document.getElementById('user-modal').classList.remove('active');
});

document.getElementById('user-modal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
        e.currentTarget.classList.remove('active');
    }
});

// Messages Page
async function loadMessages(offset = 0) {
    messagesOffset = offset;
    const tbody = document.querySelector('#messages-table tbody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading...</td></tr>';

    try {
        const messageType = document.getElementById('message-type-filter').value;
        const params = new URLSearchParams({ limit: pageSize, offset });
        if (messageType) params.append('message_type', messageType);

        const { messages, total } = await api(`/messages?${params}`);

        if (messages.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No messages found</td></tr>';
        } else {
            tbody.innerHTML = messages.map(msg => {
                const statusBadge = msg.status === 'pending'
                    ? '<span class="status-badge pending">Pending</span>'
                    : '<span class="status-badge sent">Sent</span>';
                const content = msg.content || '';
                return `
                <tr>
                    <td>${msg.id}</td>
                    <td>${msg.username || `User #${msg.user_id}`}</td>
                    <td><span class="activity-type ${msg.message_type}">${msg.message_type.replace(/_/g, ' ')}</span></td>
                    <td>${escapeHtml(content.substring(0, 100))}${content.length > 100 ? '...' : ''}</td>
                    <td>${statusBadge}</td>
                    <td>${formatRelativeTime(msg.time)}</td>
                </tr>
            `}).join('');
        }

        renderPagination('messages-pagination', total, offset, pageSize, loadMessages);
    } catch (error) {
        console.error('Error loading messages:', error);
        tbody.innerHTML = `<tr><td colspan="6" class="loading">Error: ${error.message}</td></tr>`;
    }
}

document.getElementById('message-type-filter').addEventListener('change', () => loadMessages(0));
document.getElementById('refresh-messages').addEventListener('click', () => loadMessages(messagesOffset));

// Logs Page
async function loadLogs() {
    const container = document.getElementById('logs-container');
    container.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const level = document.getElementById('log-level-filter').value;
        const params = new URLSearchParams({ limit: 100 });
        if (level) params.append('level', level);

        const { logs } = await api(`/system/logs?${params}`);

        if (logs.length === 0) {
            container.innerHTML = '<p class="loading" style="color: #94a3b8;">No logs found</p>';
        } else {
            container.innerHTML = logs.map(log => `
                <div class="log-entry">
                    <span class="log-level ${log.level}">${log.level}</span>
                    <span class="log-message">${escapeHtml(log.message)}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading logs:', error);
        container.innerHTML = `<p class="loading" style="color: #f87171;">Error: ${error.message}</p>`;
    }
}

document.getElementById('log-level-filter').addEventListener('change', loadLogs);
document.getElementById('refresh-logs').addEventListener('click', loadLogs);

// Notifications Page
async function loadNotifications() {
    const tbody = document.querySelector('#notifications-table tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading...</td></tr>';

    try {
        const pendingOnly = document.getElementById('pending-only-filter').checked;
        const params = new URLSearchParams({ limit: 50, pending_only: pendingOnly });

        const { notifications } = await api(`/system/notifications?${params}`);

        if (notifications.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No notifications found</td></tr>';
        } else {
            tbody.innerHTML = notifications.map(n => `
                <tr>
                    <td>${n.id}</td>
                    <td>${n.username || n.first_name || `User #${n.user_id}`}</td>
                    <td>${formatDate(n.scheduled_time)}</td>
                    <td>
                        <span class="status-badge ${n.sent ? 'sent' : 'pending'}">
                            ${n.sent ? 'Sent' : 'Pending'}
                        </span>
                    </td>
                    <td>${n.sent ? formatDate(n.sent_at) : '-'}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading notifications:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="loading">Error: ${error.message}</td></tr>`;
    }
}

document.getElementById('pending-only-filter').addEventListener('change', loadNotifications);
document.getElementById('refresh-notifications').addEventListener('click', loadNotifications);

// Feedback Page
let feedbackOffset = 0;

async function loadFeedback(offset = 0) {
    feedbackOffset = offset;

    // Load stats
    try {
        const stats = await api('/feedback/stats');
        document.getElementById('stat-feedback-new').textContent = stats.by_status.new;
        document.getElementById('stat-feedback-reviewed').textContent = stats.by_status.reviewed;
        document.getElementById('stat-feedback-implemented').textContent = stats.by_status.implemented;
        document.getElementById('stat-feedback-rejected').textContent = stats.by_status.rejected;
    } catch (error) {
        console.error('Error loading feedback stats:', error);
    }

    // Load feedback list
    const tbody = document.querySelector('#feedback-table tbody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">Loading...</td></tr>';

    try {
        const status = document.getElementById('feedback-status-filter').value;
        const params = new URLSearchParams({ limit: pageSize, offset });
        if (status) params.append('status', status);

        const { feedback, total } = await api(`/feedback?${params}`);

        if (feedback.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No feedback found</td></tr>';
        } else {
            tbody.innerHTML = feedback.map(f => `
                <tr>
                    <td>${f.id}</td>
                    <td>${f.username || f.first_name || `User #${f.user_id}`}</td>
                    <td><span class="feedback-category ${f.category}">${getCategoryLabel(f.category)}</span></td>
                    <td>${escapeHtml(f.content.substring(0, 80))}${f.content.length > 80 ? '...' : ''}</td>
                    <td><span class="feedback-status ${f.status}">${getStatusLabel(f.status)}</span></td>
                    <td>${formatRelativeTime(f.created_at)}</td>
                    <td class="actions">
                        <button class="btn btn-primary btn-small" onclick="showFeedbackDetail(${f.id}, ${JSON.stringify(f).replace(/"/g, '&quot;')})">View</button>
                    </td>
                </tr>
            `).join('');
        }

        renderPagination('feedback-pagination', total, offset, pageSize, loadFeedback);
    } catch (error) {
        console.error('Error loading feedback:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="loading">Error: ${error.message}</td></tr>`;
    }
}

function getCategoryLabel(category) {
    const labels = {
        'suggestion': '💡 Idea',
        'bug': '🐛 Bug',
        'other': '💬 Other'
    };
    return labels[category] || category;
}

function getStatusLabel(status) {
    const labels = {
        'new': 'New',
        'reviewed': 'Reviewed',
        'implemented': 'Implemented',
        'rejected': 'Rejected'
    };
    return labels[status] || status;
}

async function showFeedbackDetail(feedbackId, feedbackData) {
    const modal = document.getElementById('feedback-modal');
    const modalBody = document.getElementById('feedback-modal-body');

    modal.classList.add('active');

    modalBody.innerHTML = `
        <div class="feedback-detail">
            <div class="detail-section">
                <div class="user-detail-grid">
                    <div class="detail-item">
                        <div class="detail-label">User</div>
                        <div class="detail-value">${feedbackData.username || feedbackData.first_name || `User #${feedbackData.user_id}`}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Category</div>
                        <div class="detail-value">${getCategoryLabel(feedbackData.category)}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Status</div>
                        <div class="detail-value"><span class="feedback-status ${feedbackData.status}">${getStatusLabel(feedbackData.status)}</span></div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Created</div>
                        <div class="detail-value">${formatDate(feedbackData.created_at)}</div>
                    </div>
                </div>
            </div>
            <div class="detail-section">
                <h4>Content</h4>
                <div class="feedback-content-box">${escapeHtml(feedbackData.content)}</div>
            </div>
            <div class="detail-section">
                <h4>Update Status</h4>
                <div class="form-group">
                    <select id="feedback-status-select" class="select-input">
                        <option value="new" ${feedbackData.status === 'new' ? 'selected' : ''}>New</option>
                        <option value="reviewed" ${feedbackData.status === 'reviewed' ? 'selected' : ''}>Reviewed</option>
                        <option value="implemented" ${feedbackData.status === 'implemented' ? 'selected' : ''}>Implemented</option>
                        <option value="rejected" ${feedbackData.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Admin Notes</label>
                    <textarea id="feedback-admin-notes" class="textarea-input" rows="3">${feedbackData.admin_notes || ''}</textarea>
                </div>
                <button class="btn btn-primary" onclick="updateFeedbackStatus(${feedbackId})">Update Status</button>
            </div>
        </div>
    `;
}

async function updateFeedbackStatus(feedbackId) {
    const status = document.getElementById('feedback-status-select').value;
    const adminNotes = document.getElementById('feedback-admin-notes').value;

    try {
        await api(`/feedback/${feedbackId}/status`, {
            method: 'POST',
            body: JSON.stringify({ status, admin_notes: adminNotes })
        });

        // Close modal and reload
        document.getElementById('feedback-modal').classList.remove('active');
        loadFeedback(feedbackOffset);
    } catch (error) {
        alert('Error updating feedback: ' + error.message);
    }
}

// Feedback modal close handlers
document.querySelector('#feedback-modal .modal-close')?.addEventListener('click', () => {
    document.getElementById('feedback-modal').classList.remove('active');
});

document.getElementById('feedback-modal')?.addEventListener('click', (e) => {
    if (e.target === e.currentTarget) {
        e.currentTarget.classList.remove('active');
    }
});

document.getElementById('feedback-status-filter')?.addEventListener('change', () => loadFeedback(0));
document.getElementById('refresh-feedback')?.addEventListener('click', () => loadFeedback(feedbackOffset));

// Make showFeedbackDetail globally accessible
window.showFeedbackDetail = showFeedbackDetail;
window.updateFeedbackStatus = updateFeedbackStatus;

// Pagination helper
function renderPagination(containerId, total, offset, limit, loadFn) {
    const container = document.getElementById(containerId);
    const totalPages = Math.ceil(total / limit);
    const currentPage = Math.floor(offset / limit) + 1;

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // Previous button
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="(${loadFn.toString()})(${(currentPage - 2) * limit})">Prev</button>`;

    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="(${loadFn.toString()})(${(i - 1) * limit})">${i}</button>`;
    }

    // Next button
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="(${loadFn.toString()})(${currentPage * limit})">Next</button>`;

    container.innerHTML = html;
}

// Utility functions
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function debounce(fn, delay) {
    let timeout;
    return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn(...args), delay);
    };
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (localStorage.getItem('adminLoggedIn') === 'true') {
        isLoggedIn = true;
        showDashboard();
    } else {
        showLogin();
    }

    // Periodic health check
    setInterval(checkHealth, 30000);
});

// Make showUserDetail globally accessible
window.showUserDetail = showUserDetail;
