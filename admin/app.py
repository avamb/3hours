"""
MINDSETHAPPYBOT - Admin Panel Web Application
Standalone FastAPI server providing admin dashboard functionality
"""
import os
import sys
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager
import uvicorn

# Database URL - sync version for admin panel
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/mindsethappybot"
).replace("postgresql+asyncpg://", "postgresql://")

# Create sync engine for admin panel
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Admin credentials (simple auth for development)
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Admin panel starting up...")
    yield
    logger.info("Admin panel shutting down...")


app = FastAPI(
    title="MINDSETHAPPYBOT Admin Panel",
    description="Admin dashboard for monitoring users, messages, and system health",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== MODELS ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class StatsResponse(BaseModel):
    total_users: int
    active_users_24h: int
    active_users_7d: int
    total_moments: int
    total_conversations: int
    moments_today: int
    moments_week: int


class UserSummary(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    language_code: str
    notifications_enabled: bool
    created_at: datetime
    last_active_at: Optional[datetime]
    onboarding_completed: bool
    total_moments: int
    current_streak: int


class ConversationMessage(BaseModel):
    id: int
    user_id: int
    telegram_id: int
    username: Optional[str]
    message_type: str
    content: str
    created_at: datetime


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    source: str


# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    """Simple authentication endpoint"""
    if request.username == ADMIN_USERNAME and request.password == ADMIN_PASSWORD:
        return {"success": True, "message": "Login successful"}
    raise HTTPException(status_code=401, detail="Invalid credentials")


# ==================== STATS ENDPOINTS ====================

@app.get("/api/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    try:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        day_ago = now - timedelta(days=1)

        # Total users
        total_users = db.execute(
            text("SELECT COUNT(*) FROM users")
        ).scalar() or 0

        # Active users in last 24h
        active_24h = db.execute(
            text("SELECT COUNT(*) FROM users WHERE last_active_at > :cutoff"),
            {"cutoff": day_ago}
        ).scalar() or 0

        # Active users in last 7 days
        active_7d = db.execute(
            text("SELECT COUNT(*) FROM users WHERE last_active_at > :cutoff"),
            {"cutoff": week_ago}
        ).scalar() or 0

        # Total moments
        total_moments = db.execute(
            text("SELECT COUNT(*) FROM moments")
        ).scalar() or 0

        # Total conversations
        total_conversations = db.execute(
            text("SELECT COUNT(*) FROM conversations")
        ).scalar() or 0

        # Moments today
        moments_today = db.execute(
            text("SELECT COUNT(*) FROM moments WHERE created_at >= :today"),
            {"today": today_start}
        ).scalar() or 0

        # Moments this week
        moments_week = db.execute(
            text("SELECT COUNT(*) FROM moments WHERE created_at >= :week_ago"),
            {"week_ago": week_ago}
        ).scalar() or 0

        return StatsResponse(
            total_users=total_users,
            active_users_24h=active_24h,
            active_users_7d=active_7d,
            total_moments=total_moments,
            total_conversations=total_conversations,
            moments_today=moments_today,
            moments_week=moments_week
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/activity")
async def get_activity_stats(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get daily activity statistics for the specified number of days"""
    try:
        result = db.execute(
            text("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM moments
                WHERE created_at >= NOW() - INTERVAL ':days days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """.replace(":days", str(days)))
        ).fetchall()

        return [{"date": str(row[0]), "count": row[1]} for row in result]
    except Exception as e:
        logger.error(f"Error getting activity stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== USERS ENDPOINTS ====================

@app.get("/api/users")
async def get_users(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get list of users with statistics"""
    try:
        base_query = """
            SELECT
                u.id, u.telegram_id, u.username, u.first_name,
                u.language_code, u.notifications_enabled, u.created_at,
                u.last_active_at, u.onboarding_completed,
                COALESCE(s.total_moments, 0) as total_moments,
                COALESCE(s.current_streak, 0) as current_streak
            FROM users u
            LEFT JOIN user_stats s ON u.id = s.user_id
        """

        params = {"limit": limit, "offset": offset}

        if search:
            base_query += """
                WHERE u.username ILIKE :search
                OR u.first_name ILIKE :search
                OR CAST(u.telegram_id AS TEXT) LIKE :search
            """
            params["search"] = f"%{search}%"

        base_query += " ORDER BY u.last_active_at DESC NULLS LAST LIMIT :limit OFFSET :offset"

        result = db.execute(text(base_query), params).fetchall()

        users = []
        for row in result:
            users.append({
                "id": row[0],
                "telegram_id": row[1],
                "username": row[2],
                "first_name": row[3],
                "language_code": row[4],
                "notifications_enabled": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "last_active_at": row[7].isoformat() if row[7] else None,
                "onboarding_completed": row[8],
                "total_moments": row[9],
                "current_streak": row[10]
            })

        # Get total count
        count_query = "SELECT COUNT(*) FROM users"
        if search:
            count_query += """
                WHERE username ILIKE :search
                OR first_name ILIKE :search
                OR CAST(telegram_id AS TEXT) LIKE :search
            """
        total = db.execute(text(count_query), {"search": f"%{search}%" if search else None}).scalar()

        return {"users": users, "total": total}
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}")
async def get_user_detail(user_id: int, db: Session = Depends(get_db)):
    """Get detailed user information"""
    try:
        result = db.execute(
            text("""
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
                WHERE u.id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "id": result[0],
            "telegram_id": result[1],
            "username": result[2],
            "first_name": result[3],
            "language_code": result[4],
            "formal_address": result[5],
            "active_hours_start": str(result[6]) if result[6] else None,
            "active_hours_end": str(result[7]) if result[7] else None,
            "notification_interval_hours": result[8],
            "notifications_enabled": result[9],
            "timezone": result[10],
            "created_at": result[11].isoformat() if result[11] else None,
            "last_active_at": result[12].isoformat() if result[12] else None,
            "onboarding_completed": result[13],
            "total_moments": result[14],
            "current_streak": result[15],
            "longest_streak": result[16],
            "total_questions_sent": result[17],
            "total_questions_answered": result[18]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/users/{user_id}/moments")
async def get_user_moments(
    user_id: int,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """Get user's moments"""
    try:
        result = db.execute(
            text("""
                SELECT id, content, source_type, mood_score, topics, created_at
                FROM moments
                WHERE user_id = :user_id
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
            """),
            {"user_id": user_id, "limit": limit, "offset": offset}
        ).fetchall()

        moments = []
        for row in result:
            moments.append({
                "id": row[0],
                "content": row[1],
                "source_type": row[2],
                "mood_score": row[3],
                "topics": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            })

        # Get total count
        total = db.execute(
            text("SELECT COUNT(*) FROM moments WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).scalar()

        return {"moments": moments, "total": total}
    except Exception as e:
        logger.error(f"Error getting user moments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CONVERSATIONS ENDPOINTS ====================

@app.get("/api/conversations")
async def get_conversations(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    message_type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get recent conversations/messages"""
    try:
        base_query = """
            SELECT
                c.id, c.user_id, u.telegram_id, u.username,
                c.message_type, c.content, c.created_at
            FROM conversations c
            JOIN users u ON c.user_id = u.id
            WHERE 1=1
        """
        params = {"limit": limit, "offset": offset}

        if message_type:
            base_query += " AND c.message_type = :message_type"
            params["message_type"] = message_type

        if user_id:
            base_query += " AND c.user_id = :user_id"
            params["user_id"] = user_id

        base_query += " ORDER BY c.created_at DESC LIMIT :limit OFFSET :offset"

        result = db.execute(text(base_query), params).fetchall()

        conversations = []
        for row in result:
            conversations.append({
                "id": row[0],
                "user_id": row[1],
                "telegram_id": row[2],
                "username": row[3],
                "message_type": row[4],
                "content": row[5][:500] if row[5] else "",  # Truncate long messages
                "created_at": row[6].isoformat() if row[6] else None
            })

        # Get total count
        count_query = "SELECT COUNT(*) FROM conversations WHERE 1=1"
        if message_type:
            count_query += " AND message_type = :message_type"
        if user_id:
            count_query += " AND user_id = :user_id"

        total = db.execute(text(count_query), params).scalar()

        return {"conversations": conversations, "total": total}
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SYSTEM ENDPOINTS ====================

@app.get("/api/system/health")
async def system_health(db: Session = Depends(get_db)):
    """Check system health"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/system/logs")
async def get_system_logs(
    limit: int = Query(default=100, ge=1, le=500),
    level: Optional[str] = None
):
    """Get recent system logs (from bot container if available)"""
    logs = []

    try:
        # Try to read from Docker logs
        import subprocess
        result = subprocess.run(
            ["docker", "logs", "--tail", str(limit), "mindsethappybot"],
            capture_output=True,
            text=True,
            timeout=5
        )

        log_lines = (result.stdout + result.stderr).split("\n")

        for line in log_lines[-limit:]:
            if not line.strip():
                continue

            # Parse log level
            log_level = "INFO"
            if "ERROR" in line:
                log_level = "ERROR"
            elif "WARNING" in line or "WARN" in line:
                log_level = "WARNING"
            elif "DEBUG" in line:
                log_level = "DEBUG"

            if level and log_level != level.upper():
                continue

            logs.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": log_level,
                "message": line[:500],
                "source": "bot"
            })
    except Exception as e:
        logs.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "WARNING",
            "message": f"Could not read bot logs: {str(e)}",
            "source": "admin"
        })

    return {"logs": logs}


@app.get("/api/system/notifications")
async def get_scheduled_notifications(
    limit: int = Query(default=50, ge=1, le=100),
    pending_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get scheduled notifications"""
    try:
        query = """
            SELECT
                n.id, n.user_id, u.username, u.first_name,
                n.scheduled_time, n.sent, n.sent_at, n.created_at
            FROM scheduled_notifications n
            JOIN users u ON n.user_id = u.id
        """

        if pending_only:
            query += " WHERE n.sent = false"

        query += " ORDER BY n.scheduled_time DESC LIMIT :limit"

        result = db.execute(text(query), {"limit": limit}).fetchall()

        notifications = []
        for row in result:
            notifications.append({
                "id": row[0],
                "user_id": row[1],
                "username": row[2],
                "first_name": row[3],
                "scheduled_time": row[4].isoformat() if row[4] else None,
                "sent": row[5],
                "sent_at": row[6].isoformat() if row[6] else None,
                "created_at": row[7].isoformat() if row[7] else None
            })

        return {"notifications": notifications}
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== STATIC FILES AND HTML ====================

# Serve the admin panel HTML
@app.get("/", response_class=HTMLResponse)
async def admin_panel():
    """Serve the admin panel HTML"""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Admin Panel - Static files not found</h1>")


# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
