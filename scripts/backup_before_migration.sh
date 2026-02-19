#!/bin/bash
# Backup script before TIMESTAMPTZ migration
# Run this BEFORE applying the migration!

set -e  # Exit on error

# Configuration
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB:-mindsethappybot}"
DB_USER="${POSTGRES_USER:-postgres}"
BACKUP_DIR="./backups"

# Create backup directory
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========================================="
echo "DATABASE BACKUP BEFORE TIMESTAMPTZ MIGRATION"
echo "========================================="
echo "Database: $DB_NAME"
echo "Timestamp: $TIMESTAMP"
echo ""

# 1. Full database backup
echo "1. Creating full database backup..."
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    --verbose \
    --no-owner \
    --no-acl \
    > "$BACKUP_DIR/full_backup_${TIMESTAMP}.sql"

echo "   ✓ Full backup saved to: $BACKUP_DIR/full_backup_${TIMESTAMP}.sql"

# 2. Backup only tables with timestamps
echo ""
echo "2. Creating timestamp tables backup..."
PGPASSWORD=$POSTGRES_PASSWORD pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    --verbose \
    --no-owner \
    --no-acl \
    -t users \
    -t moments \
    -t conversations \
    -t conversation_memories \
    -t user_stats \
    -t feedback \
    -t social_profiles \
    -t api_usage \
    -t system_logs \
    -t prompt_templates \
    -t scheduled_notifications \
    > "$BACKUP_DIR/timestamp_tables_${TIMESTAMP}.sql"

echo "   ✓ Timestamp tables backup saved to: $BACKUP_DIR/timestamp_tables_${TIMESTAMP}.sql"

# 3. Create data snapshot for verification
echo ""
echo "3. Creating data verification snapshot..."
PGPASSWORD=$POSTGRES_PASSWORD psql \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    -c "COPY (
        SELECT
            'users' as table_name,
            count(*) as row_count,
            min(created_at) as min_timestamp,
            max(created_at) as max_timestamp
        FROM users
        UNION ALL
        SELECT
            'moments' as table_name,
            count(*) as row_count,
            min(created_at) as min_timestamp,
            max(created_at) as max_timestamp
        FROM moments
        UNION ALL
        SELECT
            'conversations' as table_name,
            count(*) as row_count,
            min(created_at) as min_timestamp,
            max(created_at) as max_timestamp
        FROM conversations
    ) TO STDOUT WITH CSV HEADER" > "$BACKUP_DIR/data_snapshot_${TIMESTAMP}.csv"

echo "   ✓ Data snapshot saved to: $BACKUP_DIR/data_snapshot_${TIMESTAMP}.csv"

# 4. Compress backups
echo ""
echo "4. Compressing backups..."
gzip "$BACKUP_DIR/full_backup_${TIMESTAMP}.sql"
gzip "$BACKUP_DIR/timestamp_tables_${TIMESTAMP}.sql"

echo "   ✓ Backups compressed"

# 5. Summary
echo ""
echo "========================================="
echo "BACKUP COMPLETE!"
echo "========================================="
echo "Files created:"
echo "  - $BACKUP_DIR/full_backup_${TIMESTAMP}.sql.gz"
echo "  - $BACKUP_DIR/timestamp_tables_${TIMESTAMP}.sql.gz"
echo "  - $BACKUP_DIR/data_snapshot_${TIMESTAMP}.csv"
echo ""
echo "To restore if needed:"
echo "  gunzip < $BACKUP_DIR/full_backup_${TIMESTAMP}.sql.gz | psql -h $DB_HOST -U $DB_USER -d $DB_NAME"
echo ""