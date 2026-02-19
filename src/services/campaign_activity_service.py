"""
MINDSETHAPPYBOT - Campaign Activity Delivery Service
Handles sending campaign messages when users become active
"""
import logging
import os
from datetime import datetime, timedelta, timezone

from aiogram import Bot
from sqlalchemy import text

from src.db.database import get_session

logger = logging.getLogger(__name__)

# Feature flag to enable/disable activity-triggered campaigns
ENABLE_CAMPAIGN_ACTIVITY_TRIGGER = os.getenv("ENABLE_CAMPAIGN_ACTIVITY_TRIGGER", "false").lower() == "true"


class CampaignActivityDeliveryService:
    """
    Service for delivering campaign messages based on user activity.

    When a user becomes active (sends a message, presses a button),
    this service checks if there are any scheduled campaigns with
    `send_on_activity=true` and delivers pending messages.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "CampaignActivityDeliveryService":
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def update_user_activity(self, telegram_id: int) -> None:
        """
        Update user's last_active_at timestamp.
        Should be called on every user interaction.
        """
        async with get_session() as session:
            await session.execute(
                text("UPDATE users SET last_active_at = NOW() WHERE telegram_id = :tid"),
                {"tid": telegram_id}
            )
            await session.commit()

    async def check_and_deliver_activity_campaigns(
        self,
        telegram_id: int,
        bot: Bot
    ) -> int:
        """
        Check for activity-triggered campaigns and deliver pending messages.

        Args:
            telegram_id: User's Telegram ID
            bot: Aiogram bot instance for sending messages

        Returns:
            Number of messages sent
        """
        if not ENABLE_CAMPAIGN_ACTIVITY_TRIGGER:
            return 0

        messages_sent = 0

        async with get_session() as session:
            # Find scheduled campaigns with send_on_activity=true
            # that have pending/rendered targets for this user
            result = await session.execute(
                text("""
                    SELECT
                        c.id as campaign_id,
                        c.title,
                        c.delivery_params_json,
                        t.id as target_id,
                        t.rendered_text,
                        t.last_activity_triggered_at,
                        t.activity_send_count
                    FROM admin_campaigns c
                    JOIN admin_campaign_targets t ON t.campaign_id = c.id
                    JOIN users u ON u.id = t.user_id
                    WHERE u.telegram_id = :tid
                      AND c.status IN ('scheduled', 'sending')
                      AND t.status IN ('pending', 'rendered')
                      AND c.delivery_params_json->>'send_on_activity' = 'true'
                      AND u.is_blocked = false
                      AND u.notifications_enabled = true
                    ORDER BY c.id
                    LIMIT 5
                """),
                {"tid": telegram_id}
            )

            targets = result.fetchall()

            for target in targets:
                try:
                    delivery_params = target.delivery_params_json or {}

                    # Check cooldown
                    cooldown_minutes = delivery_params.get('cooldown_minutes', 60)
                    if target.last_activity_triggered_at:
                        cooldown_end = target.last_activity_triggered_at + timedelta(minutes=cooldown_minutes)
                        if datetime.now(timezone.utc) < cooldown_end:
                            logger.debug(
                                f"Campaign {target.campaign_id}: User {telegram_id} is in cooldown "
                                f"(until {cooldown_end})"
                            )
                            continue

                    # Check max_per_activity
                    max_per_activity = delivery_params.get('max_per_activity', 1)
                    if messages_sent >= max_per_activity:
                        logger.debug(
                            f"Campaign {target.campaign_id}: Max per activity reached ({max_per_activity})"
                        )
                        break

                    # Check test_mode
                    test_mode = delivery_params.get('test_mode', False)

                    message_text = target.rendered_text
                    if not message_text:
                        logger.warning(
                            f"Campaign {target.campaign_id}: No rendered text for target {target.target_id}"
                        )
                        continue

                    if test_mode:
                        # In test mode, just log and update status
                        logger.info(
                            f"[TEST MODE] Campaign {target.campaign_id}: Would send to {telegram_id}: "
                            f"{message_text[:50]}..."
                        )
                        await session.execute(
                            text("""
                                UPDATE admin_campaign_targets
                                SET status = 'sent',
                                    sent_at = NOW(),
                                    last_activity_triggered_at = NOW(),
                                    activity_send_count = activity_send_count + 1
                                WHERE id = :tid
                            """),
                            {"tid": target.target_id}
                        )
                    else:
                        # Actually send the message
                        try:
                            await bot.send_message(
                                chat_id=telegram_id,
                                text=message_text,
                                parse_mode="HTML"
                            )

                            await session.execute(
                                text("""
                                    UPDATE admin_campaign_targets
                                    SET status = 'sent',
                                        sent_at = NOW(),
                                        last_activity_triggered_at = NOW(),
                                        activity_send_count = activity_send_count + 1
                                    WHERE id = :tid
                                """),
                                {"tid": target.target_id}
                            )

                            logger.info(
                                f"Campaign {target.campaign_id}: Sent activity-triggered message to {telegram_id}"
                            )
                            messages_sent += 1

                        except Exception as e:
                            logger.error(
                                f"Campaign {target.campaign_id}: Failed to send to {telegram_id}: {e}"
                            )
                            await session.execute(
                                text("""
                                    UPDATE admin_campaign_targets
                                    SET status = 'failed',
                                        error = :error,
                                        last_activity_triggered_at = NOW(),
                                        activity_send_count = activity_send_count + 1
                                    WHERE id = :tid
                                """),
                                {"tid": target.target_id, "error": str(e)}
                            )

                except Exception as e:
                    logger.error(f"Error processing campaign target {target.target_id}: {e}")

            # Update campaign sent_count if any messages were sent
            if messages_sent > 0:
                await session.execute(
                    text("""
                        UPDATE admin_campaigns c
                        SET sent_count = (
                            SELECT COUNT(*) FROM admin_campaign_targets t
                            WHERE t.campaign_id = c.id AND t.status = 'sent'
                        ),
                        failed_count = (
                            SELECT COUNT(*) FROM admin_campaign_targets t
                            WHERE t.campaign_id = c.id AND t.status = 'failed'
                        ),
                        updated_at = NOW()
                        WHERE c.status IN ('scheduled', 'sending')
                          AND c.delivery_params_json->>'send_on_activity' = 'true'
                    """)
                )

                # Check if any campaigns are complete
                await session.execute(
                    text("""
                        UPDATE admin_campaigns
                        SET status = 'done', completed_at = NOW()
                        WHERE status IN ('scheduled', 'sending')
                          AND total_targets > 0
                          AND (
                              SELECT COUNT(*) FROM admin_campaign_targets
                              WHERE campaign_id = admin_campaigns.id
                              AND status IN ('pending', 'rendered')
                          ) = 0
                    """)
                )

            await session.commit()

        return messages_sent
