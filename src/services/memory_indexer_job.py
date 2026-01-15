"""
MINDSETHAPPYBOT - Memory Indexer Job
Scheduled job for indexing conversation memories.

This module provides functions that can be called from the scheduler
to incrementally index conversation memories for all users.
"""
import logging
from src.services.conversation_memory_service import ConversationMemoryService

logger = logging.getLogger(__name__)


async def index_conversation_memories() -> dict:
    """
    Index conversation memories for all users.

    This function is designed to be called periodically (e.g., every 15 minutes)
    by the APScheduler. It performs incremental indexing - only processing
    conversations that haven't been indexed yet.

    Returns:
        Dict with stats: users_processed, conversations_processed, memories_stored
    """
    logger.info("Starting conversation memory indexing job")

    try:
        memory_service = ConversationMemoryService()
        stats = await memory_service.index_all_users(full_reindex=False)

        logger.info(
            f"Memory indexing complete: "
            f"{stats['users_processed']} users, "
            f"{stats['conversations_processed']} conversations, "
            f"{stats['memories_stored']} memories stored"
        )

        return stats

    except Exception as e:
        logger.error(f"Memory indexing job failed: {e}")
        return {
            "users_processed": 0,
            "conversations_processed": 0,
            "memories_stored": 0,
            "error": str(e),
        }


async def full_reindex_memories() -> dict:
    """
    Perform a full reindex of all conversation memories.

    WARNING: This is an expensive operation that should only be run
    manually or during maintenance windows. It processes all conversations
    for all users, regardless of whether they've been indexed before.

    Returns:
        Dict with stats: users_processed, conversations_processed, memories_stored
    """
    logger.warning("Starting FULL memory reindex - this may take a while")

    try:
        memory_service = ConversationMemoryService()
        stats = await memory_service.index_all_users(full_reindex=True)

        logger.info(
            f"Full memory reindex complete: "
            f"{stats['users_processed']} users, "
            f"{stats['conversations_processed']} conversations, "
            f"{stats['memories_stored']} memories stored"
        )

        return stats

    except Exception as e:
        logger.error(f"Full memory reindex failed: {e}")
        return {
            "users_processed": 0,
            "conversations_processed": 0,
            "memories_stored": 0,
            "error": str(e),
        }


async def create_dialog_summaries() -> dict:
    """
    Create dialog summaries for all users who need them.

    This function compresses multiple raw dialog memories into semantic summaries.
    Should be called periodically (e.g., every hour or once per day).

    Summaries are created when:
    - User has at least SUMMARY_MIN_MESSAGES (8) unsummarized raw memories
    - AND either has SUMMARY_BATCH_SIZE (12) messages OR oldest is > 24 hours old

    Returns:
        Dict with stats: users_processed, summaries_created
    """
    logger.info("Starting dialog summary creation job")

    try:
        memory_service = ConversationMemoryService()
        stats = await memory_service.create_summaries_for_all_users()

        logger.info(
            f"Dialog summary creation complete: "
            f"{stats['users_processed']} users, "
            f"{stats['summaries_created']} summaries created"
        )

        return stats

    except Exception as e:
        logger.error(f"Dialog summary creation job failed: {e}")
        return {
            "users_processed": 0,
            "summaries_created": 0,
            "error": str(e),
        }
