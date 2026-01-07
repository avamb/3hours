/**
 * MINDSETHAPPYBOT Admin Panel - Node.js Server
 * Provides admin dashboard functionality for monitoring users, messages, and system health
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pg from 'pg';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const PORT = process.env.ADMIN_PORT || 8080;
const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/mindsethappybot';
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';

// Parse database URL
const dbConfig = new URL(DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql://'));
const pool = new pg.Pool({
    host: dbConfig.hostname,
    port: parseInt(dbConfig.port) || 5432,
    database: dbConfig.pathname.slice(1),
    user: dbConfig.username,
    password: dbConfig.password,
    max: 10,
    idleTimeoutMillis: 30000,
});

// MIME types
const mimeTypes = {
    '.html': 'text/html',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.ico': 'image/x-icon',
};

// Helper to send JSON response
function sendJson(res, data, status = 200) {
    res.writeHead(status, {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
    });
    res.end(JSON.stringify(data));
}

// Helper to parse JSON body
async function parseBody(req) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => body += chunk);
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (e) {
                reject(e);
            }
        });
        req.on('error', reject);
    });
}

// Helper to parse query params
function parseQuery(url) {
    const params = new URL(url, 'http://localhost').searchParams;
    const result = {};
    for (const [key, value] of params) {
        result[key] = value;
    }
    return result;
}

// Serve static files
async function serveStatic(req, res) {
    let filePath = path.join(__dirname, 'static', req.url === '/' ? 'index.html' : req.url.replace('/static/', ''));

    if (req.url === '/') {
        filePath = path.join(__dirname, 'static', 'index.html');
    } else if (req.url.startsWith('/static/')) {
        filePath = path.join(__dirname, 'static', req.url.replace('/static/', ''));
    } else {
        return false;
    }

    try {
        const content = await fs.promises.readFile(filePath);
        const ext = path.extname(filePath);
        res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
        res.end(content);
        return true;
    } catch (e) {
        return false;
    }
}

// API Routes
const routes = {
    // Auth
    'POST /api/auth/login': async (req, res) => {
        const body = await parseBody(req);
        if (body.username === ADMIN_USERNAME && body.password === ADMIN_PASSWORD) {
            sendJson(res, { success: true, message: 'Login successful' });
        } else {
            sendJson(res, { detail: 'Invalid credentials' }, 401);
        }
    },

    // Stats
    'GET /api/stats': async (req, res) => {
        const client = await pool.connect();
        try {
            const now = new Date();
            const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
            const dayAgo = new Date(now - 24 * 60 * 60 * 1000);

            const [
                totalUsers,
                active24h,
                active7d,
                totalMoments,
                totalConversations,
                momentsToday,
                momentsWeek
            ] = await Promise.all([
                client.query('SELECT COUNT(*) FROM users'),
                client.query('SELECT COUNT(*) FROM users WHERE last_active_at > $1', [dayAgo]),
                client.query('SELECT COUNT(*) FROM users WHERE last_active_at > $1', [weekAgo]),
                client.query('SELECT COUNT(*) FROM moments'),
                client.query('SELECT COUNT(*) FROM conversations'),
                client.query('SELECT COUNT(*) FROM moments WHERE created_at >= $1', [todayStart]),
                client.query('SELECT COUNT(*) FROM moments WHERE created_at >= $1', [weekAgo]),
            ]);

            sendJson(res, {
                total_users: parseInt(totalUsers.rows[0].count),
                active_users_24h: parseInt(active24h.rows[0].count),
                active_users_7d: parseInt(active7d.rows[0].count),
                total_moments: parseInt(totalMoments.rows[0].count),
                total_conversations: parseInt(totalConversations.rows[0].count),
                moments_today: parseInt(momentsToday.rows[0].count),
                moments_week: parseInt(momentsWeek.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Users list
    'GET /api/users': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const offset = parseInt(query.offset) || 0;
        const search = query.search || '';

        const client = await pool.connect();
        try {
            let whereClause = '';
            const params = [limit, offset];

            if (search) {
                whereClause = `WHERE u.username ILIKE $3 OR u.first_name ILIKE $3 OR CAST(u.telegram_id AS TEXT) LIKE $3`;
                params.push(`%${search}%`);
            }

            const result = await client.query(`
                SELECT
                    u.id, u.telegram_id, u.username, u.first_name,
                    u.language_code, u.notifications_enabled, u.created_at,
                    u.last_active_at, u.onboarding_completed,
                    COALESCE(s.total_moments, 0) as total_moments,
                    COALESCE(s.current_streak, 0) as current_streak
                FROM users u
                LEFT JOIN user_stats s ON u.id = s.user_id
                ${whereClause}
                ORDER BY u.last_active_at DESC NULLS LAST
                LIMIT $1 OFFSET $2
            `, params);

            const countResult = await client.query(
                `SELECT COUNT(*) FROM users u ${whereClause}`,
                search ? [`%${search}%`] : []
            );

            sendJson(res, {
                users: result.rows.map(row => ({
                    id: row.id,
                    telegram_id: row.telegram_id.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    language_code: row.language_code,
                    notifications_enabled: row.notifications_enabled,
                    created_at: row.created_at?.toISOString(),
                    last_active_at: row.last_active_at?.toISOString(),
                    onboarding_completed: row.onboarding_completed,
                    total_moments: parseInt(row.total_moments),
                    current_streak: parseInt(row.current_streak),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // User detail
    'GET /api/users/:id': async (req, res, params) => {
        const userId = parseInt(params.id);
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    u.id, u.telegram_id, u.username, u.first_name,
                    u.language_code, u.formal_address, u.active_hours_start,
                    u.active_hours_end, u.notification_interval_hours,
                    u.notifications_enabled, u.timezone, u.created_at,
                    u.last_active_at, u.onboarding_completed,
                    COALESCE(s.total_moments, 0) as total_moments,
                    COALESCE(s.current_streak, 0) as current_streak,
                    COALESCE(s.longest_streak, 0) as longest_streak,
                    COALESCE(s.total_questions_sent, 0) as total_questions_sent,
                    COALESCE(s.total_questions_answered, 0) as total_questions_answered
                FROM users u
                LEFT JOIN user_stats s ON u.id = s.user_id
                WHERE u.id = $1
            `, [userId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'User not found' }, 404);
                return;
            }

            const user = result.rows[0];
            sendJson(res, {
                id: user.id,
                telegram_id: user.telegram_id.toString(),
                username: user.username,
                first_name: user.first_name,
                language_code: user.language_code,
                formal_address: user.formal_address,
                active_hours_start: user.active_hours_start?.toString(),
                active_hours_end: user.active_hours_end?.toString(),
                notification_interval_hours: user.notification_interval_hours,
                notifications_enabled: user.notifications_enabled,
                timezone: user.timezone,
                created_at: user.created_at?.toISOString(),
                last_active_at: user.last_active_at?.toISOString(),
                onboarding_completed: user.onboarding_completed,
                total_moments: parseInt(user.total_moments),
                current_streak: parseInt(user.current_streak),
                longest_streak: parseInt(user.longest_streak),
                total_questions_sent: parseInt(user.total_questions_sent),
                total_questions_answered: parseInt(user.total_questions_answered),
            });
        } finally {
            client.release();
        }
    },

    // User moments
    'GET /api/users/:id/moments': async (req, res, params) => {
        const userId = parseInt(params.id);
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 20, 100);
        const offset = parseInt(query.offset) || 0;

        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT id, content, source_type, mood_score, topics, created_at
                FROM moments
                WHERE user_id = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
            `, [userId, limit, offset]);

            const countResult = await client.query(
                'SELECT COUNT(*) FROM moments WHERE user_id = $1',
                [userId]
            );

            sendJson(res, {
                moments: result.rows.map(row => ({
                    id: row.id,
                    content: row.content,
                    source_type: row.source_type,
                    mood_score: row.mood_score,
                    topics: row.topics,
                    created_at: row.created_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Conversations
    'GET /api/conversations': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const offset = parseInt(query.offset) || 0;
        const messageType = query.message_type;
        const userId = query.user_id ? parseInt(query.user_id) : null;

        const client = await pool.connect();
        try {
            let whereClause = '1=1';
            const params = [limit, offset];
            let paramIndex = 3;

            if (messageType) {
                whereClause += ` AND c.message_type = $${paramIndex}`;
                params.push(messageType);
                paramIndex++;
            }

            if (userId) {
                whereClause += ` AND c.user_id = $${paramIndex}`;
                params.push(userId);
                paramIndex++;
            }

            const result = await client.query(`
                SELECT
                    c.id, c.user_id, u.telegram_id, u.username,
                    c.message_type, c.content, c.created_at
                FROM conversations c
                JOIN users u ON c.user_id = u.id
                WHERE ${whereClause}
                ORDER BY c.created_at DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Count query
            const countParams = [];
            let countWhere = '1=1';
            let countParamIndex = 1;

            if (messageType) {
                countWhere += ` AND message_type = $${countParamIndex}`;
                countParams.push(messageType);
                countParamIndex++;
            }

            if (userId) {
                countWhere += ` AND user_id = $${countParamIndex}`;
                countParams.push(userId);
            }

            const countResult = await client.query(
                `SELECT COUNT(*) FROM conversations WHERE ${countWhere}`,
                countParams
            );

            sendJson(res, {
                conversations: result.rows.map(row => ({
                    id: row.id,
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username,
                    message_type: row.message_type,
                    content: row.content?.substring(0, 500),
                    created_at: row.created_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },


    // Messages (unified view combining conversations and scheduled notifications)
    'GET /api/messages': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const offset = parseInt(query.offset) || 0;
        const messageType = query.message_type;
        const userId = query.user_id ? parseInt(query.user_id) : null;

        const client = await pool.connect();
        try {
            let messages = [];
            let total = 0;

            if (messageType && messageType !== 'scheduled_question') {
                let whereClause = '1=1';
                const params = [limit, offset];
                let paramIndex = 3;

                whereClause += ` AND c.message_type = $${paramIndex}`;
                params.push(messageType);
                paramIndex++;

                if (userId) {
                    whereClause += ` AND c.user_id = $${paramIndex}`;
                    params.push(userId);
                }

                const result = await client.query(`
                    SELECT c.id, c.user_id, u.telegram_id, u.username, u.first_name,
                           c.message_type, c.content, c.created_at as time
                    FROM conversations c
                    JOIN users u ON c.user_id = u.id
                    WHERE ${whereClause}
                    ORDER BY c.created_at DESC
                    LIMIT $1 OFFSET $2
                `, params);

                const countParams = [messageType];
                let countParamIndex = 2;
                let countWhere = 'message_type = $1';
                if (userId) {
                    countWhere += ` AND user_id = $${countParamIndex}`;
                    countParams.push(userId);
                }

                const countResult = await client.query(
                    `SELECT COUNT(*) FROM conversations WHERE ${countWhere}`,
                    countParams
                );

                messages = result.rows.map(row => ({
                    id: row.id,
                    source: 'conversation',
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username || row.first_name || `User #${row.user_id}`,
                    message_type: row.message_type,
                    content: row.content?.substring(0, 500) || '',
                    time: row.time?.toISOString(),
                    status: 'sent',
                }));
                total = parseInt(countResult.rows[0].count);
            }
            else if (messageType === 'scheduled_question') {
                let whereClause = '1=1';
                const params = [limit, offset];
                let paramIndex = 3;

                if (userId) {
                    whereClause += ` AND n.user_id = $${paramIndex}`;
                    params.push(userId);
                }

                const result = await client.query(`
                    SELECT n.id, n.user_id, u.telegram_id, u.username, u.first_name,
                           'scheduled_question' as message_type,
                           COALESCE(q.template_text, 'Scheduled question') as content,
                           n.scheduled_time as time, n.sent, n.sent_at
                    FROM scheduled_notifications n
                    JOIN users u ON n.user_id = u.id
                    LEFT JOIN question_templates q ON n.question_template_id = q.id
                    WHERE ${whereClause}
                    ORDER BY n.scheduled_time DESC
                    LIMIT $1 OFFSET $2
                `, params);

                const countParams = [];
                let countWhere = '1=1';
                if (userId) {
                    countWhere = 'user_id = $1';
                    countParams.push(userId);
                }

                const countResult = await client.query(
                    `SELECT COUNT(*) FROM scheduled_notifications WHERE ${countWhere}`,
                    countParams
                );

                messages = result.rows.map(row => ({
                    id: row.id,
                    source: 'scheduled',
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username || row.first_name || `User #${row.user_id}`,
                    message_type: row.message_type,
                    content: row.content?.substring(0, 500) || 'Scheduled question',
                    time: row.time?.toISOString(),
                    status: row.sent ? 'sent' : 'pending',
                    sent_at: row.sent_at?.toISOString(),
                }));
                total = parseInt(countResult.rows[0].count);
            }
            else {
                const params = [limit, offset];
                let userFilterConv = '';
                let userFilterSched = '';

                if (userId) {
                    userFilterConv = 'AND c.user_id = $3';
                    userFilterSched = 'AND n.user_id = $3';
                    params.push(userId);
                }

                const result = await client.query(`
                    SELECT * FROM (
                        SELECT c.id, 'conversation' as source, c.user_id, u.telegram_id, u.username, u.first_name,
                               c.message_type, c.content, c.created_at as time,
                               'sent' as status, NULL::timestamp as sent_at
                        FROM conversations c
                        JOIN users u ON c.user_id = u.id
                        WHERE 1=1 ${userFilterConv}

                        UNION ALL

                        SELECT n.id, 'scheduled' as source, n.user_id, u.telegram_id, u.username, u.first_name,
                               'scheduled_question' as message_type,
                               COALESCE(q.template_text, 'Scheduled question') as content,
                               n.scheduled_time as time,
                               CASE WHEN n.sent THEN 'sent' ELSE 'pending' END as status,
                               n.sent_at
                        FROM scheduled_notifications n
                        JOIN users u ON n.user_id = u.id
                        LEFT JOIN question_templates q ON n.question_template_id = q.id
                        WHERE 1=1 ${userFilterSched}
                    ) combined
                    ORDER BY time DESC
                    LIMIT $1 OFFSET $2
                `, params);

                let countQuery;
                let countParams = [];
                if (userId) {
                    countQuery = `SELECT (SELECT COUNT(*) FROM conversations WHERE user_id = $1) + (SELECT COUNT(*) FROM scheduled_notifications WHERE user_id = $1) as total`;
                    countParams = [userId];
                } else {
                    countQuery = `SELECT (SELECT COUNT(*) FROM conversations) + (SELECT COUNT(*) FROM scheduled_notifications) as total`;
                }

                const countResult = await client.query(countQuery, countParams);

                messages = result.rows.map(row => ({
                    id: row.id,
                    source: row.source,
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username || row.first_name || `User #${row.user_id}`,
                    message_type: row.message_type,
                    content: row.content?.substring(0, 500) || '',
                    time: row.time?.toISOString(),
                    status: row.status,
                    sent_at: row.sent_at?.toISOString(),
                }));
                total = parseInt(countResult.rows[0].total);
            }

            sendJson(res, { messages, total });
        } finally {
            client.release();
        }
    },

    // System health
    'GET /api/system/health': async (req, res) => {
        let dbStatus = 'healthy';
        try {
            const client = await pool.connect();
            await client.query('SELECT 1');
            client.release();
        } catch (e) {
            dbStatus = `error: ${e.message}`;
        }

        sendJson(res, {
            status: dbStatus === 'healthy' ? 'healthy' : 'unhealthy',
            database: dbStatus,
            timestamp: new Date().toISOString(),
        });
    },

    // System logs
    'GET /api/system/logs': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 100, 500);
        const level = query.level;

        const logs = [];

        try {
            const { execSync } = await import('child_process');
            const output = execSync(`docker logs --tail ${limit} mindsethappybot 2>&1`, {
                encoding: 'utf-8',
                timeout: 5000,
            });

            const lines = output.split('\n').filter(line => line.trim());

            for (const line of lines.slice(-limit)) {
                let logLevel = 'INFO';
                if (line.includes('ERROR')) logLevel = 'ERROR';
                else if (line.includes('WARNING') || line.includes('WARN')) logLevel = 'WARNING';
                else if (line.includes('DEBUG')) logLevel = 'DEBUG';

                if (level && logLevel !== level.toUpperCase()) continue;

                logs.push({
                    timestamp: new Date().toISOString(),
                    level: logLevel,
                    message: line.substring(0, 500),
                    source: 'bot',
                });
            }
        } catch (e) {
            logs.push({
                timestamp: new Date().toISOString(),
                level: 'WARNING',
                message: `Could not read bot logs: ${e.message}`,
                source: 'admin',
            });
        }

        sendJson(res, { logs });
    },

    // Scheduled notifications
    'GET /api/system/notifications': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const pendingOnly = query.pending_only === 'true';

        const client = await pool.connect();
        try {
            let whereClause = '';
            if (pendingOnly) {
                whereClause = 'WHERE n.sent = false';
            }

            const result = await client.query(`
                SELECT
                    n.id, n.user_id, u.username, u.first_name,
                    n.scheduled_time, n.sent, n.sent_at, n.created_at
                FROM scheduled_notifications n
                JOIN users u ON n.user_id = u.id
                ${whereClause}
                ORDER BY n.scheduled_time DESC
                LIMIT $1
            `, [limit]);

            sendJson(res, {
                notifications: result.rows.map(row => ({
                    id: row.id,
                    user_id: row.user_id,
                    username: row.username,
                    first_name: row.first_name,
                    scheduled_time: row.scheduled_time?.toISOString(),
                    sent: row.sent,
                    sent_at: row.sent_at?.toISOString(),
                    created_at: row.created_at?.toISOString(),
                })),
            });
        } finally {
            client.release();
        }
    },

    // Feedback list
    'GET /api/feedback': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const offset = parseInt(query.offset) || 0;
        const status = query.status;

        const client = await pool.connect();
        try {
            let whereClause = '1=1';
            const params = [limit, offset];
            let paramIndex = 3;

            if (status) {
                whereClause += ` AND f.status = $${paramIndex}`;
                params.push(status);
                paramIndex++;
            }

            const result = await client.query(`
                SELECT
                    f.id, f.user_id, u.telegram_id, u.username, u.first_name,
                    f.content, f.category, f.status, f.admin_notes,
                    f.reviewed_at, f.created_at
                FROM feedback f
                JOIN users u ON f.user_id = u.id
                WHERE ${whereClause}
                ORDER BY f.created_at DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Count query
            const countParams = [];
            let countWhere = '1=1';
            let countParamIndex = 1;

            if (status) {
                countWhere += ` AND status = $${countParamIndex}`;
                countParams.push(status);
            }

            const countResult = await client.query(
                `SELECT COUNT(*) FROM feedback WHERE ${countWhere}`,
                countParams
            );

            sendJson(res, {
                feedback: result.rows.map(row => ({
                    id: row.id,
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    content: row.content,
                    category: row.category,
                    status: row.status,
                    admin_notes: row.admin_notes,
                    reviewed_at: row.reviewed_at?.toISOString(),
                    created_at: row.created_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Update feedback status
    'POST /api/feedback/:id/status': async (req, res, params) => {
        const feedbackId = parseInt(params.id);
        const body = await parseBody(req);
        const { status, admin_notes } = body;

        if (!status || !['new', 'reviewed', 'implemented', 'rejected'].includes(status)) {
            sendJson(res, { detail: 'Invalid status' }, 400);
            return;
        }

        const client = await pool.connect();
        try {
            const result = await client.query(`
                UPDATE feedback
                SET status = $1, admin_notes = $2, reviewed_at = $3
                WHERE id = $4
                RETURNING *
            `, [status, admin_notes || null, status !== 'new' ? new Date() : null, feedbackId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Feedback not found' }, 404);
                return;
            }

            sendJson(res, {
                success: true,
                feedback: {
                    id: result.rows[0].id,
                    status: result.rows[0].status,
                    admin_notes: result.rows[0].admin_notes,
                    reviewed_at: result.rows[0].reviewed_at?.toISOString(),
                }
            });
        } finally {
            client.release();
        }
    },

    // Feedback stats
    'GET /api/feedback/stats': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'new') as new_count,
                    COUNT(*) FILTER (WHERE status = 'reviewed') as reviewed_count,
                    COUNT(*) FILTER (WHERE status = 'implemented') as implemented_count,
                    COUNT(*) FILTER (WHERE status = 'rejected') as rejected_count,
                    COUNT(*) FILTER (WHERE category = 'suggestion') as suggestions,
                    COUNT(*) FILTER (WHERE category = 'bug') as bugs,
                    COUNT(*) FILTER (WHERE category = 'other') as other
                FROM feedback
            `);

            const stats = result.rows[0];
            sendJson(res, {
                total: parseInt(stats.total),
                by_status: {
                    new: parseInt(stats.new_count),
                    reviewed: parseInt(stats.reviewed_count),
                    implemented: parseInt(stats.implemented_count),
                    rejected: parseInt(stats.rejected_count),
                },
                by_category: {
                    suggestion: parseInt(stats.suggestions),
                    bug: parseInt(stats.bugs),
                    other: parseInt(stats.other),
                }
            });
        } finally {
            client.release();
        }
    },
};

// Match route with params
function matchRoute(method, url) {
    const path = url.split('?')[0];

    for (const [pattern, handler] of Object.entries(routes)) {
        const [routeMethod, routePath] = pattern.split(' ');
        if (routeMethod !== method) continue;

        // Check for exact match
        if (routePath === path) {
            return { handler, params: {} };
        }

        // Check for parameterized match
        const routeParts = routePath.split('/');
        const pathParts = path.split('/');

        if (routeParts.length !== pathParts.length) continue;

        const params = {};
        let match = true;

        for (let i = 0; i < routeParts.length; i++) {
            if (routeParts[i].startsWith(':')) {
                params[routeParts[i].slice(1)] = pathParts[i];
            } else if (routeParts[i] !== pathParts[i]) {
                match = false;
                break;
            }
        }

        if (match) {
            return { handler, params };
        }
    }

    return null;
}

// Create HTTP server
const server = http.createServer(async (req, res) => {
    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        });
        res.end();
        return;
    }

    try {
        // Try serving static files first
        if (req.method === 'GET' && (req.url === '/' || req.url.startsWith('/static/'))) {
            const served = await serveStatic(req, res);
            if (served) return;
        }

        // Try API routes
        const match = matchRoute(req.method, req.url);
        if (match) {
            await match.handler(req, res, match.params);
            return;
        }

        // 404
        sendJson(res, { detail: 'Not found' }, 404);
    } catch (error) {
        console.error('Server error:', error);
        sendJson(res, { detail: error.message }, 500);
    }
});

// Start server
server.listen(PORT, () => {
    console.log(`Admin panel running at http://localhost:${PORT}`);
    console.log(`Database: ${DATABASE_URL}`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down...');
    await pool.end();
    server.close();
    process.exit(0);
});
