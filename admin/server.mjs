/**
 * MINDSETHAPPYBOT Admin Panel - Node.js Server
 * Provides admin dashboard functionality for monitoring users, messages, and system health
 */

import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pg from 'pg';
import OpenAI from 'openai';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const PORT = process.env.PORT || 8080;
const DATABASE_URL = process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/mindsethappybot';
const ADMIN_USERNAME = process.env.ADMIN_USERNAME || 'admin';
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'admin123';
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || '';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

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

// =============================================================================
// KNOWLEDGE BASE INDEXING
// =============================================================================

// Indexing limits (guardrails)
const MAX_DOC_CHARS = 120000;
const MIN_DOC_CHARS = 50;
const CHUNK_SIZE = 1200;
const CHUNK_OVERLAP = 200;
const MAX_CHUNKS = 120;
const MAX_RETRIES = 3;
const BASE_DELAY_MS = 500;
const RATE_LIMIT_DELAY_MS = 100;

// Initialize OpenAI client (lazy - only when needed)
let openaiClient = null;
function getOpenAIClient() {
    if (!openaiClient && OPENAI_API_KEY) {
        openaiClient = new OpenAI({ apiKey: OPENAI_API_KEY });
    }
    return openaiClient;
}

// Helper to sleep for a given number of milliseconds
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Split text into chunks with overlap, trying to split at sentence boundaries
 * @param {string} text - The text to split
 * @param {number} chunkSize - Target chunk size in characters
 * @param {number} overlap - Number of characters to overlap between chunks
 * @returns {string[]} - Array of text chunks
 */
function splitTextIntoChunks(text, chunkSize = CHUNK_SIZE, overlap = CHUNK_OVERLAP) {
    if (!text || text.length === 0) {
        return [];
    }

    // If the text is smaller than the chunk size, return it as a single chunk
    if (text.length <= chunkSize) {
        return [text.trim()].filter(c => c.length > 0);
    }

    const chunks = [];
    let start = 0;
    const sentenceEnders = /[.!?\n]/g;

    while (start < text.length) {
        let end = Math.min(start + chunkSize, text.length);

        // If we're not at the end, try to find a sentence boundary
        if (end < text.length) {
            // Look for a sentence boundary in the last portion of the chunk
            const searchStart = Math.max(start, end - 200);
            const searchText = text.substring(searchStart, end);

            let lastBoundary = -1;
            let match;
            sentenceEnders.lastIndex = 0;

            while ((match = sentenceEnders.exec(searchText)) !== null) {
                lastBoundary = searchStart + match.index + 1;
            }

            // Use the sentence boundary if found, otherwise use chunkSize
            if (lastBoundary > start && lastBoundary > start + chunkSize / 2) {
                end = lastBoundary;
            }
        }

        const chunk = text.substring(start, end).trim();
        if (chunk.length > 0) {
            chunks.push(chunk);
        }

        // If we've reached the end, stop
        if (end >= text.length) {
            break;
        }

        // Move start forward by (chunk length - overlap)
        // Ensure we make meaningful progress (at least half of chunk size or to the end)
        const chunkLength = end - start;
        const advancement = Math.max(chunkLength - overlap, Math.min(chunkSize / 2, text.length - start));
        start += advancement;
    }

    return chunks;
}

/**
 * Convert embedding array to pgvector literal string
 * @param {number[]} embedding - The embedding array
 * @returns {string} - pgvector literal like "[0.1,0.2,...]"
 */
function vectorLiteral(embedding) {
    return '[' + embedding.join(',') + ']';
}

/**
 * Create embedding with retry logic for rate limiting
 * @param {OpenAI} client - OpenAI client
 * @param {string} text - Text to embed
 * @returns {Promise<number[]>} - Embedding array
 */
async function createEmbeddingWithRetry(client, text) {
    let lastError;

    for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
        try {
            const response = await client.embeddings.create({
                model: 'text-embedding-3-small',
                input: text,
            });
            return response.data[0].embedding;
        } catch (error) {
            lastError = error;

            // Check if it's a rate limit error (429) or timeout
            const isRateLimited = error.status === 429 ||
                                  error.code === 'ETIMEDOUT' ||
                                  error.code === 'ECONNRESET';

            if (isRateLimited && attempt < MAX_RETRIES) {
                const delay = BASE_DELAY_MS * Math.pow(2, attempt - 1);
                console.log(`OpenAI rate limited, retrying in ${delay}ms (attempt ${attempt}/${MAX_RETRIES})`);
                await sleep(delay);
            } else {
                throw error;
            }
        }
    }

    throw lastError;
}

/**
 * Index a knowledge base item - creates chunks and embeddings
 * @param {number} itemId - The knowledge_base item ID to index
 */
async function indexKnowledgeItem(itemId) {
    const client = await pool.connect();

    try {
        // 1. Get the knowledge base item
        const itemResult = await client.query(
            'SELECT id, content, file_type, indexing_status FROM knowledge_base WHERE id = $1',
            [itemId]
        );

        if (itemResult.rows.length === 0) {
            console.error(`[Indexing] Item ${itemId} not found`);
            return;
        }

        const item = itemResult.rows[0];

        // Check if already indexing (prevent double processing)
        if (item.indexing_status === 'indexing') {
            console.log(`[Indexing] Item ${itemId} is already being indexed, skipping`);
            return;
        }

        // 2. Set status to indexing
        await client.query(
            `UPDATE knowledge_base
             SET indexing_status = 'indexing', indexing_error = NULL, updated_at = NOW()
             WHERE id = $1`,
            [itemId]
        );

        const content = item.content || '';

        // 3. Validate content - check for PDF first
        if (item.file_type === 'pdf') {
            await setIndexingError(client, itemId, 'PDF not supported yet');
            return;
        }

        // 4. Validate content length
        if (content.length < MIN_DOC_CHARS) {
            await setIndexingError(client, itemId, `Document too short/empty (min ${MIN_DOC_CHARS} chars)`);
            return;
        }

        if (content.length > MAX_DOC_CHARS) {
            await setIndexingError(client, itemId, `Document too large (max ${MAX_DOC_CHARS} chars)`);
            return;
        }

        // 5. Check OpenAI API key
        const openai = getOpenAIClient();
        if (!openai) {
            await setIndexingError(client, itemId, 'OpenAI API key not configured');
            return;
        }

        // 6. Split into chunks
        const chunks = splitTextIntoChunks(content, CHUNK_SIZE, CHUNK_OVERLAP);

        if (chunks.length === 0) {
            await setIndexingError(client, itemId, 'Document produced no valid chunks');
            return;
        }

        // 7. Check chunk count limit
        if (chunks.length > MAX_CHUNKS) {
            await setIndexingError(client, itemId, `Too many chunks (${chunks.length} > ${MAX_CHUNKS}). Document too large or complex.`);
            return;
        }

        console.log(`[Indexing] Item ${itemId}: Processing ${chunks.length} chunks`);

        // 8. Delete existing chunks
        await client.query('DELETE FROM knowledge_chunks WHERE knowledge_base_id = $1', [itemId]);

        // 9. Create embeddings and insert chunks
        for (let i = 0; i < chunks.length; i++) {
            const chunk = chunks[i];

            try {
                // Rate limiting - add a small delay between requests
                if (i > 0) {
                    await sleep(RATE_LIMIT_DELAY_MS);
                }

                // Create embedding
                const embedding = await createEmbeddingWithRetry(openai, chunk);

                // Insert chunk with embedding
                await client.query(
                    `INSERT INTO knowledge_chunks (knowledge_base_id, chunk_index, content, embedding)
                     VALUES ($1, $2, $3, $4::vector)`,
                    [itemId, i, chunk, vectorLiteral(embedding)]
                );

                console.log(`[Indexing] Item ${itemId}: Chunk ${i + 1}/${chunks.length} completed`);
            } catch (error) {
                console.error(`[Indexing] Item ${itemId}: Error processing chunk ${i}:`, error.message);
                await setIndexingError(client, itemId, `Error embedding chunk ${i + 1}: ${error.message}`);
                return;
            }
        }

        // 10. Update status to indexed
        await client.query(
            `UPDATE knowledge_base
             SET indexing_status = 'indexed',
                 chunks_count = $2,
                 indexing_error = NULL,
                 updated_at = NOW()
             WHERE id = $1`,
            [itemId, chunks.length]
        );

        console.log(`[Indexing] Item ${itemId}: Successfully indexed with ${chunks.length} chunks`);

    } catch (error) {
        console.error(`[Indexing] Item ${itemId}: Fatal error:`, error.message);
        try {
            await setIndexingError(client, itemId, error.message);
        } catch (e) {
            console.error(`[Indexing] Item ${itemId}: Could not set error status:`, e.message);
        }
    } finally {
        client.release();
    }
}

/**
 * Helper to set indexing error status
 * @param {pg.PoolClient} client - Database client
 * @param {number} itemId - Item ID
 * @param {string} errorMessage - Error message (will be truncated to 1000 chars)
 */
async function setIndexingError(client, itemId, errorMessage) {
    const truncatedError = errorMessage.substring(0, 1000);
    await client.query(
        `UPDATE knowledge_base
         SET indexing_status = 'error',
             indexing_error = $2,
             chunks_count = 0,
             updated_at = NOW()
         WHERE id = $1`,
        [itemId, truncatedError]
    );
    console.log(`[Indexing] Item ${itemId}: Error - ${truncatedError}`);
}

// =============================================================================
// END KNOWLEDGE BASE INDEXING
// =============================================================================

