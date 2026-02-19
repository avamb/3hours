/**
 * MINDSETHAPPYBOT Admin Panel - Attribution Routes
 * API endpoints for tracking user acquisition attribution from /start deep links
 */

export function createAttributionRoutes(pool, sendJson, parseBody) {
    return {
        'GET /api/attribution/stats': async (req, res) => {
            const client = await pool.connect();
            try {
                // Overall attribution stats
                const result = await client.query(`
                    SELECT
                        COUNT(DISTINCT id) as total_starts,
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(DISTINCT source) as unique_sources,
                        COUNT(DISTINCT campaign) FILTER (WHERE campaign IS NOT NULL) as unique_campaigns,
                        COUNT(*) FILTER (WHERE source != 'unknown') as attributed_starts,
                        COUNT(*) FILTER (WHERE source = 'unknown') as unattributed_starts
                    FROM start_events
                `);
                sendJson(res, result.rows[0]);
            } finally {
                client.release();
            }
        },

        'GET /api/attribution/by-source': async (req, res) => {
            const client = await pool.connect();
            try {
                const result = await client.query(`
                    SELECT
                        source,
                        COUNT(*) as total_starts,
                        COUNT(DISTINCT user_id) as unique_users,
                        MIN(created_at) as first_start,
                        MAX(created_at) as last_start
                    FROM start_events
                    GROUP BY source
                    ORDER BY total_starts DESC
                    LIMIT 50
                `);
                sendJson(res, result.rows);
            } finally {
                client.release();
            }
        },

        'GET /api/attribution/by-campaign': async (req, res) => {
            const client = await pool.connect();
            try {
                const result = await client.query(`
                    SELECT
                        source,
                        campaign,
                        COUNT(*) as total_starts,
                        COUNT(DISTINCT user_id) as unique_users,
                        MIN(created_at) as first_start,
                        MAX(created_at) as last_start
                    FROM start_events
                    WHERE campaign IS NOT NULL
                    GROUP BY source, campaign
                    ORDER BY total_starts DESC
                    LIMIT 100
                `);
                sendJson(res, result.rows);
            } finally {
                client.release();
            }
        },

        'GET /api/attribution/conversions': async (req, res) => {
            const client = await pool.connect();
            try {
                // Users who completed onboarding by source
                const result = await client.query(`
                    SELECT
                        COALESCE(u.first_source, 'unknown') as source,
                        COUNT(*) as total_users,
                        COUNT(*) FILTER (WHERE u.onboarding_completed = true) as onboarded_users,
                        ROUND(100.0 * COUNT(*) FILTER (WHERE u.onboarding_completed = true) / NULLIF(COUNT(*), 0), 1) as onboarding_rate
                    FROM users u
                    GROUP BY COALESCE(u.first_source, 'unknown')
                    ORDER BY total_users DESC
                    LIMIT 50
                `);
                sendJson(res, result.rows);
            } finally {
                client.release();
            }
        },

        'GET /api/attribution/daily': async (req, res) => {
            const client = await pool.connect();
            try {
                const result = await client.query(`
                    SELECT
                        DATE(created_at) as date,
                        source,
                        COUNT(*) as starts,
                        COUNT(DISTINCT user_id) as unique_users
                    FROM start_events
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    GROUP BY DATE(created_at), source
                    ORDER BY date DESC, starts DESC
                `);
                sendJson(res, result.rows);
            } finally {
                client.release();
            }
        },

        'GET /api/attribution/recent': async (req, res) => {
            const client = await pool.connect();
            try {
                const result = await client.query(`
                    SELECT
                        se.id,
                        se.telegram_id,
                        se.source,
                        se.campaign,
                        se.raw_payload,
                        se.created_at,
                        u.username,
                        u.first_name
                    FROM start_events se
                    LEFT JOIN users u ON se.user_id = u.id
                    ORDER BY se.created_at DESC
                    LIMIT 100
                `);
                sendJson(res, result.rows);
            } finally {
                client.release();
            }
        },
    };
}
