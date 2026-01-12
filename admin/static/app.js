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

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    return num.toLocaleString();
}

function formatGender(gender) {
    if (!gender || gender === 'unknown') return '-';
    if (gender === 'male') return '👨 M';
    if (gender === 'female') return '👩 F';
    return gender;
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
        case 'moments':
            loadMomentsPage();
            break;
        case 'knowledge':
            loadKnowledgePage();
            break;
        case 'templates':
            loadTemplatesPage();
            break;
        case 'dialogs':
            loadDialogsPage();
            break;
        case 'messages':
            loadMessages();
            break;
        case 'logs':
            loadLogsPage();
            break;
        case 'notifications':
            loadNotificationsUsers();
            loadNotifications(0);
            break;
        case 'feedback':
            loadFeedback();
            break;
        case 'expenses':
            loadExpenses();
            break;
        case 'analytics':
            loadAnalyticsPage();
            break;
        case 'settings':
            loadSettingsPage();
            break;
    }
}

// Health Check
async function checkHealth() {
    try {
        const health = await api('/system/health');
        healthStatus.textContent = health.status.toUpperCase();
        healthStatus.className = `health-badge ${health.status}`;

        // Update system status cards on overview page
        updateSystemStatusCards(health);
    } catch (error) {
        healthStatus.textContent = 'ERROR';
        healthStatus.className = 'health-badge unhealthy';
    }
}

