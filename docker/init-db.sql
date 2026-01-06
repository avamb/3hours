-- Initialize PostgreSQL database with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- This file is executed when the PostgreSQL container starts for the first time
-- The actual tables will be created by Alembic migrations