// Serve static files
async function serveStatic(req, res) {
    const url = new URL(req.url, 'http://localhost');
    const pathname = url.pathname;

    // Return empty favicon to avoid 404 errors
    if (pathname === '/favicon.ico') {
        res.writeHead(204);
        res.end();
        return true;
    }

    let filePath;
    if (pathname === '/') {
        filePath = path.join(__dirname, 'static', 'index.html');
    } else if (pathname.startsWith('/static/')) {
        filePath = path.join(__dirname, 'static', pathname.replace('/static/', ''));
    } else {
        return false;
    }

    try {
        const content = await fs.promises.readFile(filePath);
        const ext = path.extname(filePath);
        const cacheControl = ext === '.html' ? 'no-store' : 'no-cache';
        res.writeHead(200, {
            'Content-Type': mimeTypes[ext] || 'text/plain',
            'Cache-Control': cacheControl,
            'X-Content-Type-Options': 'nosniff',
        });
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

    // API Usage / Expenses
    'GET /api/expenses': async (req, res) => {
        const query = parseQuery(req.url);
        const days = parseInt(query.days) || 30;
        const client = await pool.connect();

        try {
            const startDate = new Date(Date.now() - days * 24 * 60 * 60 * 1000);

            // Check if table exists
            const tableCheck = await client.query(`
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_name = 'api_usage'
                )
            `);

            if (!tableCheck.rows[0].exists) {
                sendJson(res, {
                    period: { start: startDate.toISOString(), end: new Date().toISOString() },
                    totals: { requests: 0, tokens: 0, cost: 0 },
                    by_model: [],
                    by_operation: [],
                    daily: [],
                    recent: [],
                });
                return;
            }

            // Total stats
            const totals = await client.query(`
                SELECT
                    COUNT(*) as total_requests,
                    COALESCE(SUM(total_tokens), 0) as total_tokens,
                    COALESCE(SUM(cost_usd), 0) as total_cost
                FROM api_usage
                WHERE created_at >= $1
            `, [startDate]);

            // Stats by model
            const byModel = await client.query(`
                SELECT
                    model,
                    COUNT(*) as requests,
                    COALESCE(SUM(total_tokens), 0) as tokens,
                    COALESCE(SUM(cost_usd), 0) as cost
                FROM api_usage
                WHERE created_at >= $1
                GROUP BY model
                ORDER BY SUM(cost_usd) DESC
            `, [startDate]);

            // Stats by operation type
            const byOperation = await client.query(`
                SELECT
                    operation_type as operation,
                    COUNT(*) as requests,
                    COALESCE(SUM(total_tokens), 0) as tokens,
                    COALESCE(SUM(cost_usd), 0) as cost
                FROM api_usage
                WHERE created_at >= $1
                GROUP BY operation_type
                ORDER BY SUM(cost_usd) DESC
            `, [startDate]);

            // Daily stats
            const daily = await client.query(`
                SELECT
                    DATE_TRUNC('day', created_at) as date,
                    COUNT(*) as requests,
                    COALESCE(SUM(total_tokens), 0) as tokens,
                    COALESCE(SUM(cost_usd), 0) as cost
                FROM api_usage
                WHERE created_at >= $1
                GROUP BY DATE_TRUNC('day', created_at)
                ORDER BY date ASC
            `, [startDate]);

            // Recent usage
            const recent = await client.query(`
                SELECT
                    id, user_id, api_provider, model, operation_type,
                    input_tokens, output_tokens, total_tokens,
                    cost_usd, duration_ms, success, created_at
                FROM api_usage
                ORDER BY created_at DESC
                LIMIT 50
            `);

            sendJson(res, {
                period: {
                    start: startDate.toISOString(),
                    end: new Date().toISOString(),
                },
                totals: {
                    requests: parseInt(totals.rows[0].total_requests) || 0,
                    tokens: parseInt(totals.rows[0].total_tokens) || 0,
                    cost: parseFloat(totals.rows[0].total_cost) || 0,
                },
                by_model: byModel.rows.map(r => ({
                    model: r.model,
                    requests: parseInt(r.requests),
                    tokens: parseInt(r.tokens),
                    cost: parseFloat(r.cost),
                })),
                by_operation: byOperation.rows.map(r => ({
                    operation: r.operation,
                    requests: parseInt(r.requests),
                    tokens: parseInt(r.tokens),
                    cost: parseFloat(r.cost),
                })),
                daily: daily.rows.map(r => ({
                    date: r.date?.toISOString(),
                    requests: parseInt(r.requests),
                    tokens: parseInt(r.tokens),
                    cost: parseFloat(r.cost),
                })),
                recent: recent.rows.map(r => ({
                    id: r.id,
                    user_id: r.user_id,
                    api_provider: r.api_provider,
                    model: r.model,
                    operation_type: r.operation_type,
                    input_tokens: r.input_tokens,
                    output_tokens: r.output_tokens,
                    total_tokens: r.total_tokens,
                    cost_usd: parseFloat(r.cost_usd) || 0,
                    duration_ms: r.duration_ms,
                    success: r.success,
                    created_at: r.created_at?.toISOString(),
                })),
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
        const language = query.language || '';
        const status = query.status || '';
        const sort = query.sort || '';

        const client = await pool.connect();
        try {
            const conditions = [];
            const countConditions = [];
            const params = [limit, offset];
            let paramIndex = 3;

            // Search filter
            if (search) {
                conditions.push(`(u.username ILIKE $${paramIndex} OR u.first_name ILIKE $${paramIndex} OR CAST(u.telegram_id AS TEXT) LIKE $${paramIndex})`);
                countConditions.push(`(u.username ILIKE $${paramIndex - 2} OR u.first_name ILIKE $${paramIndex - 2} OR CAST(u.telegram_id AS TEXT) LIKE $${paramIndex - 2})`);
                params.push(`%${search}%`);
                paramIndex++;
            }

            // Language filter
            if (language) {
                conditions.push(`u.language_code = $${paramIndex}`);
                countConditions.push(`u.language_code = $${paramIndex - 2}`);
                params.push(language);
                paramIndex++;
            }

            // Status filter
            const now = new Date();
            const weekAgo = new Date(now - 7 * 24 * 60 * 60 * 1000);
            if (status === 'active') {
                conditions.push(`u.last_active_at > $${paramIndex}`);
                countConditions.push(`u.last_active_at > $${paramIndex - 2}`);
                params.push(weekAgo);
                paramIndex++;
            } else if (status === 'inactive') {
                conditions.push(`(u.last_active_at IS NULL OR u.last_active_at <= $${paramIndex})`);
                countConditions.push(`(u.last_active_at IS NULL OR u.last_active_at <= $${paramIndex - 2})`);
                params.push(weekAgo);
                paramIndex++;
            } else if (status === 'onboarded') {
                conditions.push('u.onboarding_completed = true');
                countConditions.push('u.onboarding_completed = true');
            } else if (status === 'not_onboarded') {
                conditions.push('u.onboarding_completed = false');
                countConditions.push('u.onboarding_completed = false');
            }

            const whereClause = conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : '';
            const countWhereClause = countConditions.length > 0 ? 'WHERE ' + countConditions.join(' AND ') : '';

            // Sort order
            let orderBy = 'u.last_active_at DESC NULLS LAST';
            if (sort === 'created_desc') {
                orderBy = 'u.created_at DESC';
            } else if (sort === 'created_asc') {
                orderBy = 'u.created_at ASC';
            } else if (sort === 'moments_desc') {
                orderBy = 'total_moments DESC';
            } else if (sort === 'streak_desc') {
                orderBy = 'current_streak DESC';
            } else if (sort === 'active_desc') {
                orderBy = 'u.last_active_at DESC NULLS LAST';
            }

            const result = await client.query(`
                SELECT
                    u.id, u.telegram_id, u.username, u.first_name, u.gender,
                    u.language_code, u.notifications_enabled, u.created_at,
                    u.last_active_at, u.onboarding_completed, u.is_blocked,
                    COALESCE(s.total_moments, 0) as total_moments,
                    COALESCE(s.current_streak, 0) as current_streak
                FROM users u
                LEFT JOIN user_stats s ON u.id = s.user_id
                ${whereClause}
                ORDER BY ${orderBy}
                LIMIT $1 OFFSET $2
            `, params);

            // Build count params (without limit/offset)
            const countParams = params.slice(2);
            const countResult = await client.query(
                `SELECT COUNT(*) FROM users u LEFT JOIN user_stats s ON u.id = s.user_id ${countWhereClause}`,
                countParams
            );

            sendJson(res, {
                users: result.rows.map(row => ({
                    id: row.id,
                    telegram_id: row.telegram_id.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    gender: row.gender || 'unknown',
                    language_code: row.language_code,
                    notifications_enabled: row.notifications_enabled,
                    created_at: row.created_at?.toISOString(),
                    last_active_at: row.last_active_at?.toISOString(),
                    onboarding_completed: row.onboarding_completed,
                    is_blocked: row.is_blocked || false,
                    total_moments: parseInt(row.total_moments),
                    current_streak: parseInt(row.current_streak),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Export users to CSV - MUST be before /api/users/:id to match correctly
    'GET /api/users/export': async (req, res) => {
        const query = parseQuery(req.url);
        const search = query.search || '';

        const client = await pool.connect();
        try {
            let sqlQuery = `
                SELECT
                    u.id,
                    u.telegram_id,
                    u.username,
                    u.first_name,
                    u.language_code,
                    u.timezone,
                    u.notifications_enabled,
                    u.notification_interval_hours,
                    u.active_hours_start,
                    u.active_hours_end,
                    u.formal_address,
                    u.onboarding_completed,
                    u.is_blocked,
                    COALESCE(s.total_moments, 0) as total_moments,
                    COALESCE(s.current_streak, 0) as current_streak,
                    COALESCE(s.longest_streak, 0) as longest_streak,
                    COALESCE(s.total_questions_sent, 0) as total_questions_sent,
                    COALESCE(s.total_questions_answered, 0) as total_questions_answered,
                    u.created_at,
                    u.last_active_at
                FROM users u
                LEFT JOIN user_stats s ON u.id = s.user_id
            `;

            const params = [];
            if (search) {
                sqlQuery += `
                    WHERE u.username ILIKE $1
                    OR u.first_name ILIKE $1
                    OR CAST(u.telegram_id AS TEXT) ILIKE $1
                `;
                params.push(`%${search}%`);
            }

            sqlQuery += ' ORDER BY u.created_at DESC';

            const result = await client.query(sqlQuery, params);

            // Generate CSV
            const headers = [
                'ID', 'Telegram ID', 'Username', 'First Name', 'Language',
                'Timezone', 'Notifications Enabled', 'Notification Interval (hours)',
                'Active Hours Start', 'Active Hours End', 'Formal Address',
                'Onboarding Completed', 'Is Blocked', 'Total Moments',
                'Current Streak', 'Longest Streak', 'Questions Sent',
                'Questions Answered', 'Created At', 'Last Active At'
            ];

            const csvRows = [headers.join(',')];

            for (const row of result.rows) {
                const values = [
                    row.id,
                    row.telegram_id,
                    `"${(row.username || '').replace(/"/g, '""')}"`,
                    `"${(row.first_name || '').replace(/"/g, '""')}"`,
                    row.language_code,
                    row.timezone,
                    row.notifications_enabled,
                    row.notification_interval_hours,
                    row.active_hours_start,
                    row.active_hours_end,
                    row.formal_address,
                    row.onboarding_completed,
                    row.is_blocked,
                    row.total_moments,
                    row.current_streak,
                    row.longest_streak,
                    row.total_questions_sent,
                    row.total_questions_answered,
                    row.created_at?.toISOString() || '',
                    row.last_active_at?.toISOString() || ''
                ];
                csvRows.push(values.join(','));
            }

            const csv = csvRows.join('\n');
            const filename = `users_export_${new Date().toISOString().split('T')[0]}.csv`;

            res.writeHead(200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': `attachment; filename="${filename}"`,
            });
            res.end(csv);
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
                    u.id, u.telegram_id, u.username, u.first_name, u.gender,
                    u.language_code, u.formal_address, u.active_hours_start,
                    u.active_hours_end, u.notification_interval_hours,
                    u.notifications_enabled, u.timezone, u.created_at,
                    u.last_active_at, u.onboarding_completed, u.is_blocked,
                    COALESCE(s.total_moments, 0) as total_moments,
                    COALESCE(s.current_streak, 0) as current_streak,
                    COALESCE(s.longest_streak, 0) as longest_streak,
                    COALESCE(s.total_questions_sent, 0) as total_questions_sent,
                    COALESCE(s.total_questions_answered, 0) as total_questions_answered,
                    sp.instagram_url, sp.facebook_url, sp.twitter_url,
                    sp.linkedin_url, sp.vk_url, sp.telegram_channel_url,
                    sp.youtube_url, sp.tiktok_url, sp.bio_text,
                    sp.interests, sp.communication_style
                FROM users u
                LEFT JOIN user_stats s ON u.id = s.user_id
                LEFT JOIN social_profiles sp ON u.id = sp.user_id
                WHERE u.id = $1
            `, [userId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'User not found' }, 404);
                return;
            }

            const user = result.rows[0];

            // Build social profile object
            const socialProfile = {
                instagram_url: user.instagram_url,
                facebook_url: user.facebook_url,
                twitter_url: user.twitter_url,
                linkedin_url: user.linkedin_url,
                vk_url: user.vk_url,
                telegram_channel_url: user.telegram_channel_url,
                youtube_url: user.youtube_url,
                tiktok_url: user.tiktok_url,
                bio_text: user.bio_text,
                interests: user.interests,
                communication_style: user.communication_style,
            };

            // Check if any social profile data exists
            const hasSocialProfile = Object.values(socialProfile).some(v => v !== null && v !== undefined);

            sendJson(res, {
                id: user.id,
                telegram_id: user.telegram_id.toString(),
                username: user.username,
                first_name: user.first_name,
                gender: user.gender || 'unknown',
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
                is_blocked: user.is_blocked || false,
                total_moments: parseInt(user.total_moments),
                current_streak: parseInt(user.current_streak),
                longest_streak: parseInt(user.longest_streak),
                total_questions_sent: parseInt(user.total_questions_sent),
                total_questions_answered: parseInt(user.total_questions_answered),
                social_profile: hasSocialProfile ? socialProfile : null,
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

    // Block user
    'POST /api/users/:id/block': async (req, res, params) => {
        const userId = parseInt(params.id);

        const client = await pool.connect();
        try {
            const result = await client.query(`
                UPDATE users
                SET is_blocked = true
                WHERE id = $1
                RETURNING id, username, first_name, is_blocked
            `, [userId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'User not found' }, 404);
                return;
            }

            sendJson(res, {
                success: true,
                user: {
                    id: result.rows[0].id,
                    username: result.rows[0].username,
                    first_name: result.rows[0].first_name,
                    is_blocked: result.rows[0].is_blocked,
                },
                message: 'User blocked successfully',
            });
        } finally {
            client.release();
        }
    },

    // Unblock user
    'POST /api/users/:id/unblock': async (req, res, params) => {
        const userId = parseInt(params.id);

        const client = await pool.connect();
        try {
            const result = await client.query(`
                UPDATE users
                SET is_blocked = false
                WHERE id = $1
                RETURNING id, username, first_name, is_blocked
            `, [userId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'User not found' }, 404);
                return;
            }

            sendJson(res, {
                success: true,
                user: {
                    id: result.rows[0].id,
                    username: result.rows[0].username,
                    first_name: result.rows[0].first_name,
                    is_blocked: result.rows[0].is_blocked,
                },
                message: 'User unblocked successfully',
            });
        } finally {
            client.release();
        }
    },

    // Send direct message to user
    'POST /api/users/:id/message': async (req, res, params) => {
        const userId = parseInt(params.id);
        const body = await parseBody(req);
        const { message } = body;

        if (!message || message.trim().length === 0) {
            sendJson(res, { detail: 'Message is required' }, 400);
            return;
        }

        if (!TELEGRAM_BOT_TOKEN) {
            sendJson(res, { detail: 'Telegram bot token not configured' }, 500);
            return;
        }

        const client = await pool.connect();
        try {
            // Get user's telegram_id
            const userResult = await client.query(
                'SELECT id, telegram_id, username, first_name, is_blocked FROM users WHERE id = $1',
                [userId]
            );

            if (userResult.rows.length === 0) {
                sendJson(res, { detail: 'User not found' }, 404);
                return;
            }

            const user = userResult.rows[0];

            if (user.is_blocked) {
                sendJson(res, { detail: 'Cannot send message to blocked user' }, 400);
                return;
            }

            // Send message via Telegram API
            const telegramUrl = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
            const telegramResponse = await fetch(telegramUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    chat_id: user.telegram_id.toString(),
                    text: message.trim(),
                    parse_mode: 'HTML',
                }),
            });

            const telegramResult = await telegramResponse.json();

            if (!telegramResult.ok) {
                console.error('Telegram API error:', telegramResult);
                sendJson(res, {
                    detail: `Failed to send message: ${telegramResult.description || 'Unknown error'}`
                }, 500);
                return;
            }

            // Log the message in conversations table
            await client.query(`
                INSERT INTO conversations (user_id, message_type, content, metadata, created_at)
                VALUES ($1, 'admin_message', $2, $3, NOW())
            `, [userId, message.trim(), JSON.stringify({ source: 'admin_panel' })]);

            // Log to system_logs
            await client.query(`
                INSERT INTO system_logs (level, source, message, details, created_at)
                VALUES ('INFO', 'admin', $1, $2, NOW())
            `, [
                `Admin sent message to user ${user.username || user.first_name || user.telegram_id}`,
                JSON.stringify({ user_id: userId, telegram_id: user.telegram_id.toString(), message_preview: message.substring(0, 100) })
            ]);

            sendJson(res, {
                success: true,
                message: 'Message sent successfully',
                telegram_message_id: telegramResult.result?.message_id,
                user: {
                    id: user.id,
                    username: user.username,
                    first_name: user.first_name,
                },
            });
        } catch (error) {
            console.error('Send message error:', error);
            sendJson(res, { detail: `Failed to send message: ${error.message}` }, 500);
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

    // Lightweight health check (no DB call) - for container healthcheck
    'GET /health': async (req, res) => {
        sendJson(res, {
            status: 'ok',
            service: 'admin',
            timestamp: new Date().toISOString(),
        });
    },

    // System health (with DB check)
    'GET /api/system/health': async (req, res) => {
        let dbStatus = 'healthy';
        let dbDetails = {};
        try {
            const client = await pool.connect();
            await client.query('SELECT 1');

            // Get database stats
            const statsResult = await client.query(`
                SELECT
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM moments) as total_moments,
                    (SELECT pg_size_pretty(pg_database_size(current_database()))) as db_size
            `);
            dbDetails = statsResult.rows[0];
            client.release();
        } catch (e) {
            dbStatus = `error: ${e.message}`;
        }

        // Check bot status (by looking at recent activity)
        let botStatus = 'unknown';
        try {
            const client = await pool.connect();
            const recentActivity = await client.query(`
                SELECT COUNT(*) as recent FROM conversations
                WHERE created_at > NOW() - INTERVAL '1 hour'
            `);
            const scheduledCount = await client.query(`
                SELECT COUNT(*) as pending FROM scheduled_notifications
                WHERE sent = false AND scheduled_time > NOW()
            `);
            botStatus = 'running';
            dbDetails.recent_conversations = parseInt(recentActivity.rows[0].recent);
            dbDetails.pending_notifications = parseInt(scheduledCount.rows[0].pending);
            client.release();
        } catch (e) {
            botStatus = 'error';
        }

        // Check OpenAI status (we can't directly check without making API call)
        // Instead, check if API key is configured
        let openaiStatus = OPENAI_API_KEY ? 'configured' : 'not_configured';

        sendJson(res, {
            status: dbStatus === 'healthy' ? 'healthy' : 'unhealthy',
            database: dbStatus,
            database_details: dbDetails,
            bot: botStatus,
            openai: openaiStatus,
            timestamp: new Date().toISOString(),
        });
    },

    // System logs from database
    'GET /api/system/logs': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 100, 500);
        const offset = parseInt(query.offset) || 0;
        const level = query.level;
        const source = query.source;
        const dateFrom = query.date_from;
        const dateTo = query.date_to;

        const client = await pool.connect();
        try {
            let whereConditions = [];
            let params = [];
            let paramIndex = 1;

            if (level) {
                whereConditions.push(`level = $${paramIndex}`);
                params.push(level.toUpperCase());
                paramIndex++;
            }

            if (source) {
                whereConditions.push(`source ILIKE $${paramIndex}`);
                params.push(`%${source}%`);
                paramIndex++;
            }

            if (dateFrom) {
                whereConditions.push(`created_at >= $${paramIndex}`);
                params.push(dateFrom);
                paramIndex++;
            }

            if (dateTo) {
                whereConditions.push(`created_at <= $${paramIndex}`);
                params.push(dateTo + ' 23:59:59');
                paramIndex++;
            }

            const whereClause = whereConditions.length > 0 ? 'WHERE ' + whereConditions.join(' AND ') : '';

            // Get total count
            const countResult = await client.query(
                `SELECT COUNT(*) FROM system_logs ${whereClause}`,
                params
            );
            const total = parseInt(countResult.rows[0].count);

            // Get logs
            const result = await client.query(
                `SELECT id, level, source, message, details, created_at
                 FROM system_logs
                 ${whereClause}
                 ORDER BY created_at DESC
                 LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`,
                [...params, limit, offset]
            );

            // Get unique sources for filter dropdown
            const sourcesResult = await client.query(
                `SELECT DISTINCT source FROM system_logs ORDER BY source`
            );

            sendJson(res, {
                logs: result.rows.map(row => ({
                    id: row.id,
                    level: row.level,
                    source: row.source,
                    message: row.message,
                    details: row.details,
                    timestamp: row.created_at,
                })),
                total,
                sources: sourcesResult.rows.map(r => r.source),
            });
        } finally {
            client.release();
        }
    },

    // Scheduled notifications
    'GET /api/system/notifications': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const offset = parseInt(query.offset) || 0;
        const userId = query.user_id || '';
        const status = query.status || '';
        const dateFrom = query.date_from || '';
        const dateTo = query.date_to || '';

        const client = await pool.connect();
        try {
            const conditions = [];
            const params = [limit, offset];
            let paramIndex = 3;

            // User filter
            if (userId) {
                conditions.push(`n.user_id = $${paramIndex}`);
                params.push(parseInt(userId));
                paramIndex++;
            }

            // Status filter
            if (status === 'pending') {
                conditions.push('n.sent = false');
            } else if (status === 'sent') {
                conditions.push('n.sent = true');
            }

            // Date range filter
            if (dateFrom) {
                conditions.push(`n.scheduled_time >= $${paramIndex}`);
                params.push(new Date(dateFrom));
                paramIndex++;
            }
            if (dateTo) {
                const toDate = new Date(dateTo);
                toDate.setHours(23, 59, 59, 999);
                conditions.push(`n.scheduled_time <= $${paramIndex}`);
                params.push(toDate);
                paramIndex++;
            }

            const whereClause = conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : '';

            const result = await client.query(`
                SELECT
                    n.id, n.user_id, u.username, u.first_name,
                    n.scheduled_time, n.sent, n.sent_at, n.created_at
                FROM scheduled_notifications n
                JOIN users u ON n.user_id = u.id
                ${whereClause}
                ORDER BY n.scheduled_time DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Get total count with same filters
            const countParams = params.slice(2);
            const countWhereClause = conditions.length > 0
                ? 'WHERE ' + conditions.map((c, i) => c.replace(/\$\d+/g, `$${i + 1}`)).join(' AND ')
                : '';

            let countQuery = `SELECT COUNT(*) FROM scheduled_notifications n JOIN users u ON n.user_id = u.id ${whereClause}`;
            const countResult = await client.query(
                `SELECT COUNT(*) FROM scheduled_notifications n JOIN users u ON n.user_id = u.id ${whereClause.replace(/\$(\d+)/g, (_, num) => '$' + (parseInt(num) - 2))}`,
                countParams
            );

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
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Database backup - export all data as SQL dump
    'GET /api/system/backup': async (req, res) => {
        const client = await pool.connect();
        try {
            // Get list of tables to export
            const tablesResult = await client.query(`
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename NOT LIKE 'pg_%'
                ORDER BY tablename
            `);

            const tables = tablesResult.rows.map(r => r.tablename);

            let sqlDump = `-- MINDSETHAPPYBOT Database Backup\n`;
            sqlDump += `-- Generated: ${new Date().toISOString()}\n`;
            sqlDump += `-- Tables: ${tables.join(', ')}\n\n`;

            // Export data for each table
            for (const tableName of tables) {
                sqlDump += `-- Table: ${tableName}\n`;

                // Get column info
                const columnsResult = await client.query(`
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = $1 AND table_schema = 'public'
                    ORDER BY ordinal_position
                `, [tableName]);

                const columns = columnsResult.rows.map(c => c.column_name);

                // Get data
                const dataResult = await client.query(`SELECT * FROM "${tableName}"`);

                if (dataResult.rows.length > 0) {
                    sqlDump += `DELETE FROM "${tableName}";\n`;

                    for (const row of dataResult.rows) {
                        const values = columns.map(col => {
                            const val = row[col];
                            if (val === null || val === undefined) return 'NULL';
                            if (typeof val === 'boolean') return val ? 'TRUE' : 'FALSE';
                            if (typeof val === 'number') return val.toString();
                            if (val instanceof Date) return `'${val.toISOString()}'`;
                            if (Array.isArray(val)) return `ARRAY[${val.map(v => `'${String(v).replace(/'/g, "''")}'`).join(',')}]`;
                            if (typeof val === 'object') return `'${JSON.stringify(val).replace(/'/g, "''")}'`;
                            return `'${String(val).replace(/'/g, "''")}'`;
                        });

                        sqlDump += `INSERT INTO "${tableName}" ("${columns.join('","')}") VALUES (${values.join(',')});\n`;
                    }
                }
                sqlDump += `\n`;
            }

            const filename = `mindsethappybot_backup_${new Date().toISOString().split('T')[0]}.sql`;

            res.writeHead(200, {
                'Content-Type': 'application/sql',
                'Content-Disposition': `attachment; filename="${filename}"`,
            });
            res.end(sqlDump);
        } catch (error) {
            console.error('Backup error:', error);
            sendJson(res, { detail: `Backup failed: ${error.message}` }, 500);
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
                    f.admin_response, f.admin_response_at,
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
                    admin_response: row.admin_response,
                    admin_response_at: row.admin_response_at?.toISOString(),
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

    // Respond to feedback (stores response and optionally sends to user)
    'POST /api/feedback/:id/respond': async (req, res, params) => {
        const feedbackId = parseInt(params.id);
        const body = await parseBody(req);
        const { response, send_to_user } = body;

        if (!response || response.trim().length === 0) {
            sendJson(res, { detail: 'Response is required' }, 400);
            return;
        }

        const client = await pool.connect();
        try {
            // Get feedback and user info
            const feedbackResult = await client.query(`
                SELECT f.*, u.telegram_id, u.first_name, u.username
                FROM feedback f
                JOIN users u ON f.user_id = u.id
                WHERE f.id = $1
            `, [feedbackId]);

            if (feedbackResult.rows.length === 0) {
                sendJson(res, { detail: 'Feedback not found' }, 404);
                return;
            }

            const feedback = feedbackResult.rows[0];

            // Update feedback with response
            await client.query(`
                UPDATE feedback
                SET admin_response = $1,
                    admin_response_at = NOW(),
                    status = CASE WHEN status = 'new' THEN 'reviewed' ELSE status END,
                    reviewed_at = COALESCE(reviewed_at, NOW())
                WHERE id = $2
            `, [response.trim(), feedbackId]);

            // If send_to_user is true, send the response to user via Telegram
            let messageSent = false;
            let telegramError = null;
            if (send_to_user && feedback.telegram_id && TELEGRAM_BOT_TOKEN) {
                try {
                    // Format the response message
                    const messageText = `💬 <b>Ответ на ваш отзыв:</b>\n\n${response.trim()}`;

                    // Send message via Telegram API
                    const telegramUrl = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`;
                    const telegramResponse = await fetch(telegramUrl, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            chat_id: feedback.telegram_id.toString(),
                            text: messageText,
                            parse_mode: 'HTML',
                        }),
                    });

                    const telegramResult = await telegramResponse.json();

                    if (telegramResult.ok) {
                        messageSent = true;
                        // Mark response as sent
                        await client.query(`
                            UPDATE feedback
                            SET admin_response_sent = true
                            WHERE id = $1
                        `, [feedbackId]);

                        // Log the message in conversations table
                        await client.query(`
                            INSERT INTO conversations (user_id, message_type, content, metadata, created_at)
                            VALUES ($1, 'admin_feedback_response', $2, $3, NOW())
                        `, [feedback.user_id, response.trim(), JSON.stringify({
                            source: 'admin_panel',
                            feedback_id: feedbackId
                        })]);
                    } else {
                        telegramError = telegramResult.description || 'Unknown Telegram error';
                        console.error('Telegram API error sending feedback response:', telegramResult);
                    }
                } catch (error) {
                    telegramError = error.message;
                    console.error('Error sending feedback response via Telegram:', error);
                }
            }

            sendJson(res, {
                success: true,
                feedback_id: feedbackId,
                response_saved: true,
                message_sent: messageSent,
                telegram_error: telegramError,
                telegram_id: feedback.telegram_id?.toString(),
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

    // Dialogs/Conversations list
    'GET /api/dialogs': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 200);
        const offset = parseInt(query.offset) || 0;
        const userId = query.user_id;
        const messageType = query.message_type;
        const search = query.search;

        const client = await pool.connect();
        try {
            let whereClause = '1=1';
            const params = [limit, offset];
            let paramIndex = 3;

            if (userId) {
                whereClause += ` AND c.user_id = $${paramIndex}`;
                params.push(parseInt(userId));
                paramIndex++;
            }

            if (messageType) {
                whereClause += ` AND c.message_type = $${paramIndex}`;
                params.push(messageType);
                paramIndex++;
            }

            if (search) {
                whereClause += ` AND c.content ILIKE $${paramIndex}`;
                params.push(`%${search}%`);
                paramIndex++;
            }

            const result = await client.query(`
                SELECT
                    c.id, c.user_id, c.message_type, c.content,
                    c.metadata, c.created_at,
                    u.telegram_id, u.username, u.first_name
                FROM conversations c
                JOIN users u ON c.user_id = u.id
                WHERE ${whereClause}
                ORDER BY c.created_at DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Count total
            const countParams = params.slice(2);
            let countWhere = whereClause.replace(/\$(\d+)/g, (_, n) => `$${parseInt(n) - 2}`);
            const countResult = await client.query(
                `SELECT COUNT(*) FROM conversations c WHERE ${countWhere}`,
                countParams
            );

            sendJson(res, {
                dialogs: result.rows.map(row => ({
                    id: row.id,
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    message_type: row.message_type,
                    content: row.content,
                    metadata: row.metadata,
                    created_at: row.created_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Export dialogs to CSV or JSON - MUST be before /api/dialogs/user/:userId
    'GET /api/dialogs/export': async (req, res) => {
        const query = parseQuery(req.url);
        const format = query.format || 'csv'; // 'csv' or 'json'
        const userId = query.user_id ? parseInt(query.user_id) : null;
        const messageType = query.message_type || '';
        const dateFrom = query.date_from || '';
        const dateTo = query.date_to || '';

        const client = await pool.connect();
        try {
            let sqlQuery = `
                SELECT
                    c.id,
                    c.user_id,
                    u.telegram_id,
                    u.username,
                    u.first_name,
                    c.message_type,
                    c.content,
                    c.created_at
                FROM conversations c
                JOIN users u ON c.user_id = u.id
                WHERE 1=1
            `;

            const params = [];
            let paramIdx = 1;

            if (userId) {
                sqlQuery += ` AND c.user_id = $${paramIdx}`;
                params.push(userId);
                paramIdx++;
            }

            if (messageType) {
                sqlQuery += ` AND c.message_type = $${paramIdx}`;
                params.push(messageType);
                paramIdx++;
            }

            if (dateFrom) {
                sqlQuery += ` AND c.created_at >= $${paramIdx}`;
                params.push(dateFrom);
                paramIdx++;
            }

            if (dateTo) {
                sqlQuery += ` AND c.created_at <= $${paramIdx}`;
                params.push(dateTo + 'T23:59:59Z');
                paramIdx++;
            }

            sqlQuery += ' ORDER BY c.created_at DESC LIMIT 10000';

            const result = await client.query(sqlQuery, params);

            if (format === 'json') {
                // Export as JSON
                const data = result.rows.map(row => ({
                    id: row.id,
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    message_type: row.message_type,
                    content: row.content,
                    created_at: row.created_at?.toISOString(),
                }));

                const filename = `dialogs_export_${new Date().toISOString().split('T')[0]}.json`;

                res.writeHead(200, {
                    'Content-Type': 'application/json',
                    'Content-Disposition': `attachment; filename="${filename}"`,
                });
                res.end(JSON.stringify(data, null, 2));
            } else {
                // Export as CSV
                const headers = [
                    'ID', 'User ID', 'Telegram ID', 'Username', 'First Name',
                    'Message Type', 'Content', 'Created At'
                ];

                const csvRows = [headers.join(',')];

                for (const row of result.rows) {
                    const values = [
                        row.id,
                        row.user_id,
                        row.telegram_id,
                        `"${(row.username || '').replace(/"/g, '""')}"`,
                        `"${(row.first_name || '').replace(/"/g, '""')}"`,
                        row.message_type,
                        `"${(row.content || '').replace(/"/g, '""').replace(/\n/g, '\\n')}"`,
                        row.created_at?.toISOString() || ''
                    ];
                    csvRows.push(values.join(','));
                }

                const csv = csvRows.join('\n');
                const filename = `dialogs_export_${new Date().toISOString().split('T')[0]}.csv`;

                res.writeHead(200, {
                    'Content-Type': 'text/csv',
                    'Content-Disposition': `attachment; filename="${filename}"`,
                });
                res.end(csv);
            }
        } finally {
            client.release();
        }
    },

    // Get dialog for specific user
    'GET /api/dialogs/user/:userId': async (req, res, params) => {
        const userId = parseInt(params.userId);
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 100, 500);

        if (!Number.isFinite(userId)) {
            sendJson(res, { detail: 'Invalid user id' }, 400);
            return;
        }

        const client = await pool.connect();
        try {
            // Get user info
            const userResult = await client.query(`
                SELECT id, telegram_id, username, first_name, language_code
                FROM users WHERE id = $1
            `, [userId]);

            if (userResult.rows.length === 0) {
                sendJson(res, { detail: 'User not found' }, 404);
                return;
            }

            const user = userResult.rows[0];

            // Get conversations for user (chronological order for chat view)
            const dialogResult = await client.query(`
                SELECT id, message_type, content, metadata, created_at
                FROM conversations
                WHERE user_id = $1
                ORDER BY created_at ASC
                LIMIT $2
            `, [userId, limit]);

            sendJson(res, {
                user: {
                    id: user.id,
                    telegram_id: user.telegram_id?.toString(),
                    username: user.username,
                    first_name: user.first_name,
                    language_code: user.language_code,
                },
                messages: dialogResult.rows.map(row => ({
                    id: row.id,
                    message_type: row.message_type,
                    content: row.content,
                    metadata: row.metadata,
                    created_at: row.created_at?.toISOString(),
                })),
            });
        } finally {
            client.release();
        }
    },

    // All moments with filters
    'GET /api/moments': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 200);
        const offset = parseInt(query.offset) || 0;
        const userId = query.user_id;
        const dateFrom = query.date_from;
        const dateTo = query.date_to;
        const moodMin = query.mood_min ? parseFloat(query.mood_min) : null;
        const moodMax = query.mood_max ? parseFloat(query.mood_max) : null;
        const topic = query.topic;

        const client = await pool.connect();
        try {
            let whereClause = '1=1';
            const params = [limit, offset];
            let paramIndex = 3;

            if (userId) {
                whereClause += ` AND m.user_id = $${paramIndex}`;
                params.push(parseInt(userId));
                paramIndex++;
            }

            if (dateFrom) {
                whereClause += ` AND m.created_at >= $${paramIndex}`;
                params.push(new Date(dateFrom));
                paramIndex++;
            }

            if (dateTo) {
                whereClause += ` AND m.created_at <= $${paramIndex}`;
                params.push(new Date(dateTo));
                paramIndex++;
            }

            if (moodMin !== null) {
                whereClause += ` AND m.mood_score >= $${paramIndex}`;
                params.push(moodMin);
                paramIndex++;
            }

            if (moodMax !== null) {
                whereClause += ` AND m.mood_score <= $${paramIndex}`;
                params.push(moodMax);
                paramIndex++;
            }

            if (topic) {
                whereClause += ` AND $${paramIndex} = ANY(m.topics)`;
                params.push(topic);
                paramIndex++;
            }

            const result = await client.query(`
                SELECT
                    m.id, m.user_id, m.content, m.source_type,
                    m.mood_score, m.topics, m.created_at,
                    u.telegram_id, u.username, u.first_name
                FROM moments m
                JOIN users u ON m.user_id = u.id
                WHERE ${whereClause}
                ORDER BY m.created_at DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Count total
            const countParams = params.slice(2);
            let countWhere = whereClause.replace(/\$(\d+)/g, (_, n) => `$${parseInt(n) - 2}`);
            const countResult = await client.query(
                `SELECT COUNT(*) FROM moments m WHERE ${countWhere}`,
                countParams
            );

            sendJson(res, {
                moments: result.rows.map(row => ({
                    id: row.id,
                    user_id: row.user_id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    content: row.content,
                    source_type: row.source_type,
                    mood_score: row.mood_score,
                    topics: row.topics || [],
                    created_at: row.created_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Moments statistics and topics cloud
    'GET /api/moments/stats': async (req, res) => {
        const client = await pool.connect();
        try {
            // Get overall stats
            const statsResult = await client.query(`
                SELECT
                    COUNT(*) as total_moments,
                    AVG(mood_score) as avg_mood,
                    COUNT(DISTINCT user_id) as unique_users,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as moments_week,
                    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') as moments_month
                FROM moments
            `);

            // Get topics cloud (frequency of each topic)
            const topicsResult = await client.query(`
                SELECT
                    topic,
                    COUNT(*) as count
                FROM moments, unnest(topics) as topic
                WHERE topics IS NOT NULL AND array_length(topics, 1) > 0
                GROUP BY topic
                ORDER BY count DESC
                LIMIT 50
            `);

            // Get mood distribution
            const moodResult = await client.query(`
                SELECT
                    CASE
                        WHEN mood_score >= 0.8 THEN 'very_positive'
                        WHEN mood_score >= 0.6 THEN 'positive'
                        WHEN mood_score >= 0.4 THEN 'neutral'
                        WHEN mood_score >= 0.2 THEN 'negative'
                        ELSE 'very_negative'
                    END as mood_category,
                    COUNT(*) as count
                FROM moments
                WHERE mood_score IS NOT NULL
                GROUP BY mood_category
                ORDER BY mood_category
            `);

            // Get source type distribution
            const sourceResult = await client.query(`
                SELECT source_type, COUNT(*) as count
                FROM moments
                GROUP BY source_type
                ORDER BY count DESC
            `);

            // Get moments by day (last 30 days)
            const dailyResult = await client.query(`
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM moments
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            `);

            const stats = statsResult.rows[0];
            sendJson(res, {
                total_moments: parseInt(stats.total_moments),
                avg_mood: stats.avg_mood ? parseFloat(stats.avg_mood).toFixed(2) : null,
                unique_users: parseInt(stats.unique_users),
                moments_week: parseInt(stats.moments_week),
                moments_month: parseInt(stats.moments_month),
                topics_cloud: topicsResult.rows.map(row => ({
                    topic: row.topic,
                    count: parseInt(row.count),
                })),
                mood_distribution: moodResult.rows.map(row => ({
                    category: row.mood_category,
                    count: parseInt(row.count),
                })),
                source_distribution: sourceResult.rows.map(row => ({
                    source: row.source_type,
                    count: parseInt(row.count),
                })),
                daily_moments: dailyResult.rows.map(row => ({
                    date: row.date?.toISOString().split('T')[0],
                    count: parseInt(row.count),
                })),
            });
        } finally {
            client.release();
        }
    },

    // Knowledge Base list
    'GET /api/knowledge': async (req, res) => {
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
                whereClause += ` AND indexing_status = $${paramIndex}`;
                params.push(status);
                paramIndex++;
            }

            const result = await client.query(`
                SELECT
                    id, title, file_type, original_filename, category,
                    tags, chunks_count, indexing_status, indexing_error,
                    usage_count, created_at, updated_at
                FROM knowledge_base
                WHERE ${whereClause}
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Count total
            const countParams = status ? [status] : [];
            const countWhere = status ? 'indexing_status = $1' : '1=1';
            const countResult = await client.query(
                `SELECT COUNT(*) FROM knowledge_base WHERE ${countWhere}`,
                countParams
            );

            sendJson(res, {
                items: result.rows.map(row => ({
                    id: row.id,
                    title: row.title,
                    file_type: row.file_type,
                    original_filename: row.original_filename,
                    category: row.category,
                    tags: row.tags || [],
                    chunks_count: row.chunks_count || 0,
                    indexing_status: row.indexing_status,
                    indexing_error: row.indexing_error,
                    usage_count: row.usage_count || 0,
                    created_at: row.created_at?.toISOString(),
                    updated_at: row.updated_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Knowledge Base stats
    'GET /api/knowledge/stats': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    COUNT(*) as total_items,
                    COUNT(*) FILTER (WHERE indexing_status = 'indexed') as indexed,
                    COUNT(*) FILTER (WHERE indexing_status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE indexing_status = 'error') as errors,
                    COALESCE(SUM(chunks_count), 0) as total_chunks,
                    COALESCE(SUM(usage_count), 0) as total_usage
                FROM knowledge_base
            `);

            const stats = result.rows[0];
            sendJson(res, {
                total_items: parseInt(stats.total_items),
                indexed: parseInt(stats.indexed),
                pending: parseInt(stats.pending),
                errors: parseInt(stats.errors),
                total_chunks: parseInt(stats.total_chunks),
                total_usage: parseInt(stats.total_usage),
            });
        } finally {
            client.release();
        }
    },

    // Upload knowledge base item
    'POST /api/knowledge/upload': async (req, res) => {
        // Parse multipart form data
        const contentType = req.headers['content-type'] || '';
        if (!contentType.includes('multipart/form-data')) {
            sendJson(res, { detail: 'Content-Type must be multipart/form-data' }, 400);
            return;
        }

        try {
            const boundary = contentType.split('boundary=')[1];
            if (!boundary) {
                sendJson(res, { detail: 'No boundary found in Content-Type' }, 400);
                return;
            }

            const chunks = [];
            for await (const chunk of req) {
                chunks.push(chunk);
            }
            const buffer = Buffer.concat(chunks);
            const data = buffer.toString('utf-8');

            // Parse multipart data (simplified)
            const parts = data.split(`--${boundary}`).filter(p => p.trim() && p.trim() !== '--');

            let title = '';
            let category = '';
            let tags = [];
            let fileContent = '';
            let fileName = '';
            let fileType = 'text';

            for (const part of parts) {
                if (part.includes('name="title"')) {
                    title = part.split('\r\n\r\n')[1]?.trim().split('\r\n')[0] || '';
                } else if (part.includes('name="category"')) {
                    category = part.split('\r\n\r\n')[1]?.trim().split('\r\n')[0] || '';
                } else if (part.includes('name="tags"')) {
                    const tagsStr = part.split('\r\n\r\n')[1]?.trim().split('\r\n')[0] || '';
                    tags = tagsStr.split(',').map(t => t.trim()).filter(t => t);
                } else if (part.includes('name="file"')) {
                    const fileMatch = part.match(/filename="([^"]+)"/);
                    fileName = fileMatch ? fileMatch[1] : 'unknown.txt';

                    // Determine file type
                    if (fileName.endsWith('.pdf')) {
                        fileType = 'pdf';
                    } else if (fileName.endsWith('.txt')) {
                        fileType = 'text';
                    } else if (fileName.endsWith('.md')) {
                        fileType = 'markdown';
                    }

                    // Extract file content (after double CRLF)
                    const contentStart = part.indexOf('\r\n\r\n') + 4;
                    const contentEnd = part.lastIndexOf('\r\n');
                    fileContent = part.substring(contentStart, contentEnd > contentStart ? contentEnd : undefined);
                }
            }

            if (!title) {
                title = fileName || 'Untitled';
            }

            if (!fileContent) {
                sendJson(res, { detail: 'No file content provided' }, 400);
                return;
            }

            // Save to database
            const client = await pool.connect();
            try {
                const result = await client.query(`
                    INSERT INTO knowledge_base
                    (title, content, file_type, original_filename, category, tags, indexing_status)
                    VALUES ($1, $2, $3, $4, $5, $6, 'pending')
                    RETURNING id, title, file_type, original_filename, indexing_status, created_at
                `, [title, fileContent, fileType, fileName, category || null, tags.length > 0 ? tags : null]);

                const item = result.rows[0];
                sendJson(res, {
                    success: true,
                    item: {
                        id: item.id,
                        title: item.title,
                        file_type: item.file_type,
                        original_filename: item.original_filename,
                        indexing_status: item.indexing_status,
                        created_at: item.created_at?.toISOString(),
                    },
                    message: 'File uploaded successfully. Indexing will be processed.',
                });

                // Fire-and-forget: Start indexing asynchronously (don't await)
                console.log(`[Upload] Starting async indexing for item ${item.id}`);
                indexKnowledgeItem(item.id).catch(err => {
                    console.error(`[Upload] Async indexing failed for item ${item.id}:`, err.message);
                });
            } finally {
                client.release();
            }
        } catch (error) {
            console.error('Upload error:', error);
            sendJson(res, { detail: `Upload failed: ${error.message}` }, 500);
        }
    },

    // Delete knowledge base item
    'POST /api/knowledge/:id/delete': async (req, res, params) => {
        const itemId = parseInt(params.id);

        const client = await pool.connect();
        try {
            // Delete chunks first
            await client.query('DELETE FROM knowledge_chunks WHERE knowledge_base_id = $1', [itemId]);

            // Delete knowledge base item
            const result = await client.query(
                'DELETE FROM knowledge_base WHERE id = $1 RETURNING id, title',
                [itemId]
            );

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Item not found' }, 404);
                return;
            }

            sendJson(res, {
                success: true,
                message: `Deleted "${result.rows[0].title}"`,
            });
        } finally {
            client.release();
        }
    },

    // Reindex knowledge base item
    'POST /api/knowledge/:id/reindex': async (req, res, params) => {
        const itemId = parseInt(params.id);

        const client = await pool.connect();
        try {
            // Reset status to pending
            const result = await client.query(`
                UPDATE knowledge_base
                SET indexing_status = 'pending', indexing_error = NULL, updated_at = NOW()
                WHERE id = $1
                RETURNING id, title, indexing_status
            `, [itemId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Item not found' }, 404);
                return;
            }

            // Delete existing chunks
            await client.query('DELETE FROM knowledge_chunks WHERE knowledge_base_id = $1', [itemId]);

            sendJson(res, {
                success: true,
                message: `Reindexing scheduled for "${result.rows[0].title}"`,
                item: result.rows[0],
            });

            // Fire-and-forget: Start indexing asynchronously (don't await)
            console.log(`[Reindex] Starting async indexing for item ${itemId}`);
            indexKnowledgeItem(itemId).catch(err => {
                console.error(`[Reindex] Async indexing failed for item ${itemId}:`, err.message);
            });
        } finally {
            client.release();
        }
    },

    // Message Templates list
    'GET /api/templates': async (req, res) => {
        const query = parseQuery(req.url);
        const limit = Math.min(parseInt(query.limit) || 50, 100);
        const offset = parseInt(query.offset) || 0;
        const language = query.language;
        const category = query.category;

        const client = await pool.connect();
        try {
            let whereClause = '1=1';
            const params = [limit, offset];
            let paramIndex = 3;

            if (language) {
                whereClause += ` AND language_code = $${paramIndex}`;
                params.push(language);
                paramIndex++;
            }

            if (category) {
                whereClause += ` AND category = $${paramIndex}`;
                params.push(category);
                paramIndex++;
            }

            const result = await client.query(`
                SELECT id, template_text, language_code, formal, category, is_active, created_at, updated_at
                FROM question_templates
                WHERE ${whereClause}
                ORDER BY category, created_at DESC
                LIMIT $1 OFFSET $2
            `, params);

            // Count total
            const countParams = [];
            let countWhere = '1=1';
            let countParamIdx = 1;
            if (language) {
                countWhere += ` AND language_code = $${countParamIdx}`;
                countParams.push(language);
                countParamIdx++;
            }
            if (category) {
                countWhere += ` AND category = $${countParamIdx}`;
                countParams.push(category);
            }
            const countResult = await client.query(
                `SELECT COUNT(*) FROM question_templates WHERE ${countWhere}`,
                countParams
            );

            sendJson(res, {
                templates: result.rows.map(row => ({
                    id: row.id,
                    template_text: row.template_text,
                    language_code: row.language_code,
                    formal: row.formal,
                    category: row.category,
                    is_active: row.is_active,
                    created_at: row.created_at?.toISOString(),
                    updated_at: row.updated_at?.toISOString(),
                })),
                total: parseInt(countResult.rows[0].count),
            });
        } finally {
            client.release();
        }
    },

    // Get template categories
    'GET /api/templates/categories': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT DISTINCT category, COUNT(*) as count
                FROM question_templates
                GROUP BY category
                ORDER BY category
            `);

            sendJson(res, {
                categories: result.rows.map(row => ({
                    name: row.category,
                    count: parseInt(row.count),
                })),
            });
        } finally {
            client.release();
        }
    },

    // Create template
    'POST /api/templates': async (req, res) => {
        const body = await parseBody(req);
        const { template_text, language_code, formal, category, is_active } = body;

        if (!template_text) {
            sendJson(res, { detail: 'Template text is required' }, 400);
            return;
        }

        const client = await pool.connect();
        try {
            const result = await client.query(`
                INSERT INTO question_templates (template_text, language_code, formal, category, is_active)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id, template_text, language_code, formal, category, is_active, created_at
            `, [
                template_text,
                language_code || 'ru',
                formal === true,  // Default to informal (false) if not specified
                category || 'general',
                is_active !== false,
            ]);

            sendJson(res, {
                success: true,
                template: result.rows[0],
            });
        } finally {
            client.release();
        }
    },

    // Get single template
    'GET /api/templates/:id': async (req, res, params) => {
        const templateId = parseInt(params.id);

        const client = await pool.connect();
        try {
            const result = await client.query(
                'SELECT * FROM question_templates WHERE id = $1',
                [templateId]
            );

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Template not found' }, 404);
                return;
            }

            const row = result.rows[0];
            sendJson(res, {
                id: row.id,
                template_text: row.template_text,
                language_code: row.language_code,
                formal: row.formal,
                category: row.category,
                is_active: row.is_active,
                created_at: row.created_at?.toISOString(),
                updated_at: row.updated_at?.toISOString(),
            });
        } finally {
            client.release();
        }
    },

    // Update template
    'POST /api/templates/:id/update': async (req, res, params) => {
        const templateId = parseInt(params.id);
        const body = await parseBody(req);
        const { template_text, language_code, formal, category, is_active } = body;

        const client = await pool.connect();
        try {
            const updates = [];
            const values = [];
            let paramIndex = 1;

            if (template_text !== undefined) {
                updates.push(`template_text = $${paramIndex}`);
                values.push(template_text);
                paramIndex++;
            }
            if (language_code !== undefined) {
                updates.push(`language_code = $${paramIndex}`);
                values.push(language_code);
                paramIndex++;
            }
            if (formal !== undefined) {
                updates.push(`formal = $${paramIndex}`);
                values.push(formal);
                paramIndex++;
            }
            if (category !== undefined) {
                updates.push(`category = $${paramIndex}`);
                values.push(category);
                paramIndex++;
            }
            if (is_active !== undefined) {
                updates.push(`is_active = $${paramIndex}`);
                values.push(is_active);
                paramIndex++;
            }

            if (updates.length === 0) {
                sendJson(res, { detail: 'No fields to update' }, 400);
                return;
            }

            updates.push(`updated_at = NOW()`);
            values.push(templateId);

            const result = await client.query(`
                UPDATE question_templates
                SET ${updates.join(', ')}
                WHERE id = $${paramIndex}
                RETURNING id, template_text, language_code, formal, category, is_active, updated_at
            `, values);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Template not found' }, 404);
                return;
            }

            sendJson(res, {
                success: true,
                template: result.rows[0],
            });
        } finally {
            client.release();
        }
    },

    // Delete template
    'POST /api/templates/:id/delete': async (req, res, params) => {
        const templateId = parseInt(params.id);

        const client = await pool.connect();
        try {
            const result = await client.query(
                'DELETE FROM question_templates WHERE id = $1 RETURNING id, template_text',
                [templateId]
            );

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Template not found' }, 404);
                return;
            }

            sendJson(res, {
                success: true,
                message: 'Template deleted',
            });
        } finally {
            client.release();
        }
    },

    // Analytics - Funnel data
    'GET /api/analytics/funnel': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    COUNT(*) as total_users,
                    COUNT(*) FILTER (WHERE onboarding_completed = true) as completed_onboarding,
                    COUNT(*) FILTER (WHERE id IN (SELECT DISTINCT user_id FROM moments)) as has_moments,
                    COUNT(*) FILTER (WHERE id IN (
                        SELECT user_id FROM moments GROUP BY user_id HAVING COUNT(*) >= 5
                    )) as regular_users
                FROM users
            `);

            const stats = result.rows[0];
            sendJson(res, {
                stages: [
                    { name: 'Registered', count: parseInt(stats.total_users), percentage: 100 },
                    {
                        name: 'Completed Onboarding',
                        count: parseInt(stats.completed_onboarding),
                        percentage: stats.total_users > 0 ? Math.round(stats.completed_onboarding / stats.total_users * 100) : 0
                    },
                    {
                        name: 'First Moment',
                        count: parseInt(stats.has_moments),
                        percentage: stats.total_users > 0 ? Math.round(stats.has_moments / stats.total_users * 100) : 0
                    },
                    {
                        name: 'Regular Use (5+ moments)',
                        count: parseInt(stats.regular_users),
                        percentage: stats.total_users > 0 ? Math.round(stats.regular_users / stats.total_users * 100) : 0
                    },
                ],
            });
        } finally {
            client.release();
        }
    },

    // Analytics - Retention by cohorts
    'GET /api/analytics/retention': async (req, res) => {
        const client = await pool.connect();
        try {
            // Get weekly cohorts and their retention
            const result = await client.query(`
                WITH cohorts AS (
                    SELECT
                        id as user_id,
                        DATE_TRUNC('week', created_at) as cohort_week
                    FROM users
                    WHERE created_at >= NOW() - INTERVAL '8 weeks'
                ),
                activity AS (
                    SELECT
                        user_id,
                        DATE_TRUNC('week', created_at) as activity_week
                    FROM moments
                    WHERE created_at >= NOW() - INTERVAL '8 weeks'
                )
                SELECT
                    c.cohort_week,
                    COUNT(DISTINCT c.user_id) as cohort_size,
                    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week THEN a.user_id END) as week_0,
                    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '1 week' THEN a.user_id END) as week_1,
                    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '2 weeks' THEN a.user_id END) as week_2,
                    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '3 weeks' THEN a.user_id END) as week_3,
                    COUNT(DISTINCT CASE WHEN a.activity_week = c.cohort_week + INTERVAL '4 weeks' THEN a.user_id END) as week_4
                FROM cohorts c
                LEFT JOIN activity a ON c.user_id = a.user_id
                GROUP BY c.cohort_week
                ORDER BY c.cohort_week DESC
                LIMIT 8
            `);

            sendJson(res, {
                cohorts: result.rows.map(row => ({
                    cohort_week: row.cohort_week?.toISOString().split('T')[0],
                    users: parseInt(row.cohort_size),
                    weeks: [
                        { week: 1, retention: row.cohort_size > 0 ? Math.round(row.week_1 / row.cohort_size * 100) : 0 },
                        { week: 2, retention: row.cohort_size > 0 ? Math.round(row.week_2 / row.cohort_size * 100) : 0 },
                        { week: 3, retention: row.cohort_size > 0 ? Math.round(row.week_3 / row.cohort_size * 100) : 0 },
                        { week: 4, retention: row.cohort_size > 0 ? Math.round(row.week_4 / row.cohort_size * 100) : 0 },
                    ],
                })),
            });
        } finally {
            client.release();
        }
    },

    // Analytics - Activity heatmap (hour x day of week)
    'GET /api/analytics/heatmap': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    EXTRACT(DOW FROM created_at) as day_of_week,
                    EXTRACT(HOUR FROM created_at) as hour,
                    COUNT(*) as count
                FROM moments
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY EXTRACT(DOW FROM created_at), EXTRACT(HOUR FROM created_at)
                ORDER BY day_of_week, hour
            `);

            // Create a 7x24 matrix
            const heatmap = Array(7).fill(null).map(() => Array(24).fill(0));

            for (const row of result.rows) {
                const dow = parseInt(row.day_of_week);
                const hour = parseInt(row.hour);
                heatmap[dow][hour] = parseInt(row.count);
            }

            // Convert Sunday-first (PostgreSQL) to Monday-first for display
            // PostgreSQL DOW: 0=Sun, 1=Mon, ..., 6=Sat
            // We want: 0=Mon, 1=Tue, ..., 6=Sun
            const mondayFirstHeatmap = [
                heatmap[1], // Mon
                heatmap[2], // Tue
                heatmap[3], // Wed
                heatmap[4], // Thu
                heatmap[5], // Fri
                heatmap[6], // Sat
                heatmap[0], // Sun
            ];

            sendJson(res, {
                matrix: mondayFirstHeatmap,
                days: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                hours: Array.from({ length: 24 }, (_, i) => `${i}:00`),
            });
        } finally {
            client.release();
        }
    },

    // Analytics - Language distribution
    'GET /api/analytics/languages': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    COALESCE(language_code, 'unknown') as language,
                    COUNT(*) as count
                FROM users
                GROUP BY language_code
                ORDER BY count DESC
            `);

            const total = result.rows.reduce((sum, r) => sum + parseInt(r.count), 0);

            sendJson(res, {
                languages: result.rows.map(row => ({
                    language_code: row.language,
                    count: parseInt(row.count),
                    percentage: total > 0 ? Math.round(parseInt(row.count) / total * 100) : 0,
                })),
            });
        } finally {
            client.release();
        }
    },

    // Analytics - Overview stats
    'GET /api/analytics/overview': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT
                    (SELECT COUNT(*) FROM users) as total_users,
                    (SELECT COUNT(*) FROM users WHERE created_at >= NOW() - INTERVAL '7 days') as new_users_week,
                    (SELECT COUNT(*) FROM moments) as total_moments,
                    (SELECT COUNT(*) FROM moments WHERE created_at >= NOW() - INTERVAL '7 days') as moments_week,
                    (SELECT COALESCE(AVG(mood_score), 0) FROM moments WHERE mood_score IS NOT NULL) as avg_mood,
                    (SELECT COUNT(*) FROM users WHERE last_active_at >= NOW() - INTERVAL '7 days') as active_users_week,
                    (SELECT COUNT(*) FROM users WHERE notifications_enabled = true) as notifications_enabled
            `);

            const stats = result.rows[0];
            // Also get onboarded users count
            const onboardedResult = await client.query('SELECT COUNT(*) FROM users WHERE onboarding_completed = true');
            const onboardedUsers = parseInt(onboardedResult.rows[0].count);

            sendJson(res, {
                total_users: parseInt(stats.total_users),
                new_users_week: parseInt(stats.new_users_week),
                total_moments: parseInt(stats.total_moments),
                moments_week: parseInt(stats.moments_week),
                avg_mood: parseFloat(stats.avg_mood).toFixed(2),
                active_users_7d: parseInt(stats.active_users_week),
                onboarded_users: onboardedUsers,
                notifications_enabled: parseInt(stats.notifications_enabled),
            });
        } finally {
            client.release();
        }
    },

    // Analytics - Users added per day (registration chart)
    'GET /api/analytics/users-per-day': async (req, res) => {
        const query = parseQuery(req.url);
        const days = Math.min(Math.max(parseInt(query.days) || 30, 7), 90);

        const client = await pool.connect();
        try {
            // Get user registrations per day for the specified period
            const result = await client.query(`
                WITH date_series AS (
                    SELECT generate_series(
                        (NOW() - INTERVAL '${days} days')::date,
                        NOW()::date,
                        '1 day'::interval
                    )::date as date
                )
                SELECT
                    ds.date,
                    COALESCE(COUNT(u.id), 0) as count
                FROM date_series ds
                LEFT JOIN users u ON DATE(u.created_at) = ds.date
                GROUP BY ds.date
                ORDER BY ds.date ASC
            `);

            sendJson(res, {
                period_days: days,
                data: result.rows.map(row => ({
                    date: row.date.toISOString().split('T')[0],
                    count: parseInt(row.count),
                })),
            });
        } finally {
            client.release();
        }
    },

    // Get single knowledge base item detail
    'GET /api/knowledge/:id': async (req, res, params) => {
        const itemId = parseInt(params.id);

        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT * FROM knowledge_base WHERE id = $1
            `, [itemId]);

            if (result.rows.length === 0) {
                sendJson(res, { detail: 'Item not found' }, 404);
                return;
            }

            const row = result.rows[0];
            sendJson(res, {
                id: row.id,
                title: row.title,
                content: row.content,
                file_type: row.file_type,
                original_filename: row.original_filename,
                category: row.category,
                tags: row.tags || [],
                chunks_count: row.chunks_count || 0,
                indexing_status: row.indexing_status,
                indexing_error: row.indexing_error,
                usage_count: row.usage_count || 0,
                created_at: row.created_at?.toISOString(),
                updated_at: row.updated_at?.toISOString(),
            });
        } finally {
            client.release();
        }
    },

    // Export moments to CSV
    'GET /api/moments/export': async (req, res) => {
        const query = parseQuery(req.url);
        const userId = query.user_id;
        const dateFrom = query.date_from;
        const dateTo = query.date_to;

        const client = await pool.connect();
        try {
            let whereClause = '1=1';
            const params = [];
            let paramIndex = 1;

            if (userId) {
                whereClause += ` AND m.user_id = $${paramIndex}`;
                params.push(parseInt(userId));
                paramIndex++;
            }

            if (dateFrom) {
                whereClause += ` AND m.created_at >= $${paramIndex}`;
                params.push(new Date(dateFrom));
                paramIndex++;
            }

            if (dateTo) {
                whereClause += ` AND m.created_at <= $${paramIndex}`;
                params.push(new Date(dateTo));
                paramIndex++;
            }

            const result = await client.query(`
                SELECT
                    m.id, m.user_id, u.username, u.first_name,
                    m.content, m.source_type, m.mood_score,
                    array_to_string(m.topics, '; ') as topics,
                    m.created_at
                FROM moments m
                JOIN users u ON m.user_id = u.id
                WHERE ${whereClause}
                ORDER BY m.created_at DESC
                LIMIT 10000
            `, params);

            // Generate CSV
            const headers = ['ID', 'User ID', 'Username', 'Name', 'Content', 'Source', 'Mood Score', 'Topics', 'Created At'];
            const csvRows = [headers.join(',')];

            for (const row of result.rows) {
                const values = [
                    row.id,
                    row.user_id,
                    `"${(row.username || '').replace(/"/g, '""')}"`,
                    `"${(row.first_name || '').replace(/"/g, '""')}"`,
                    `"${(row.content || '').replace(/"/g, '""').replace(/\n/g, ' ')}"`,
                    row.source_type || '',
                    row.mood_score || '',
                    `"${(row.topics || '').replace(/"/g, '""')}"`,
                    row.created_at?.toISOString() || '',
                ];
                csvRows.push(values.join(','));
            }

            const csv = csvRows.join('\n');

            res.writeHead(200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': `attachment; filename="moments_export_${new Date().toISOString().split('T')[0]}.csv"`,
                'Access-Control-Allow-Origin': '*',
            });
            res.end(csv);
        } finally {
            client.release();
        }
    },

    // Get unique users with dialogs (for filter dropdown)
    'GET /api/dialogs/users': async (req, res) => {
        const client = await pool.connect();
        try {
            const result = await client.query(`
                SELECT DISTINCT ON (u.id)
                    u.id, u.telegram_id, u.username, u.first_name,
                    cnt.message_count,
                    c.created_at as last_message_at,
                    c.content as last_message_content,
                    c.message_type as last_message_type
                FROM users u
                INNER JOIN (
                    SELECT user_id, COUNT(*) as message_count
                    FROM conversations
                    GROUP BY user_id
                ) cnt ON cnt.user_id = u.id
                INNER JOIN conversations c ON u.id = c.user_id
                ORDER BY u.id, c.created_at DESC
                LIMIT 100
            `);

            sendJson(res, {
                users: result.rows.map(row => ({
                    id: row.id,
                    telegram_id: row.telegram_id?.toString(),
                    username: row.username,
                    first_name: row.first_name,
                    message_count: parseInt(row.message_count),
                    last_message_at: row.last_message_at?.toISOString(),
                    last_message_content: row.last_message_content,
                    last_message_type: row.last_message_type,
                })),
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
        if (req.method === 'GET' && (req.url === '/' || req.url.startsWith('/static/') || req.url === '/favicon.ico')) {
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

// Start server - bind to 0.0.0.0 for Docker/Dokploy compatibility
server.listen(PORT, '0.0.0.0', () => {
    console.log(`Admin panel running at http://0.0.0.0:${PORT}`);
    console.log(`Database: ${DATABASE_URL}`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('Shutting down...');
    await pool.end();
    server.close();
    process.exit(0);
});
