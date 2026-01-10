"""
MINDSETHAPPYBOT - System log service
Writes entries to the system_logs table for the admin panel.
"""

import logging
from typing import Optional, Dict, Any

from src.db.database import get_session
from src.db.models import SystemLog

logger = logging.getLogger(__name__)


class SystemLogService:
    """Best-effort DB logger. Never raises to caller."""

    async def log(
        self,
        level: str,
        source: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        try:
            async with get_session() as session:
                row = SystemLog(
                    level=(level or "INFO").upper(),
                    source=source[:50] if source else "bot",
                    message=message,
                    details=details,
                )
                session.add(row)
                await session.commit()
        except Exception as e:
            # Avoid recursive logging into DB
            logger.debug(f"Failed to write system log: {e}")


