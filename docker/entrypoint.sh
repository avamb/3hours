#!/bin/bash
# MINDSETHAPPYBOT - Entrypoint script
# Handles DB wait, migrations, and service startup

set -e

# Function to wait for PostgreSQL
wait_for_postgres() {
    echo "Waiting for PostgreSQL to be ready..."

    # Extract host and port from DATABASE_URL
    # DATABASE_URL format: postgresql+asyncpg://user:pass@host:port/dbname
    DB_HOST=$(echo "$DATABASE_URL" | sed -E 's/.*@([^:]+):.*/\1/')
    DB_PORT=$(echo "$DATABASE_URL" | sed -E 's/.*:([0-9]+)\/.*/\1/')

    # Default port if not found
    DB_PORT=${DB_PORT:-5432}

    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        if python -c "
import socket
import sys
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex(('$DB_HOST', $DB_PORT))
    sock.close()
    sys.exit(0 if result == 0 else 1)
except:
    sys.exit(1)
" 2>/dev/null; then
            echo "PostgreSQL is ready!"
            return 0
        fi

        echo "Attempt $attempt/$max_attempts: PostgreSQL not ready, waiting..."
        sleep 2
        attempt=$((attempt + 1))
    done

    echo "ERROR: PostgreSQL did not become ready in time"
    exit 1
}

# Function to run migrations
run_migrations() {
    echo "Running database migrations..."
    python -m alembic upgrade head
    echo "Migrations completed successfully!"
}

# Main logic
case "${1:-bot}" in
    "bot")
        wait_for_postgres
        run_migrations
        echo "Starting bot..."
        exec python -m src.bot.main
        ;;
    "migrate")
        wait_for_postgres
        run_migrations
        echo "Migration-only mode completed."
        ;;
    *)
        # Pass through any other command
        exec "$@"
        ;;
esac
