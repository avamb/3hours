"""
MINDSETHAPPYBOT - Attribution Service
Handles tracking of user acquisition source/campaign from /start deep links
"""
import logging
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select

from src.db.database import get_session
from src.db.models import User, StartEvent

logger = logging.getLogger(__name__)


def parse_attribution_payload(payload: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Parse attribution payload into source and campaign.
    
    Format: source_campaign (e.g., "reddit_r_productivity_burnout")
    - source: first token before underscore (e.g., "reddit")
    - campaign: everything after first underscore (e.g., "r_productivity_burnout")
    
    If parsing fails, returns ("unknown", None).
    
    Args:
        payload: The raw deep link payload (may be None or empty)
        
    Returns:
        Tuple of (source, campaign)
    """
    if not payload or not payload.strip():
        return ("unknown", None)
    
    payload = payload.strip()
    
    # Truncate if too long (safety)
    if len(payload) > 500:
        payload = payload[:500]
    
    try:
        # Split on first underscore
        if "_" in payload:
            parts = payload.split("_", 1)
            source = parts[0].lower()[:100] if parts[0] else "unknown"
            campaign = parts[1][:255] if len(parts) > 1 and parts[1] else None
            return (source or "unknown", campaign)
        else:
            # No underscore - treat entire payload as source
            return (payload.lower()[:100] or "unknown", None)
    except Exception as e:
        logger.warning(f"Error parsing attribution payload '{payload}': {e}")
        return ("unknown", None)


class AttributionService:
    """Service for tracking user acquisition attribution"""

    async def record_start_event(
        self,
        user_id: int,
        telegram_id: int,
        payload: Optional[str] = None,
    ) -> Optional[StartEvent]:
        """
        Record a /start event and update user attribution fields.
        
        - Always creates a new StartEvent record
        - First-touch fields are set only if not already set
        - Last-touch fields are always updated
        
        Args:
            user_id: Internal user ID
            telegram_id: Telegram user ID
            payload: Raw deep link payload (may be None)
            
        Returns:
            The created StartEvent, or None on error
        """
        try:
            source, campaign = parse_attribution_payload(payload)
            now = datetime.now(timezone.utc)
            
            async with get_session() as session:
                # Get the user
                result = await session.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    logger.warning(f"User {user_id} not found for attribution recording")
                    return None
                
                # Create start event
                event = StartEvent(
                    user_id=user_id,
                    telegram_id=telegram_id,
                    raw_payload=payload[:500] if payload else None,
                    source=source,
                    campaign=campaign,
                    created_at=now,
                )
                session.add(event)
                
                # Update first-touch attribution (only if not set)
                if user.first_source is None:
                    user.first_source = source
                    user.first_campaign = campaign
                    user.first_start_payload = payload[:500] if payload else None
                    user.first_started_at = now
                    logger.info(
                        f"Set first-touch attribution for user {telegram_id}: "
                        f"source={source}, campaign={campaign}"
                    )
                
                # Always update last-touch attribution
                user.last_source = source
                user.last_campaign = campaign
                user.last_start_payload = payload[:500] if payload else None
                user.last_started_at = now
                
                await session.commit()
                
                logger.info(
                    f"Recorded start event for user {telegram_id}: "
                    f"source={source}, campaign={campaign}, payload={payload}"
                )
                
                return event
                
        except Exception as e:
            logger.error(f"Error recording start event for user {user_id}: {e}", exc_info=True)
            return None

    async def get_user_attribution(self, telegram_id: int) -> Optional[dict]:
        """
        Get attribution data for a user.
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            Dict with first_touch and last_touch attribution, or None if user not found
        """
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(User).where(User.telegram_id == telegram_id)
                )
                user = result.scalar_one_or_none()
                
                if not user:
                    return None
                
                return {
                    "first_touch": {
                        "source": user.first_source,
                        "campaign": user.first_campaign,
                        "payload": user.first_start_payload,
                        "started_at": user.first_started_at.isoformat() if user.first_started_at else None,
                    },
                    "last_touch": {
                        "source": user.last_source,
                        "campaign": user.last_campaign,
                        "payload": user.last_start_payload,
                        "started_at": user.last_started_at.isoformat() if user.last_started_at else None,
                    },
                }
                
        except Exception as e:
            logger.error(f"Error getting attribution for user {telegram_id}: {e}", exc_info=True)
            return None
