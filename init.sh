#!/bin/bash
# MINDSETHAPPYBOT - Initialization Script
# This script sets up and runs the development environment

set -e

echo "=================================================="
echo "  MINDSETHAPPYBOT - Development Environment Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cat > .env << 'EOF'
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mindsethappybot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=mindsethappybot

# Optional: Timezone (default: UTC)
DEFAULT_TIMEZONE=UTC

# Optional: Logging level
LOG_LEVEL=INFO
EOF
    echo -e "${RED}Please edit .env file with your actual credentials before running again.${NC}"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo ""
echo "Checking prerequisites..."

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
    echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
else
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Check Docker (optional)
if command_exists docker; then
    DOCKER_VERSION=$(docker --version | cut -d" " -f3 | tr -d ',')
    echo -e "${GREEN}✓ Docker ${DOCKER_VERSION} found${NC}"
    USE_DOCKER=true
else
    echo -e "${YELLOW}○ Docker not found. Will use local PostgreSQL.${NC}"
    USE_DOCKER=false
fi

# Setup function for Docker
setup_with_docker() {
    echo ""
    echo "Starting services with Docker Compose..."

    # Start PostgreSQL with pgvector
    docker-compose up -d postgres

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    sleep 5

    # Check if database is ready
    until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
        echo "Waiting for PostgreSQL..."
        sleep 2
    done
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
}

# Setup function for local development
setup_local() {
    echo ""
    echo "Setting up local development environment..."

    # Create virtual environment if not exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    echo "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    echo "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt

    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Run database migrations
run_migrations() {
    echo ""
    echo "Running database migrations..."

    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    python3 -m alembic upgrade head
    echo -e "${GREEN}✓ Migrations completed${NC}"
}

# Start the bot
start_bot() {
    echo ""
    echo "Starting MINDSETHAPPYBOT..."

    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    python3 -m src.bot.main
}

# Main execution
echo ""
echo "Choose setup mode:"
echo "1) Full setup with Docker (recommended)"
echo "2) Local development setup"
echo "3) Start bot only (assumes setup already done)"
echo ""

if [ -n "$1" ]; then
    CHOICE=$1
else
    read -p "Enter choice [1-3]: " CHOICE
fi

case $CHOICE in
    1)
        if [ "$USE_DOCKER" = true ]; then
            setup_with_docker
            setup_local
            run_migrations
            start_bot
        else
            echo -e "${RED}Docker not available. Please install Docker or use option 2.${NC}"
            exit 1
        fi
        ;;
    2)
        setup_local
        echo -e "${YELLOW}Note: Make sure PostgreSQL with pgvector is running locally.${NC}"
        echo "DATABASE_URL in .env should point to your local PostgreSQL."
        run_migrations
        start_bot
        ;;
    3)
        start_bot
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo "=================================================="
echo "  MINDSETHAPPYBOT is running!"
echo "  Open Telegram and search for your bot."
echo "=================================================="
