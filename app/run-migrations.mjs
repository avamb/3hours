import pg from 'pg';

const client = new pg.Client({
    host: 'localhost',
    port: 5432,
    database: 'mindsethappybot',
    user: 'postgres',
    password: 'postgres'
});

async function runMigrations() {
    try {
        await client.connect();
        console.log('Connected to mindsethappybot database');

        // Try to create pgvector extension (may not be available locally)
        console.log('Creating pgvector extension...');
        let hasVector = false;
        try {
            await client.query('CREATE EXTENSION IF NOT EXISTS vector');
            hasVector = true;
            console.log('pgvector extension created');
        } catch (e) {
            console.log('pgvector extension not available, will use BYTEA for embeddings');
        }

        // Create alembic_version table
        await client.query(`
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL
            )
        `);

        // Check if tables already exist
        const tablesCheck = await client.query(`
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'users'
        `);

        if (tablesCheck.rows.length > 0) {
            console.log('Tables already exist, skipping creation');
            await client.end();
            return;
        }

        const embeddingType = hasVector ? 'vector(1536)' : 'BYTEA';

        // Migration 0001: Initial schema
        console.log('Running migration 0001: Initial schema...');

        // Create users table
        await client.query(`
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT NOT NULL UNIQUE,
                username VARCHAR(255),
                first_name VARCHAR(255),
                language_code VARCHAR(10) DEFAULT 'ru' NOT NULL,
                formal_address BOOLEAN DEFAULT false NOT NULL,
                active_hours_start TIME DEFAULT '09:00' NOT NULL,
                active_hours_end TIME DEFAULT '21:00' NOT NULL,
                notification_interval_hours INTEGER DEFAULT 3 NOT NULL,
                notifications_enabled BOOLEAN DEFAULT true NOT NULL,
                timezone VARCHAR(50) DEFAULT 'UTC' NOT NULL,
                created_at TIMESTAMP DEFAULT now() NOT NULL,
                updated_at TIMESTAMP DEFAULT now() NOT NULL,
                last_active_at TIMESTAMP,
                onboarding_completed BOOLEAN DEFAULT false NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_users_telegram_id ON users (telegram_id)');

        // Create moments table
        await client.query(`
            CREATE TABLE moments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                source_type VARCHAR(20) DEFAULT 'text' NOT NULL,
                original_voice_file_id VARCHAR(255),
                embedding ${embeddingType},
                mood_score FLOAT,
                topics TEXT[],
                created_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_moments_user_id ON moments (user_id)');
        await client.query('CREATE INDEX idx_moments_created_at ON moments (created_at)');

        // Create conversations table
        await client.query(`
            CREATE TABLE conversations (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                message_type VARCHAR(50) NOT NULL,
                content TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_conversations_user_id ON conversations (user_id)');

        // Create user_stats table
        await client.query(`
            CREATE TABLE user_stats (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                current_streak INTEGER DEFAULT 0 NOT NULL,
                longest_streak INTEGER DEFAULT 0 NOT NULL,
                total_moments INTEGER DEFAULT 0 NOT NULL,
                total_questions_sent INTEGER DEFAULT 0 NOT NULL,
                total_questions_answered INTEGER DEFAULT 0 NOT NULL,
                last_response_date DATE,
                updated_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);

        // Create scheduled_notifications table
        await client.query(`
            CREATE TABLE scheduled_notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                scheduled_time TIMESTAMP NOT NULL,
                sent BOOLEAN DEFAULT false NOT NULL,
                sent_at TIMESTAMP,
                question_template_id INTEGER,
                created_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_scheduled_notifications_time ON scheduled_notifications (scheduled_time, sent)');

        // Create question_templates table (with is_active and updated_at columns)
        await client.query(`
            CREATE TABLE question_templates (
                id SERIAL PRIMARY KEY,
                language_code VARCHAR(10) NOT NULL,
                formal BOOLEAN NOT NULL,
                template_text TEXT NOT NULL,
                category VARCHAR(50) DEFAULT 'main' NOT NULL,
                is_active BOOLEAN DEFAULT true NOT NULL,
                created_at TIMESTAMP DEFAULT now() NOT NULL,
                updated_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_question_templates_language ON question_templates (language_code)');

        // Migration 0002: Feedback table
        console.log('Running migration 0002: Feedback table...');
        await client.query(`
            CREATE TABLE feedback (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                content TEXT NOT NULL,
                category VARCHAR(50),
                status VARCHAR(20) DEFAULT 'new' NOT NULL,
                admin_notes TEXT,
                reviewed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_feedback_user_id ON feedback (user_id)');
        await client.query('CREATE INDEX idx_feedback_status ON feedback (status)');
        await client.query('CREATE INDEX idx_feedback_created_at ON feedback (created_at)');

        // Migration 0003: User summary fields
        console.log('Running migration 0003: User summary fields...');
        await client.query('ALTER TABLE users ADD COLUMN last_name VARCHAR(255)');
        await client.query('ALTER TABLE users ADD COLUMN detected_language VARCHAR(10)');
        await client.query('ALTER TABLE users ADD COLUMN daily_summary_enabled BOOLEAN DEFAULT true NOT NULL');
        await client.query('ALTER TABLE users ADD COLUMN weekly_summary_enabled BOOLEAN DEFAULT true NOT NULL');
        await client.query('ALTER TABLE users ADD COLUMN monthly_summary_enabled BOOLEAN DEFAULT true NOT NULL');
        await client.query('ALTER TABLE users ADD COLUMN is_blocked BOOLEAN DEFAULT false NOT NULL');

        // Migration 0004: Social profiles table
        console.log('Running migration 0004: Social profiles table...');
        await client.query(`
            CREATE TABLE social_profiles (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                instagram_url VARCHAR(500),
                facebook_url VARCHAR(500),
                twitter_url VARCHAR(500),
                linkedin_url VARCHAR(500),
                vk_url VARCHAR(500),
                telegram_channel_url VARCHAR(500),
                youtube_url VARCHAR(500),
                tiktok_url VARCHAR(500),
                bio_text TEXT,
                parsed_bio TEXT,
                interests TEXT[],
                communication_style VARCHAR(50),
                interests_embedding ${embeddingType},
                last_parsed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT now() NOT NULL,
                updated_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_social_profiles_user_id ON social_profiles (user_id)');

        // Migration 0005: Knowledge base tables
        console.log('Running migration 0005: Knowledge base tables...');
        await client.query(`
            CREATE TABLE knowledge_base (
                id SERIAL PRIMARY KEY,
                title VARCHAR(500) NOT NULL,
                content TEXT NOT NULL,
                file_type VARCHAR(20),
                original_filename VARCHAR(500),
                tags TEXT[],
                category VARCHAR(100),
                chunks_count INTEGER DEFAULT 0 NOT NULL,
                indexing_status VARCHAR(20) DEFAULT 'pending' NOT NULL,
                indexing_error TEXT,
                usage_count INTEGER DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT now() NOT NULL,
                updated_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_knowledge_base_category ON knowledge_base (category)');
        await client.query('CREATE INDEX idx_knowledge_base_indexing_status ON knowledge_base (indexing_status)');

        await client.query(`
            CREATE TABLE knowledge_chunks (
                id SERIAL PRIMARY KEY,
                knowledge_base_id INTEGER NOT NULL REFERENCES knowledge_base(id) ON DELETE CASCADE,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                embedding ${embeddingType},
                created_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_knowledge_chunks_kb_id ON knowledge_chunks (knowledge_base_id)');

        // Migration 0006: System logs table
        console.log('Running migration 0006: System logs table...');
        await client.query(`
            CREATE TABLE system_logs (
                id SERIAL PRIMARY KEY,
                level VARCHAR(20) NOT NULL,
                source VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                details JSONB,
                created_at TIMESTAMP DEFAULT now() NOT NULL
            )
        `);
        await client.query('CREATE INDEX idx_system_logs_level ON system_logs (level)');
        await client.query('CREATE INDEX idx_system_logs_source ON system_logs (source)');
        await client.query('CREATE INDEX idx_system_logs_created_at ON system_logs (created_at)');

        // Set alembic version
        await client.query("DELETE FROM alembic_version");
        await client.query("INSERT INTO alembic_version (version_num) VALUES ('0006')");

        console.log('All migrations completed successfully!');
    } catch (err) {
        console.error('Error:', err.message);
        console.error(err.stack);
    } finally {
        await client.end();
    }
}

runMigrations();