// Update system status cards
function updateSystemStatusCards(health) {
    // Database status
    const dbIndicator = document.getElementById('status-db');
    const dbDetail = document.getElementById('status-db-detail');
    if (dbIndicator && dbDetail) {
        const dbOk = health.database === 'healthy';
        dbIndicator.textContent = dbOk ? 'CONNECTED' : 'ERROR';
        dbIndicator.className = `status-indicator ${dbOk ? 'healthy' : 'unhealthy'}`;

        if (health.database_details) {
            dbDetail.textContent = `Size: ${health.database_details.db_size || '-'}`;
        }
    }

    // Bot status
    const botIndicator = document.getElementById('status-bot');
    const botDetail = document.getElementById('status-bot-detail');
    if (botIndicator && botDetail) {
        botIndicator.textContent = health.bot === 'running' ? 'RUNNING' : health.bot.toUpperCase();
        botIndicator.className = `status-indicator ${health.bot}`;

        if (health.database_details) {
            const pending = health.database_details.pending_notifications || 0;
            botDetail.textContent = `${pending} pending notifications`;
        }
    }

    // OpenAI status
    const openaiIndicator = document.getElementById('status-openai');
    const openaiDetail = document.getElementById('status-openai-detail');
    if (openaiIndicator && openaiDetail) {
        const configured = health.openai === 'configured';
        openaiIndicator.textContent = configured ? 'CONFIGURED' : 'NOT CONFIGURED';
        openaiIndicator.className = `status-indicator ${health.openai}`;
        openaiDetail.textContent = configured ? 'API key set' : 'API key not set';
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
function getUsersFilters() {
    return {
        search: document.getElementById('user-search')?.value || '',
        language: document.getElementById('user-language-filter')?.value || '',
        status: document.getElementById('user-status-filter')?.value || '',
        sort: document.getElementById('user-sort-filter')?.value || '',
    };
}

async function loadUsers(offset = 0) {
    usersOffset = offset;
    const tbody = document.querySelector('#users-table tbody');
    tbody.innerHTML = '<tr><td colspan="10" class="loading">Loading...</td></tr>';

    try {
        const filters = getUsersFilters();
        const params = new URLSearchParams({ limit: pageSize, offset });

        if (filters.search) params.append('search', filters.search);
        if (filters.language) params.append('language', filters.language);
        if (filters.status) params.append('status', filters.status);
        if (filters.sort) params.append('sort', filters.sort);

        const { users, total } = await api(`/users?${params}`);

        if (users.length === 0) {
            tbody.innerHTML = '<tr><td colspan="10" class="loading">No users found</td></tr>';
        } else {
            tbody.innerHTML = users.map(user => `
                <tr>
                    <td>${user.id}</td>
                    <td>${user.telegram_id}</td>
                    <td>${user.username || '-'}</td>
                    <td>${user.first_name || '-'}</td>
                    <td>${formatGender(user.gender)}</td>
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

        renderPagination('users-pagination', total, offset, pageSize, loadUsers);
    } catch (error) {
        console.error('Error loading users:', error);
        tbody.innerHTML = `<tr><td colspan="10" class="loading">Error: ${error.message}</td></tr>`;
    }
}

// User search and filters
document.getElementById('user-search')?.addEventListener('input', debounce(() => {
    loadUsers(0);
}, 300));

document.getElementById('user-language-filter')?.addEventListener('change', () => loadUsers(0));
document.getElementById('user-status-filter')?.addEventListener('change', () => loadUsers(0));
document.getElementById('user-sort-filter')?.addEventListener('change', () => loadUsers(0));

document.getElementById('refresh-users')?.addEventListener('click', () => {
    loadUsers(usersOffset);
});

document.getElementById('export-users')?.addEventListener('click', () => {
    const filters = getUsersFilters();
    const params = new URLSearchParams();
    if (filters.search) params.append('search', filters.search);
    if (filters.language) params.append('language', filters.language);
    if (filters.status) params.append('status', filters.status);
    if (filters.sort) params.append('sort', filters.sort);
    window.open(`/api/users/export?${params}`, '_blank');
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
                    <div class="detail-label">Gender</div>
                    <div class="detail-value">${formatGender(user.gender)}</div>
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
            ${user.social_profile ? `
                <div class="detail-section">
                    <h4>Social Profile</h4>
                    <div class="user-detail-grid">
                        ${user.social_profile.instagram_url ? `
                            <div class="detail-item">
                                <div class="detail-label">Instagram</div>
                                <div class="detail-value"><a href="${user.social_profile.instagram_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.facebook_url ? `
                            <div class="detail-item">
                                <div class="detail-label">Facebook</div>
                                <div class="detail-value"><a href="${user.social_profile.facebook_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.twitter_url ? `
                            <div class="detail-item">
                                <div class="detail-label">Twitter/X</div>
                                <div class="detail-value"><a href="${user.social_profile.twitter_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.linkedin_url ? `
                            <div class="detail-item">
                                <div class="detail-label">LinkedIn</div>
                                <div class="detail-value"><a href="${user.social_profile.linkedin_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.vk_url ? `
                            <div class="detail-item">
                                <div class="detail-label">VK</div>
                                <div class="detail-value"><a href="${user.social_profile.vk_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.telegram_channel_url ? `
                            <div class="detail-item">
                                <div class="detail-label">Telegram Channel</div>
                                <div class="detail-value"><a href="${user.social_profile.telegram_channel_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.youtube_url ? `
                            <div class="detail-item">
                                <div class="detail-label">YouTube</div>
                                <div class="detail-value"><a href="${user.social_profile.youtube_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.tiktok_url ? `
                            <div class="detail-item">
                                <div class="detail-label">TikTok</div>
                                <div class="detail-value"><a href="${user.social_profile.tiktok_url}" target="_blank">Link</a></div>
                            </div>
                        ` : ''}
                        ${user.social_profile.interests && user.social_profile.interests.length > 0 ? `
                            <div class="detail-item" style="grid-column: span 2;">
                                <div class="detail-label">Interests</div>
                                <div class="detail-value">${user.social_profile.interests.join(', ')}</div>
                            </div>
                        ` : ''}
                        ${user.social_profile.bio_text ? `
                            <div class="detail-item" style="grid-column: span 2;">
                                <div class="detail-label">Bio</div>
                                <div class="detail-value">${escapeHtml(user.social_profile.bio_text).substring(0, 300)}${user.social_profile.bio_text.length > 300 ? '...' : ''}</div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
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
            <div class="detail-section user-actions">
                <h4>Admin Actions</h4>
                <div class="user-action-buttons">
                    ${user.is_blocked
                        ? `<button class="btn btn-success" onclick="unblockUser(${user.id})">✓ Unblock User</button>`
                        : `<button class="btn btn-danger" onclick="blockUser(${user.id})">🚫 Block User</button>`
                    }
                </div>
                ${user.is_blocked ? '<p class="blocked-warning">⚠️ This user is currently blocked and cannot interact with the bot.</p>' : ''}
            </div>
            ${!user.is_blocked ? `
            <div class="detail-section send-message-section">
                <h4>Send Direct Message</h4>
                <div class="send-message-form">
                    <textarea id="user-direct-message" class="textarea-input" rows="3" placeholder="Type your message to send via Telegram..."></textarea>
                    <div class="send-message-actions">
                        <span class="text-muted">Message will be sent directly to user's Telegram</span>
                        <button class="btn btn-primary" onclick="sendDirectMessage(${user.id})">
                            📤 Send Message
                        </button>
                    </div>
                </div>
            </div>
            ` : ''}
        `;
    } catch (error) {
        modalBody.innerHTML = `<p class="error-message">Error loading user details: ${error.message}</p>`;
    }
}

async function blockUser(userId) {
    if (!confirm('Are you sure you want to block this user? They will not be able to interact with the bot.')) {
        return;
    }

    try {
        const result = await api(`/users/${userId}/block`, { method: 'POST' });
        if (result.success) {
            alert('User blocked successfully');
            // Refresh the modal
            showUserDetail(userId);
            // Refresh users list
            loadUsers(usersOffset, document.getElementById('user-search').value);
        }
    } catch (error) {
        alert('Error blocking user: ' + error.message);
    }
}

async function unblockUser(userId) {
    if (!confirm('Are you sure you want to unblock this user?')) {
        return;
    }

    try {
        const result = await api(`/users/${userId}/unblock`, { method: 'POST' });
        if (result.success) {
            alert('User unblocked successfully');
            // Refresh the modal
            showUserDetail(userId);
            // Refresh users list
            loadUsers(usersOffset, document.getElementById('user-search').value);
        }
    } catch (error) {
        alert('Error unblocking user: ' + error.message);
    }
}

async function sendDirectMessage(userId) {
    const messageInput = document.getElementById('user-direct-message');
    const message = messageInput.value.trim();

    if (!message) {
        alert('Please enter a message');
        return;
    }

    if (!confirm('Are you sure you want to send this message to the user?')) {
        return;
    }

    try {
        const result = await api(`/users/${userId}/message`, {
            method: 'POST',
            body: JSON.stringify({ message })
        });

        if (result.success) {
            alert('Message sent successfully!');
            messageInput.value = '';
        }
    } catch (error) {
        alert('Error sending message: ' + error.message);
    }
}

// Make block/unblock/sendMessage functions globally accessible
window.blockUser = blockUser;
window.unblockUser = unblockUser;
window.sendDirectMessage = sendDirectMessage;

// Modal close - user modal
document.querySelector('#user-modal .modal-close').addEventListener('click', () => {
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
let logsOffset = 0;
const logsPageSize = 50;

async function loadLogsPage() {
    await Promise.all([
        loadLogsSources(),
        loadLogsStats(),
        loadLogs(0),
    ]);
}

async function loadLogsSources() {
    try {
        const { sources } = await api('/system/logs?limit=1');
        const select = document.getElementById('log-source-filter');
        if (select && sources) {
            select.innerHTML = '<option value="">All Sources</option>' +
                sources.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');
        }
    } catch (error) {
        console.error('Error loading log sources:', error);
    }
}

async function loadLogsStats() {
    try {
        // Get stats for last 24 hours
        const yesterday = new Date();
        yesterday.setDate(yesterday.getDate() - 1);
        const dateFrom = yesterday.toISOString().split('T')[0];

        const [errorsRes, warningsRes, infoRes, totalRes] = await Promise.all([
            api(`/system/logs?level=ERROR&date_from=${dateFrom}&limit=1`),
            api(`/system/logs?level=WARNING&date_from=${dateFrom}&limit=1`),
            api(`/system/logs?level=INFO&date_from=${dateFrom}&limit=1`),
            api('/system/logs?limit=1'),
        ]);

        document.getElementById('logs-stat-errors').textContent = errorsRes.total || 0;
        document.getElementById('logs-stat-warnings').textContent = warningsRes.total || 0;
        document.getElementById('logs-stat-info').textContent = infoRes.total || 0;
        document.getElementById('logs-stat-total').textContent = totalRes.total || 0;
    } catch (error) {
        console.error('Error loading logs stats:', error);
    }
}

async function loadLogs(offset = 0) {
    logsOffset = offset;
    const container = document.getElementById('logs-container');
    container.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const level = document.getElementById('log-level-filter').value;
        const source = document.getElementById('log-source-filter')?.value || '';
        const dateFrom = document.getElementById('log-date-from')?.value || '';
        const dateTo = document.getElementById('log-date-to')?.value || '';

        const params = new URLSearchParams({ limit: logsPageSize, offset });
        if (level) params.append('level', level);
        if (source) params.append('source', source);
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);

        const { logs, total, sources } = await api(`/system/logs?${params}`);

        // Update sources dropdown if available
        if (sources && sources.length > 0) {
            const select = document.getElementById('log-source-filter');
            if (select && select.options.length <= 1) {
                select.innerHTML = '<option value="">All Sources</option>' +
                    sources.map(s => `<option value="${escapeHtml(s)}">${escapeHtml(s)}</option>`).join('');
            }
        }

        if (logs.length === 0) {
            container.innerHTML = '<p class="loading" style="color: #94a3b8;">No logs found</p>';
        } else {
            container.innerHTML = logs.map(log => {
                const hasDetails = log.details && Object.keys(log.details || {}).length > 0;
                const detailsJson = hasDetails ? JSON.stringify(log.details, null, 2) : '';

                return `
                    <div class="log-entry ${hasDetails ? 'has-details' : ''}" onclick="toggleLogDetails(this)">
                        <div class="log-entry-header">
                            <span class="log-level ${log.level}">${log.level}</span>
                            ${log.source ? `<span class="log-source">${escapeHtml(log.source)}</span>` : ''}
                            <span class="log-message">${escapeHtml(log.message)}</span>
                            <span class="log-time">${formatDate(log.timestamp)}</span>
                            ${hasDetails ? '<span class="log-expand-icon">▶</span>' : ''}
                        </div>
                        ${hasDetails ? `
                            <div class="log-details">
                                <div class="log-details-label">Details:</div>
                                <pre>${escapeHtml(detailsJson)}</pre>
                            </div>
                        ` : ''}
                    </div>
                `;
            }).join('');
        }

        renderPagination('logs-pagination', total, offset, logsPageSize, loadLogs);
    } catch (error) {
        console.error('Error loading logs:', error);
        container.innerHTML = `<p class="loading" style="color: #f87171;">Error: ${error.message}</p>`;
    }
}

function toggleLogDetails(entry) {
    if (entry.classList.contains('has-details')) {
        entry.classList.toggle('expanded');
    }
}

// Make toggleLogDetails globally accessible
window.toggleLogDetails = toggleLogDetails;

document.getElementById('log-level-filter')?.addEventListener('change', () => loadLogs(0));
document.getElementById('log-source-filter')?.addEventListener('change', () => loadLogs(0));
document.getElementById('log-date-from')?.addEventListener('change', () => loadLogs(0));
document.getElementById('log-date-to')?.addEventListener('change', () => loadLogs(0));
document.getElementById('refresh-logs')?.addEventListener('click', () => {
    loadLogsStats();
    loadLogs(logsOffset);
});

// Notifications Page
let notificationsOffset = 0;
const notificationsPageSize = 50;

function getNotificationsFilters() {
    return {
        userId: document.getElementById('notifications-user-filter')?.value || '',
        status: document.getElementById('notifications-status-filter')?.value || '',
        dateFrom: document.getElementById('notifications-date-from')?.value || '',
        dateTo: document.getElementById('notifications-date-to')?.value || '',
    };
}

async function loadNotificationsUsers() {
    const select = document.getElementById('notifications-user-filter');
    if (!select) return;

    try {
        const { users } = await api('/users?limit=100');
        select.innerHTML = '<option value="">All Users</option>' +
            users.map(u => `<option value="${u.id}">${escapeHtml(u.username || u.first_name || 'User #' + u.telegram_id)}</option>`).join('');
    } catch (error) {
        console.error('Error loading users for filter:', error);
    }
}

async function loadNotifications(offset = 0) {
    notificationsOffset = offset;
    const tbody = document.querySelector('#notifications-table tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading">Loading...</td></tr>';

    try {
        const filters = getNotificationsFilters();
        const params = new URLSearchParams({ limit: notificationsPageSize, offset });

        if (filters.userId) params.append('user_id', filters.userId);
        if (filters.status) params.append('status', filters.status);
        if (filters.dateFrom) params.append('date_from', filters.dateFrom);
        if (filters.dateTo) params.append('date_to', filters.dateTo);

        const { notifications, total } = await api(`/system/notifications?${params}`);

        if (notifications.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading">No notifications found</td></tr>';
        } else {
            tbody.innerHTML = notifications.map(n => `
                <tr>
                    <td>${n.id}</td>
                    <td>${escapeHtml(n.username || n.first_name || `User #${n.user_id}`)}</td>
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

        renderPagination('notifications-pagination', total || notifications.length, offset, notificationsPageSize, loadNotifications);
    } catch (error) {
        console.error('Error loading notifications:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="loading">Error: ${error.message}</td></tr>`;
    }
}

document.getElementById('notifications-user-filter')?.addEventListener('change', () => loadNotifications(0));
document.getElementById('notifications-status-filter')?.addEventListener('change', () => loadNotifications(0));
document.getElementById('notifications-date-from')?.addEventListener('change', () => loadNotifications(0));
document.getElementById('notifications-date-to')?.addEventListener('change', () => loadNotifications(0));
document.getElementById('refresh-notifications')?.addEventListener('click', () => loadNotifications(notificationsOffset));

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
    const modalFooter = document.getElementById('feedback-modal-footer');

    modal.classList.add('active');

    // Check for existing response
    const existingResponseHtml = feedbackData.admin_response ? `
        <div class="feedback-existing-response">
            <h5>Previous Admin Response</h5>
            <p>${escapeHtml(feedbackData.admin_response)}</p>
            <small>Responded: ${feedbackData.admin_response_at ? formatDate(feedbackData.admin_response_at) : 'Unknown'}</small>
        </div>
    ` : '';

    modalBody.innerHTML = `
        <div class="feedback-detail">
            <div class="feedback-meta">
                <div class="feedback-meta-item">
                    <span class="feedback-meta-label">User</span>
                    <span class="feedback-meta-value">${feedbackData.username || feedbackData.first_name || `User #${feedbackData.user_id}`}</span>
                </div>
                <div class="feedback-meta-item">
                    <span class="feedback-meta-label">Telegram ID</span>
                    <span class="feedback-meta-value">${feedbackData.telegram_id || 'N/A'}</span>
                </div>
                <div class="feedback-meta-item">
                    <span class="feedback-meta-label">Category</span>
                    <span class="feedback-meta-value">${getCategoryLabel(feedbackData.category)}</span>
                </div>
                <div class="feedback-meta-item">
                    <span class="feedback-meta-label">Status</span>
                    <span class="feedback-meta-value"><span class="feedback-status ${feedbackData.status}">${getStatusLabel(feedbackData.status)}</span></span>
                </div>
                <div class="feedback-meta-item">
                    <span class="feedback-meta-label">Created</span>
                    <span class="feedback-meta-value">${formatDate(feedbackData.created_at)}</span>
                </div>
            </div>

            <div class="feedback-detail-section">
                <h4>Feedback Content</h4>
                <div class="feedback-content-box">${escapeHtml(feedbackData.content)}</div>
            </div>

            ${existingResponseHtml}

            <div class="feedback-detail-section">
                <h4>Update Status</h4>
                <div class="form-group" style="display: flex; gap: 12px; align-items: center;">
                    <select id="feedback-status-select" class="select-input" style="flex: 1;">
                        <option value="new" ${feedbackData.status === 'new' ? 'selected' : ''}>New</option>
                        <option value="reviewed" ${feedbackData.status === 'reviewed' ? 'selected' : ''}>Reviewed</option>
                        <option value="implemented" ${feedbackData.status === 'implemented' ? 'selected' : ''}>Implemented</option>
                        <option value="rejected" ${feedbackData.status === 'rejected' ? 'selected' : ''}>Rejected</option>
                    </select>
                    <button class="btn btn-secondary" onclick="updateFeedbackStatus(${feedbackId})">Update</button>
                </div>
                <div class="form-group">
                    <label>Admin Notes (internal)</label>
                    <textarea id="feedback-admin-notes" class="textarea-input" rows="2" placeholder="Internal notes (not sent to user)">${feedbackData.admin_notes || ''}</textarea>
                </div>
            </div>
        </div>
    `;

    // Response form in footer
    if (modalFooter) {
        modalFooter.innerHTML = `
            <div class="feedback-response-form">
                <h4 style="margin-bottom: 8px;">Respond to User</h4>
                <textarea id="feedback-response-text" placeholder="Type your response to the user... This will be sent to their Telegram.">${feedbackData.admin_response || ''}</textarea>
                <div class="feedback-response-actions">
                    <div class="feedback-response-options">
                        <label class="checkbox-label">
                            <input type="checkbox" id="feedback-send-to-user" checked>
                            Send to user via Telegram
                        </label>
                    </div>
                    <button class="btn btn-primary" onclick="sendFeedbackResponse(${feedbackId})">
                        Send Response
                    </button>
                </div>
            </div>
        `;
    }
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

async function sendFeedbackResponse(feedbackId) {
    const responseText = document.getElementById('feedback-response-text').value.trim();
    const sendToUser = document.getElementById('feedback-send-to-user').checked;

    if (!responseText) {
        alert('Please enter a response');
        return;
    }

    try {
        const result = await api(`/feedback/${feedbackId}/respond`, {
            method: 'POST',
            body: JSON.stringify({
                response: responseText,
                send_to_user: sendToUser,
            }),
        });

        if (result.success) {
            let alertMessage = 'Response saved successfully!';
            if (sendToUser) {
                if (result.message_sent) {
                    alertMessage = 'Response saved and message sent to user!';
                } else if (result.telegram_error) {
                    alertMessage = `Response saved but message failed to send: ${result.telegram_error}`;
                } else {
                    alertMessage = 'Response saved (message sending not available)';
                }
            }
            alert(alertMessage);

            // Close modal and refresh
            document.getElementById('feedback-modal').classList.remove('active');
            loadFeedback(feedbackOffset);
        }
    } catch (error) {
        console.error('Error sending feedback response:', error);
        alert('Error: ' + error.message);
    }
}

// Make showFeedbackDetail and sendFeedbackResponse globally accessible
window.showFeedbackDetail = showFeedbackDetail;

// =============================================================================
// EXPENSES PAGE
// =============================================================================

async function loadExpenses() {
    const days = document.getElementById('expenses-period')?.value || 30;

    try {
        const data = await api(`/expenses?days=${days}`);

        // Update totals
        document.getElementById('expense-total-requests').textContent =
            formatNumber(data.totals.requests);
        document.getElementById('expense-total-tokens').textContent =
            formatNumber(data.totals.tokens);
        document.getElementById('expense-total-cost').textContent =
            `$${data.totals.cost.toFixed(4)}`;

        // Render by model table
        const byModelContainer = document.getElementById('expenses-by-model');
        if (data.by_model.length === 0) {
            byModelContainer.innerHTML = '<p class="no-data">No API usage data</p>';
        } else {
            byModelContainer.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>Requests</th>
                            <th>Tokens</th>
                            <th>Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.by_model.map(m => `
                            <tr>
                                <td><code>${escapeHtml(m.model)}</code></td>
                                <td>${formatNumber(m.requests)}</td>
                                <td>${formatNumber(m.tokens)}</td>
                                <td>$${m.cost.toFixed(4)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

        // Render by operation table
        const byOperationContainer = document.getElementById('expenses-by-operation');
        if (data.by_operation.length === 0) {
            byOperationContainer.innerHTML = '<p class="no-data">No API usage data</p>';
        } else {
            byOperationContainer.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Operation</th>
                            <th>Requests</th>
                            <th>Tokens</th>
                            <th>Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.by_operation.map(o => `
                            <tr>
                                <td>${escapeHtml(o.operation)}</td>
                                <td>${formatNumber(o.requests)}</td>
                                <td>${formatNumber(o.tokens)}</td>
                                <td>$${o.cost.toFixed(4)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

        // Render recent calls table
        const recentContainer = document.getElementById('expenses-recent');
        if (data.recent.length === 0) {
            recentContainer.innerHTML = '<p class="no-data">No recent API calls</p>';
        } else {
            recentContainer.innerHTML = `
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Time</th>
                            <th>Model</th>
                            <th>Operation</th>
                            <th>Tokens</th>
                            <th>Cost</th>
                            <th>Duration</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.recent.map(r => `
                            <tr>
                                <td>${formatRelativeTime(r.created_at)}</td>
                                <td><code>${escapeHtml(r.model)}</code></td>
                                <td>${escapeHtml(r.operation_type)}</td>
                                <td>${formatNumber(r.total_tokens)}</td>
                                <td>$${r.cost_usd.toFixed(6)}</td>
                                <td>${r.duration_ms ? r.duration_ms + 'ms' : '-'}</td>
                                <td>
                                    <span class="status-badge ${r.success ? 'enabled' : 'disabled'}">
                                        ${r.success ? 'OK' : 'Error'}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }

    } catch (error) {
        console.error('Error loading expenses:', error);
        document.getElementById('expenses-by-model').innerHTML =
            '<p class="error">Error loading data</p>';
        document.getElementById('expenses-by-operation').innerHTML =
            '<p class="error">Error loading data</p>';
        document.getElementById('expenses-recent').innerHTML =
            '<p class="error">Error loading data</p>';
    }
}

// Expenses event listeners
document.getElementById('expenses-period')?.addEventListener('change', () => loadExpenses());
document.getElementById('refresh-expenses')?.addEventListener('click', () => loadExpenses());
window.sendFeedbackResponse = sendFeedbackResponse;
window.updateFeedbackStatus = updateFeedbackStatus;

// Moments Page
let momentsOffset = 0;
let selectedTopic = null;

async function loadMomentsPage() {
    await Promise.all([
        loadMomentsStats(),
        loadMomentsUsers(),
        loadMoments(0),
    ]);
}

async function loadMomentsStats() {
    try {
        const stats = await api('/moments/stats');

        // Update stats cards
        document.getElementById('moments-stat-total').textContent = stats.total_moments;
        document.getElementById('moments-stat-week').textContent = stats.moments_week;
        document.getElementById('moments-stat-mood').textContent = stats.avg_mood || '-';
        document.getElementById('moments-stat-users').textContent = stats.unique_users;

        // Render topics cloud
        renderTopicsCloud(stats.topics_cloud);
    } catch (error) {
        console.error('Error loading moments stats:', error);
    }
}

function renderTopicsCloud(topics) {
    const container = document.getElementById('topics-cloud');

    if (!topics || topics.length === 0) {
        container.innerHTML = '<p class="loading">No topics found yet</p>';
        return;
    }

    // Calculate size classes based on frequency
    const maxCount = Math.max(...topics.map(t => t.count));
    const minCount = Math.min(...topics.map(t => t.count));
    const range = maxCount - minCount || 1;

    container.innerHTML = topics.map(topic => {
        const normalized = (topic.count - minCount) / range;
        let sizeClass = 'size-1';
        if (normalized > 0.8) sizeClass = 'size-5';
        else if (normalized > 0.6) sizeClass = 'size-4';
        else if (normalized > 0.4) sizeClass = 'size-3';
        else if (normalized > 0.2) sizeClass = 'size-2';

        const isSelected = selectedTopic === topic.topic;

        return `
            <span class="topic-tag ${sizeClass} ${isSelected ? 'selected' : ''}"
                  onclick="filterByTopic('${escapeHtml(topic.topic)}')"
                  title="${topic.count} moments">
                ${escapeHtml(topic.topic)} (${topic.count})
            </span>
        `;
    }).join('');
}

function filterByTopic(topic) {
    if (selectedTopic === topic) {
        selectedTopic = null;
    } else {
        selectedTopic = topic;
    }
    loadMoments(0);
}

async function loadMomentsUsers() {
    const select = document.getElementById('moments-user-filter');
    try {
        const { users } = await api('/users?limit=100');
        select.innerHTML = '<option value="">All Users</option>' +
            users.map(u => `<option value="${u.id}">${escapeHtml(u.username || u.first_name || 'User #' + u.telegram_id)}</option>`).join('');
    } catch (error) {
        console.error('Error loading users for filter:', error);
    }
}

async function loadMoments(offset = 0) {
    momentsOffset = offset;
    const tbody = document.querySelector('#moments-table tbody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">Loading...</td></tr>';

    try {
        const userId = document.getElementById('moments-user-filter').value;
        const dateFrom = document.getElementById('moments-date-from').value;
        const dateTo = document.getElementById('moments-date-to').value;
        const moodFilter = document.getElementById('moments-mood-filter').value;

        const params = new URLSearchParams({ limit: pageSize, offset });

        if (userId) params.append('user_id', userId);
        if (dateFrom) params.append('date_from', dateFrom);
        if (dateTo) params.append('date_to', dateTo);

        if (moodFilter) {
            const [min, max] = moodFilter.split('-');
            params.append('mood_min', min);
            params.append('mood_max', max);
        }

        if (selectedTopic) {
            params.append('topic', selectedTopic);
        }

        const { moments, total } = await api(`/moments?${params}`);

        if (moments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No moments found</td></tr>';
        } else {
            tbody.innerHTML = moments.map(m => {
                const moodBadge = getMoodBadge(m.mood_score);
                const sourceBadge = getSourceBadge(m.source_type);
                const topicsHtml = (m.topics || []).slice(0, 3).map(t =>
                    `<span class="topic-mini">${escapeHtml(t)}</span>`
                ).join('');

                return `
                    <tr>
                        <td>${m.id}</td>
                        <td>${escapeHtml(m.username || m.first_name || 'User #' + m.user_id)}</td>
                        <td>${escapeHtml((m.content || '').substring(0, 100))}${m.content?.length > 100 ? '...' : ''}</td>
                        <td>${sourceBadge}</td>
                        <td>${moodBadge}</td>
                        <td><div class="topics-list">${topicsHtml}</div></td>
                        <td>${formatRelativeTime(m.created_at)}</td>
                    </tr>
                `;
            }).join('');
        }

        renderPagination('moments-pagination', total, offset, pageSize, loadMoments);
    } catch (error) {
        console.error('Error loading moments:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="loading">Error: ${error.message}</td></tr>`;
    }
}

function getMoodBadge(score) {
    if (score === null || score === undefined) return '<span class="mood-badge">-</span>';

    let className = 'neutral';
    let label = 'Neutral';

    if (score >= 0.8) { className = 'very-positive'; label = 'Very Positive'; }
    else if (score >= 0.6) { className = 'positive'; label = 'Positive'; }
    else if (score >= 0.4) { className = 'neutral'; label = 'Neutral'; }
    else { className = 'negative'; label = 'Negative'; }

    return `<span class="mood-badge ${className}" title="${score.toFixed(2)}">${label}</span>`;
}

function getSourceBadge(source) {
    if (!source) return '<span class="source-badge">-</span>';
    return `<span class="source-badge ${source}">${source}</span>`;
}

function exportMoments() {
    const userId = document.getElementById('moments-user-filter').value;
    const dateFrom = document.getElementById('moments-date-from').value;
    const dateTo = document.getElementById('moments-date-to').value;

    const params = new URLSearchParams();
    if (userId) params.append('user_id', userId);
    if (dateFrom) params.append('date_from', dateFrom);
    if (dateTo) params.append('date_to', dateTo);

    window.open(`/api/moments/export?${params}`, '_blank');
}

// Moments event listeners
document.getElementById('moments-user-filter')?.addEventListener('change', () => loadMoments(0));
document.getElementById('moments-date-from')?.addEventListener('change', () => loadMoments(0));
document.getElementById('moments-date-to')?.addEventListener('change', () => loadMoments(0));
document.getElementById('moments-mood-filter')?.addEventListener('change', () => loadMoments(0));
document.getElementById('moments-export-btn')?.addEventListener('click', exportMoments);
document.getElementById('refresh-moments')?.addEventListener('click', () => {
    loadMomentsStats();
    loadMoments(momentsOffset);
});

// Make filterByTopic globally accessible
window.filterByTopic = filterByTopic;

// Knowledge Base Page
let knowledgeOffset = 0;

async function loadKnowledgePage() {
    await Promise.all([
        loadKnowledgeStats(),
        loadKnowledgeItems(0),
    ]);
}

async function loadKnowledgeStats() {
    try {
        const stats = await api('/knowledge/stats');

        document.getElementById('kb-stat-total').textContent = stats.total_items;
        document.getElementById('kb-stat-indexed').textContent = stats.indexed;
        document.getElementById('kb-stat-pending').textContent = stats.pending;
        document.getElementById('kb-stat-chunks').textContent = stats.total_chunks;
    } catch (error) {
        console.error('Error loading knowledge stats:', error);
    }
}

async function loadKnowledgeItems(offset = 0) {
    knowledgeOffset = offset;
    const tbody = document.querySelector('#knowledge-table tbody');
    tbody.innerHTML = '<tr><td colspan="9" class="loading">Loading...</td></tr>';

    try {
        const status = document.getElementById('kb-status-filter').value;
        const params = new URLSearchParams({ limit: pageSize, offset });
        if (status) params.append('status', status);

        const { items, total } = await api(`/knowledge?${params}`);

        if (items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="loading">No knowledge base items found</td></tr>';
        } else {
            tbody.innerHTML = items.map(item => {
                const statusBadge = getIndexingStatusBadge(item.indexing_status);
                const typeBadge = getFileTypeBadge(item.file_type);

                return `
                    <tr>
                        <td>${item.id}</td>
                        <td>${escapeHtml(item.title)}</td>
                        <td>${typeBadge}</td>
                        <td>${escapeHtml(item.category || '-')}</td>
                        <td>${statusBadge}</td>
                        <td>${item.chunks_count}</td>
                        <td>${item.usage_count}</td>
                        <td>${formatRelativeTime(item.created_at)}</td>
                        <td class="actions">
                            <button class="btn btn-secondary btn-small" onclick="reindexKnowledge(${item.id})">Reindex</button>
                            <button class="btn btn-secondary btn-small" onclick="deleteKnowledge(${item.id}, '${escapeHtml(item.title)}')">Delete</button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        renderPagination('knowledge-pagination', total, offset, pageSize, loadKnowledgeItems);
    } catch (error) {
        console.error('Error loading knowledge items:', error);
        tbody.innerHTML = `<tr><td colspan="9" class="loading">Error: ${error.message}</td></tr>`;
    }
}

function getIndexingStatusBadge(status) {
    const labels = {
        'indexed': 'Indexed',
        'pending': 'Pending',
        'error': 'Error',
    };
    return `<span class="indexing-status ${status}">${labels[status] || status}</span>`;
}

function getFileTypeBadge(type) {
    return `<span class="file-type-badge ${type}">${type}</span>`;
}

async function uploadKnowledge(formData) {
    const statusDiv = document.getElementById('kb-upload-status');
    statusDiv.textContent = 'Uploading...';
    statusDiv.className = 'upload-status loading';

    try {
        const response = await fetch('/api/knowledge/upload', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || 'Upload failed');
        }

        statusDiv.textContent = result.message;
        statusDiv.className = 'upload-status success';

        // Clear form
        document.getElementById('kb-upload-form').reset();

        // Reload list and stats
        await Promise.all([loadKnowledgeStats(), loadKnowledgeItems(0)]);
    } catch (error) {
        statusDiv.textContent = `Error: ${error.message}`;
        statusDiv.className = 'upload-status error';
    }
}

async function reindexKnowledge(itemId) {
    if (!confirm('Are you sure you want to reindex this item?')) return;

    try {
        const result = await api(`/knowledge/${itemId}/reindex`, { method: 'POST' });
        alert(result.message);
        await Promise.all([loadKnowledgeStats(), loadKnowledgeItems(knowledgeOffset)]);
    } catch (error) {
        alert('Error reindexing: ' + error.message);
    }
}

async function deleteKnowledge(itemId, title) {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) return;

    try {
        const result = await api(`/knowledge/${itemId}/delete`, { method: 'POST' });
        alert(result.message);
        await Promise.all([loadKnowledgeStats(), loadKnowledgeItems(knowledgeOffset)]);
    } catch (error) {
        alert('Error deleting: ' + error.message);
    }
}

// Knowledge Base event listeners
document.getElementById('kb-upload-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    await uploadKnowledge(formData);
});

document.getElementById('kb-status-filter')?.addEventListener('change', () => loadKnowledgeItems(0));
document.getElementById('refresh-knowledge')?.addEventListener('click', () => {
    loadKnowledgeStats();
    loadKnowledgeItems(knowledgeOffset);
});

// Make knowledge functions globally accessible
window.reindexKnowledge = reindexKnowledge;
window.deleteKnowledge = deleteKnowledge;

// Templates Page
let templatesOffset = 0;
let editingTemplateId = null;

async function loadTemplatesPage() {
    await Promise.all([
        loadTemplateCategories(),
        loadTemplates(0),
    ]);
}

async function loadTemplateCategories() {
    const select = document.getElementById('templates-category-filter');
    try {
        const { categories } = await api('/templates/categories');
        const currentOptions = '<option value="">All Categories</option>';
        select.innerHTML = currentOptions + categories.map(c =>
            `<option value="${escapeHtml(c.name)}">${escapeHtml(c.name)} (${c.count})</option>`
        ).join('');
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function loadTemplates(offset = 0) {
    templatesOffset = offset;
    const tbody = document.querySelector('#templates-table tbody');
    tbody.innerHTML = '<tr><td colspan="7" class="loading">Loading...</td></tr>';

    try {
        const language = document.getElementById('templates-language-filter').value;
        const category = document.getElementById('templates-category-filter').value;

        const params = new URLSearchParams({ limit: pageSize, offset });
        if (language) params.append('language', language);
        if (category) params.append('category', category);

        const { templates, total } = await api(`/templates?${params}`);

        if (templates.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="loading">No templates found</td></tr>';
        } else {
            tbody.innerHTML = templates.map(t => {
                const statusClass = t.is_active ? 'active' : 'inactive';
                const statusText = t.is_active ? 'Active' : 'Inactive';
                const formalText = t.formal ? 'Вы' : 'Ты';
                const formalClass = t.formal ? 'formal' : 'informal';

                return `
                    <tr>
                        <td>${t.id}</td>
                        <td>${escapeHtml(t.template_text.substring(0, 80))}${t.template_text.length > 80 ? '...' : ''}</td>
                        <td><span class="language-badge">${t.language_code}</span></td>
                        <td><span class="formal-badge ${formalClass}">${formalText}</span></td>
                        <td><span class="category-badge">${escapeHtml(t.category || 'general')}</span></td>
                        <td><span class="template-status ${statusClass}">${statusText}</span></td>
                        <td class="actions">
                            <button class="btn btn-secondary btn-small" onclick="editTemplate(${t.id})">Edit</button>
                            <button class="btn btn-secondary btn-small" onclick="deleteTemplate(${t.id})">Delete</button>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        renderPagination('templates-pagination', total, offset, pageSize, loadTemplates);
    } catch (error) {
        console.error('Error loading templates:', error);
        tbody.innerHTML = `<tr><td colspan="7" class="loading">Error: ${error.message}</td></tr>`;
    }
}

async function createTemplate(data) {
    try {
        await api('/templates', {
            method: 'POST',
            body: JSON.stringify(data),
        });
        resetTemplateForm();
        await Promise.all([loadTemplateCategories(), loadTemplates(0)]);
        alert('Template created successfully');
    } catch (error) {
        alert('Error creating template: ' + error.message);
    }
}

async function updateTemplate(id, data) {
    try {
        await api(`/templates/${id}/update`, {
            method: 'POST',
            body: JSON.stringify(data),
        });
        resetTemplateForm();
        await Promise.all([loadTemplateCategories(), loadTemplates(templatesOffset)]);
        alert('Template updated successfully');
    } catch (error) {
        alert('Error updating template: ' + error.message);
    }
}

async function editTemplate(id) {
    try {
        const template = await api(`/templates/${id}`);

        editingTemplateId = id;
        document.getElementById('template-edit-id').value = id;
        document.getElementById('template-text').value = template.template_text;
        document.getElementById('template-language').value = template.language_code;
        document.getElementById('template-formal').checked = template.formal;
        document.getElementById('template-category').value = template.category || 'general';
        document.getElementById('template-active').checked = template.is_active;

        document.getElementById('template-form-title').textContent = 'Edit Template #' + id;
        document.getElementById('template-submit-btn').textContent = 'Update';
        document.getElementById('template-cancel-btn').style.display = 'inline-block';

        updateTemplatePreview();

        // Scroll to form
        document.querySelector('.template-form-section').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        alert('Error loading template: ' + error.message);
    }
}

async function deleteTemplate(id) {
    if (!confirm('Are you sure you want to delete this template?')) return;

    try {
        await api(`/templates/${id}/delete`, { method: 'POST' });
        await Promise.all([loadTemplateCategories(), loadTemplates(templatesOffset)]);
        alert('Template deleted successfully');
    } catch (error) {
        alert('Error deleting template: ' + error.message);
    }
}

function resetTemplateForm() {
    editingTemplateId = null;
    document.getElementById('template-edit-id').value = '';
    document.getElementById('template-form').reset();
    document.getElementById('template-category').value = 'general';
    document.getElementById('template-formal').checked = false;
    document.getElementById('template-active').checked = true;

    document.getElementById('template-form-title').textContent = 'Create New Template';
    document.getElementById('template-submit-btn').textContent = 'Create';
    document.getElementById('template-cancel-btn').style.display = 'none';

    document.getElementById('template-preview-text').textContent = 'Enter text to see preview...';
}

function updateTemplatePreview() {
    const text = document.getElementById('template-text').value;
    const previewBox = document.getElementById('template-preview-text');

    if (!text) {
        previewBox.textContent = 'Enter text to see preview...';
        return;
    }

    // Replace {name} with sample name
    const preview = text.replace(/{name}/g, 'User');
    previewBox.textContent = preview;
}

// Templates event listeners
let isSubmittingTemplate = false;

document.getElementById('template-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Prevent double-submit
    if (isSubmittingTemplate) {
        return;
    }

    const submitBtn = document.getElementById('template-submit-btn');
    const originalText = submitBtn.textContent;

    try {
        isSubmittingTemplate = true;
        submitBtn.disabled = true;
        submitBtn.textContent = 'Saving...';

        const data = {
            template_text: document.getElementById('template-text').value,
            language_code: document.getElementById('template-language').value,
            formal: document.getElementById('template-formal').checked,
            category: document.getElementById('template-category').value || 'general',
            is_active: document.getElementById('template-active').checked,
        };

        if (editingTemplateId) {
            await updateTemplate(editingTemplateId, data);
        } else {
            await createTemplate(data);
        }
    } finally {
        isSubmittingTemplate = false;
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
});

document.getElementById('template-cancel-btn')?.addEventListener('click', resetTemplateForm);

document.getElementById('template-text')?.addEventListener('input', updateTemplatePreview);

document.getElementById('templates-language-filter')?.addEventListener('change', () => loadTemplates(0));
document.getElementById('templates-category-filter')?.addEventListener('change', () => loadTemplates(0));
document.getElementById('refresh-templates')?.addEventListener('click', () => {
    loadTemplateCategories();
    loadTemplates(templatesOffset);
});

// Make template functions globally accessible
window.editTemplate = editTemplate;
window.deleteTemplate = deleteTemplate;

// Dialogs Page
let currentDialogUserId = null;
// NOTE: Inline event handlers and some older browser scoping rules don't reliably see
// top-level `let/const` as `window.*`. Keep this state on `window` to avoid
// "Cannot access ... before initialization" / scope issues.
var allDialogUsers = window.allDialogUsers || [];
window.allDialogUsers = allDialogUsers;

async function loadDialogsPage() {
    await loadDialogUsers();
}

async function loadDialogUsers(search = '') {
    const container = document.getElementById('dialogs-users-list');
    container.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const { users } = await api('/dialogs/users');
        allDialogUsers = users;
        window.allDialogUsers = allDialogUsers;

        renderDialogUsersList(search);
    } catch (error) {
        console.error('Error loading dialog users:', error);
        container.innerHTML = `<p class="loading">Error: ${error.message}</p>`;
    }
}

function renderDialogUsersList(search = '') {
    const container = document.getElementById('dialogs-users-list');
    let filteredUsers = allDialogUsers;

    if (search) {
        const searchLower = search.toLowerCase();
        filteredUsers = allDialogUsers.filter(u =>
            (u.username && u.username.toLowerCase().includes(searchLower)) ||
            (u.first_name && u.first_name.toLowerCase().includes(searchLower)) ||
            u.telegram_id.toString().includes(searchLower)
        );
    }

    if (filteredUsers.length === 0) {
        container.innerHTML = '<p class="loading">No users with dialogs found</p>';
        return;
    }

    container.innerHTML = filteredUsers.map(user => {
        const displayName = escapeHtml(user.username || user.first_name || ('User #' + user.telegram_id));
        const userId = Number(user.id);
        const preview = escapeHtml(user.last_message_content || '');
        const lastAt = user.last_message_at || user.last_message || null;
        const timeText = lastAt ? formatRelativeTime(lastAt) : '-';

        return `
            <div class="dialog-user-item ${currentDialogUserId === userId ? 'active' : ''}"
                 onclick="selectDialogUser(${userId}, '${displayName}', this)">
                <div class="dialog-user-name">${displayName}</div>
                <div class="dialog-user-preview">${preview || '-'}</div>
                <div class="dialog-user-time">${user.message_count} messages • ${timeText}</div>
            </div>
        `;
    }).join('');
}

async function selectDialogUser(userId, userName, el) {
    const id = Number(userId);
    if (!Number.isFinite(id)) {
        const container = document.getElementById('dialogs-messages');
        container.innerHTML = '<p class="loading">Error: Invalid user id</p>';
        return;
    }

    currentDialogUserId = id;

    // Update user list UI
    document.querySelectorAll('.dialog-user-item').forEach(item => {
        item.classList.remove('active');
    });
    if (el) el.classList.add('active');

    // Update header
    document.getElementById('dialogs-header').innerHTML = `
        <span class="dialogs-user-name">${escapeHtml(userName)}</span>
    `;

    // Load messages for this user
    await loadUserDialog(id);
}

async function loadUserDialog(userId) {
    const container = document.getElementById('dialogs-messages');
    container.innerHTML = '<p class="loading">Loading messages...</p>';

    try {
        const messageType = document.getElementById('dialog-message-type-filter').value;
        const search = document.getElementById('dialog-text-search').value;

        const params = new URLSearchParams();
        if (messageType) params.append('message_type', messageType);
        if (search) params.append('search', search);

        const { messages, user } = await api(`/dialogs/user/${userId}?${params}`);

        if (messages.length === 0) {
            container.innerHTML = '<p class="loading">No messages found</p>';
            return;
        }

        // Render messages in messenger style (oldest first for natural reading)
        const sortedMessages = [...messages].reverse();

        container.innerHTML = sortedMessages.map(msg => {
            const isUserMessage = msg.message_type === 'user_response' || msg.message_type === 'free_dialog';
            const messageClass = isUserMessage ? 'user-message' : 'bot-message';

            return `
                <div class="dialog-message ${messageClass} ${msg.message_type}">
                    <div class="dialog-message-type">${msg.message_type.replace(/_/g, ' ')}</div>
                    <div class="dialog-message-content">${escapeHtml(msg.content)}</div>
                    <div class="dialog-message-time">${formatDate(msg.created_at)}</div>
                </div>
            `;
        }).join('');

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Error loading user dialog:', error);
        container.innerHTML = `<p class="loading">Error: ${error.message}</p>`;
    }
}

// Dialog user search
document.getElementById('dialog-user-search')?.addEventListener('input', debounce((e) => {
    renderDialogUsersList(e.target.value);
}, 300));

// Dialog filters
document.getElementById('dialog-message-type-filter')?.addEventListener('change', () => {
    if (currentDialogUserId) loadUserDialog(currentDialogUserId);
});

document.getElementById('dialog-text-search')?.addEventListener('input', debounce((e) => {
    if (currentDialogUserId) loadUserDialog(currentDialogUserId);
}, 300));

// Export dialogs buttons
document.getElementById('export-dialogs-csv')?.addEventListener('click', () => {
    const params = new URLSearchParams({ format: 'csv' });
    if (currentDialogUserId) params.append('user_id', currentDialogUserId);
    const messageType = document.getElementById('dialog-message-type-filter')?.value;
    if (messageType) params.append('message_type', messageType);
    window.open(`/api/dialogs/export?${params}`, '_blank');
});

document.getElementById('export-dialogs-json')?.addEventListener('click', () => {
    const params = new URLSearchParams({ format: 'json' });
    if (currentDialogUserId) params.append('user_id', currentDialogUserId);
    const messageType = document.getElementById('dialog-message-type-filter')?.value;
    if (messageType) params.append('message_type', messageType);
    window.open(`/api/dialogs/export?${params}`, '_blank');
});

// Make selectDialogUser globally accessible
window.selectDialogUser = selectDialogUser;

// Pagination helper - stores callbacks globally to avoid inline function code
// Must be on window because inline `onclick="paginationCallbacks[...]()"` resolves via `window`.
var paginationCallbacks = window.paginationCallbacks || {};
window.paginationCallbacks = paginationCallbacks;

function renderPagination(containerId, total, offset, limit, loadFn) {
    const container = document.getElementById(containerId);
    const totalPages = Math.ceil(total / limit);
    const currentPage = Math.floor(offset / limit) + 1;

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    // Store the callback globally
    paginationCallbacks[containerId] = loadFn;
    window.paginationCallbacks = paginationCallbacks;

    let html = '';

    // Previous button
    const prevOffset = (currentPage - 2) * limit;
    html += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="window.paginationCallbacks['${containerId}'](${prevOffset})">Prev</button>`;

    // Page numbers
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
        const pageOffset = (i - 1) * limit;
        html += `<button class="${i === currentPage ? 'active' : ''}" onclick="window.paginationCallbacks['${containerId}'](${pageOffset})">${i}</button>`;
    }

    // Next button
    const nextOffset = currentPage * limit;
    html += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="window.paginationCallbacks['${containerId}'](${nextOffset})">Next</button>`;

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

// Analytics Page
async function loadAnalyticsPage() {
    await Promise.all([
        loadAnalyticsOverview(),
        loadFunnelChart(),
        loadRetentionTable(),
        loadUsersPerDayChart(),
        loadHeatmap(),
        loadLanguagesChart(),
    ]);
}

async function loadAnalyticsOverview() {
    try {
        const stats = await api('/analytics/overview');

        document.getElementById('analytics-total-users').textContent = stats.total_users || 0;
        document.getElementById('analytics-onboarded').textContent = stats.onboarded_users || 0;
        document.getElementById('analytics-active-users').textContent = stats.active_users_7d || 0;

        // Calculate retention rate
        const retentionRate = stats.total_users > 0
            ? Math.round((stats.active_users_7d / stats.total_users) * 100)
            : 0;
        document.getElementById('analytics-retention-rate').textContent = retentionRate + '%';
    } catch (error) {
        console.error('Error loading analytics overview:', error);
    }
}

async function loadFunnelChart() {
    const container = document.getElementById('funnel-chart');
    container.innerHTML = '<p class="loading">Loading funnel data...</p>';

    try {
        const data = await api('/analytics/funnel');
        const stages = data.stages || [];

        if (stages.length === 0) {
            container.innerHTML = '<p class="loading">No funnel data available</p>';
            return;
        }

        const maxCount = stages[0]?.count || 1;

        let html = '';
        for (let i = 0; i < stages.length; i++) {
            const stage = stages[i];
            const width = Math.max(10, (stage.count / maxCount) * 100);
            const dropRate = i > 0 && stages[i - 1].count > 0
                ? Math.round((1 - stage.count / stages[i - 1].count) * 100)
                : 0;

            html += `
                <div class="funnel-stage">
                    <div class="funnel-stage-info">
                        <div class="funnel-stage-name">${escapeHtml(stage.name)}</div>
                        <div class="funnel-stage-count">${stage.count} users (${stage.percentage}%)</div>
                    </div>
                    <div class="funnel-bar-container">
                        <div class="funnel-bar" style="width: ${width}%;">
                            <span class="funnel-bar-label">${stage.count}</span>
                        </div>
                    </div>
                </div>
            `;

            if (i < stages.length - 1 && dropRate > 0) {
                html += `<div class="funnel-drop-indicator">▼ ${dropRate}% drop-off</div>`;
            }
        }

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading funnel chart:', error);
        container.innerHTML = `<p class="loading">Error: ${error.message}</p>`;
    }
}

async function loadRetentionTable() {
    const tbody = document.querySelector('#retention-table tbody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading...</td></tr>';

    try {
        const data = await api('/analytics/retention');
        const cohorts = data.cohorts || [];

        if (cohorts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No retention data available</td></tr>';
            return;
        }

        tbody.innerHTML = cohorts.map(cohort => {
            const weeks = cohort.weeks || [];

            return `
                <tr>
                    <td class="retention-cohort">${escapeHtml(cohort.cohort_week)}</td>
                    <td class="retention-users">${cohort.users}</td>
                    ${weeks.map(week => {
                        const cellClass = getRetentionClass(week.retention);
                        return `<td><span class="retention-cell ${cellClass}">${week.retention}%</span></td>`;
                    }).join('')}
                    ${Array(4 - weeks.length).fill('<td>-</td>').join('')}
                </tr>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading retention table:', error);
        tbody.innerHTML = `<tr><td colspan="6" class="loading">Error: ${error.message}</td></tr>`;
    }
}

function getRetentionClass(retention) {
    if (retention >= 50) return 'high';
    if (retention >= 25) return 'medium';
    return 'low';
}

async function loadHeatmap() {
    const container = document.getElementById('heatmap-grid');
    container.innerHTML = '<p class="loading">Loading heatmap...</p>';

    try {
        const data = await api('/analytics/heatmap');
        const matrix = data.matrix || [];

        if (matrix.length === 0) {
            container.innerHTML = '<p class="loading">No activity data available</p>';
            return;
        }

        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

        // Find max value for normalization
        let maxVal = 0;
        matrix.forEach(row => {
            row.forEach(val => {
                if (val > maxVal) maxVal = val;
            });
        });

        let html = '';

        // Header row with hour labels
        html += '<div class="heatmap-header"></div>'; // Empty corner
        for (let h = 0; h < 24; h++) {
            html += `<div class="heatmap-header">${h}</div>`;
        }

        // Data rows
        for (let d = 0; d < 7; d++) {
            html += `<div class="heatmap-row-label">${days[d]}</div>`;

            for (let h = 0; h < 24; h++) {
                const value = matrix[d]?.[h] || 0;
                const level = getHeatmapLevel(value, maxVal);
                html += `<div class="heatmap-cell level-${level}" title="${days[d]} ${h}:00 - ${value} activities"></div>`;
            }
        }

        container.innerHTML = html;

        // Add legend
        const legendHtml = `
            <div class="heatmap-legend">
                <span>Less</span>
                <div class="heatmap-legend-scale">
                    <div class="heatmap-legend-cell level-0"></div>
                    <div class="heatmap-legend-cell level-1"></div>
                    <div class="heatmap-legend-cell level-2"></div>
                    <div class="heatmap-legend-cell level-3"></div>
                    <div class="heatmap-legend-cell level-4"></div>
                    <div class="heatmap-legend-cell level-5"></div>
                </div>
                <span>More</span>
            </div>
        `;
        container.insertAdjacentHTML('afterend', legendHtml);
    } catch (error) {
        console.error('Error loading heatmap:', error);
        container.innerHTML = `<p class="loading">Error: ${error.message}</p>`;
    }
}

function getHeatmapLevel(value, maxVal) {
    if (value === 0) return 0;
    if (maxVal === 0) return 0;

    const normalized = value / maxVal;
    if (normalized > 0.8) return 5;
    if (normalized > 0.6) return 4;
    if (normalized > 0.4) return 3;
    if (normalized > 0.2) return 2;
    return 1;
}

async function loadLanguagesChart() {
    const container = document.getElementById('languages-chart');
    container.innerHTML = '<p class="loading">Loading languages...</p>';

    try {
        const data = await api('/analytics/languages');
        const languages = data.languages || [];

        if (languages.length === 0) {
            container.innerHTML = '<p class="loading">No language data available</p>';
            return;
        }

        const total = languages.reduce((sum, l) => sum + l.count, 0);
        const maxCount = languages[0]?.count || 1;

        const langNames = {
            'ru': 'Russian',
            'en': 'English',
            'uk': 'Ukrainian',
        };

        container.innerHTML = languages.map(lang => {
            const name = langNames[lang.language_code] || lang.language_code || 'Other';
            const percent = total > 0 ? Math.round((lang.count / total) * 100) : 0;
            const barWidth = (lang.count / maxCount) * 100;
            const langClass = ['ru', 'en', 'uk'].includes(lang.language_code) ? `lang-${lang.language_code}` : 'lang-other';

            return `
                <div class="language-item">
                    <div class="language-label">${escapeHtml(name)}</div>
                    <div class="language-bar-container">
                        <div class="language-bar ${langClass}" style="width: ${barWidth}%;"></div>
                    </div>
                    <div class="language-percent">${percent}%</div>
                    <div class="language-count">${lang.count} users</div>
                </div>
            `;
        }).join('');
    } catch (error) {
        console.error('Error loading languages chart:', error);
        container.innerHTML = `<p class="loading">Error: ${error.message}</p>`;
    }
}

// Users per day chart
async function loadUsersPerDayChart(days = null) {
    const container = document.getElementById('users-chart');
    container.innerHTML = '<p class="loading">Loading chart...</p>';

    try {
        // Get period from dropdown if not specified
        if (!days) {
            const select = document.getElementById('users-chart-period');
            days = parseInt(select?.value) || 30;
        }

        const data = await api(`/analytics/users-per-day?days=${days}`);
        const chartData = data.data || [];

        if (chartData.length === 0) {
            container.innerHTML = '<p class="loading">No registration data available</p>';
            return;
        }

        // Find max value for scaling
        const maxCount = Math.max(...chartData.map(d => d.count), 1);
        const total = chartData.reduce((sum, d) => sum + d.count, 0);

        // Create bar chart
        let html = '<div class="users-chart-bars">';

        chartData.forEach((item, index) => {
            const barHeight = Math.max(5, (item.count / maxCount) * 100);
            const dateObj = new Date(item.date);
            const dayLabel = dateObj.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' });
            const fullDate = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

            html += `
                <div class="users-chart-bar-container" title="${fullDate}: ${item.count} user${item.count !== 1 ? 's' : ''}">
                    <div class="users-chart-bar" style="height: ${barHeight}%;">
                        ${item.count > 0 ? `<span class="users-chart-bar-value">${item.count}</span>` : ''}
                    </div>
                    <div class="users-chart-bar-label">${dayLabel}</div>
                </div>
            `;
        });

        html += '</div>';

        // Add summary
        html += `
            <div class="users-chart-summary">
                <span class="users-chart-total">Total: <strong>${total}</strong> new users in last ${days} days</span>
                <span class="users-chart-avg">Average: <strong>${(total / chartData.length).toFixed(1)}</strong> per day</span>
            </div>
        `;

        container.innerHTML = html;
    } catch (error) {
        console.error('Error loading users per day chart:', error);
        container.innerHTML = `<p class="loading">Error: ${error.message}</p>`;
    }
}

// Users chart period selector
document.getElementById('users-chart-period')?.addEventListener('change', (e) => {
    loadUsersPerDayChart(parseInt(e.target.value));
});

// Analytics refresh button
document.getElementById('refresh-analytics')?.addEventListener('click', loadAnalyticsPage);

// ============ Settings Page ============
async function loadSettingsPage() {
    try {
        const health = await api('/system/health');
        document.getElementById('settings-health-status').textContent = health.status === 'healthy' ? 'HEALTHY' : 'UNHEALTHY';
        document.getElementById('settings-health-status').className = health.status === 'healthy'
            ? 'health-badge healthy'
            : 'health-badge unhealthy';

        document.getElementById('settings-db-status').textContent = health.database === 'healthy' ? 'CONNECTED' : 'DISCONNECTED';
        document.getElementById('settings-db-status').className = health.database === 'healthy'
            ? 'health-badge healthy'
            : 'health-badge unhealthy';
    } catch (error) {
        console.error('Error loading settings:', error);
        document.getElementById('settings-health-status').textContent = 'ERROR';
        document.getElementById('settings-db-status').textContent = 'ERROR';
    }
}

// Database backup button
document.getElementById('backup-database-btn')?.addEventListener('click', () => {
    if (confirm('This will download a SQL backup of the database. Continue?')) {
        window.open('/api/system/backup', '_blank');
    }
});

// Make showUserDetail globally accessible
window.showUserDetail = showUserDetail;
