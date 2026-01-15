"""
MINDSETHAPPYBOT - Immediate Memory Indexer
Provides functions to trigger immediate memory indexing for user messages.

This module is called from message handlers to index user messages immediately
rather than waiting for the scheduled batch job.
"""

import logging
import asyncio
from typing import Optional

from src.db.models import Conversation

logger = logging.getLogger(__name__)

# Minimum message length for immediate memory indexing
# Short messages (greetings, ok, yes, etc.) are skipped
MIN_IMMEDIATE_INDEX_LENGTH = 80


async def trigger_immediate_indexing(
    user_id: int,
    conversation: Conversation,
) -> None:
    """
    Trigger immediate memory indexing for a conversation.

    This is a fire-and-forget function that indexes the message
    in the background without blocking the main response flow.

    Args:
        user_id: Database user ID
        conversation: The Conversation object to index
    """
    # Skip short messages
    content = conversation.content or ""
    if len(content) < MIN_IMMEDIATE_INDEX_LENGTH:
        logger.debug(
            f"Skipped immediate indexing for short message {conversation.id} "
            f"(len={len(content)} < {MIN_IMMEDIATE_INDEX_LENGTH})"
        )
        return

    # Fire-and-forget: don't block the response
    asyncio.create_task(_index_message_async(user_id, conversation))
    logger.debug(
        f"Triggered immediate indexing for message {conversation.id} "
        f"(user_id={user_id}, len={len(content)})"
    )


async def _index_message_async(user_id: int, conversation: Conversation) -> None:
    """
    Index a single message asynchronously.
    This runs in the background after the message is saved.
    """
    try:
        # Lazy import to avoid circular dependency
        from src.services.conversation_memory_service import ConversationMemoryService

        memory_service = ConversationMemoryService()
        stored_count = await memory_service.process_conversation(user_id, conversation)

        if stored_count > 0:
            logger.info(
                f"Immediate indexing: stored {stored_count} memories from message {conversation.id}"
            )
        else:
            logger.debug(
                f"Immediate indexing: no memories stored from message {conversation.id}"
            )

    except Exception as e:
        # Never fail - this is best-effort background work
        logger.warning(f"Immediate memory indexing failed for message {conversation.id}: {e}")


async def should_index_immediately(message_type: str, content: str) -> bool:
    """
    Check if a message should be indexed immediately.

    Args:
        message_type: Type of message (e.g., 'free_dialog', 'user_response')
        content: Message content

    Returns:
        True if the message should be indexed immediately
    """
    # Only index user messages
    if message_type not in ("user_response", "free_dialog"):
        return False

    # Skip short messages
    if len(content) < MIN_IMMEDIATE_INDEX_LENGTH:
        return False

    return True
