"""
MINDSETHAPPYBOT - Knowledge Base indexer

Indexes rows in `knowledge_base` by:
- splitting `content` into chunks
- generating embeddings for each chunk
- writing into `knowledge_chunks`
- updating `knowledge_base.indexing_status` to 'indexed' (as expected by admin UI stats)

Run inside Docker bot container:
  python -m src.knowledge_indexer
"""

import asyncio
import logging
from typing import List, Tuple

from sqlalchemy import text

from src.db.database import init_db, close_db, get_session
from src.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

# Chunking defaults (chars). Good enough for a first pass; refine later to token-based if needed.
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200


def split_text_into_chunks(text_value: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text_value:
        return []
    if len(text_value) <= chunk_size:
        return [text_value.strip()]

    chunks: List[str] = []
    start = 0

    while start < len(text_value):
        end = min(len(text_value), start + chunk_size)

        # Try to break on a sentence/newline boundary for readability.
        if end < len(text_value):
            last_boundary = max(
                text_value.rfind(".", start, end),
                text_value.rfind("!", start, end),
                text_value.rfind("?", start, end),
                text_value.rfind("\n", start, end),
            )
            if last_boundary > start + 200:  # avoid tiny chunks
                end = last_boundary + 1

        chunk = text_value[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # advance with overlap
        start = max(end - overlap, end)

    return chunks


def _vector_literal(embedding: List[float]) -> str:
    # pgvector accepts text literal like: [0.1,0.2,...]
    return "[" + ",".join(f"{x:.10g}" for x in embedding) + "]"


async def _fetch_pending_items(limit: int = 50) -> List[Tuple[int, str]]:
    async with get_session() as session:
        result = await session.execute(
            text(
                """
                SELECT id, title
                FROM knowledge_base
                WHERE indexing_status = 'pending'
                ORDER BY created_at ASC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        )
        return [(int(r.id), str(r.title)) for r in result.fetchall()]


async def index_item(item_id: int, embedding_service: EmbeddingService) -> bool:
    async with get_session() as session:
        try:
            row = (
                await session.execute(
                    text(
                        """
                        SELECT id, title, content
                        FROM knowledge_base
                        WHERE id = :id
                        """
                    ),
                    {"id": item_id},
                )
            ).fetchone()

            if not row:
                logger.warning("KB item %s not found", item_id)
                return False

            title = str(row.title)
            content = str(row.content or "")

            await session.execute(
                text(
                    """
                    UPDATE knowledge_base
                    SET indexing_status = 'indexing',
                        indexing_error = NULL,
                        updated_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": item_id},
            )

            chunks = split_text_into_chunks(content)
            if not chunks:
                await session.execute(
                    text(
                        """
                        UPDATE knowledge_base
                        SET indexing_status = 'error',
                            indexing_error = 'Empty content',
                            updated_at = NOW()
                        WHERE id = :id
                        """
                    ),
                    {"id": item_id},
                )
                logger.error("KB item %s has empty content: %s", item_id, title)
                return False

            # Reset existing chunks (idempotent)
            await session.execute(
                text("DELETE FROM knowledge_chunks WHERE knowledge_base_id = :id"),
                {"id": item_id},
            )

            chunks_inserted = 0
            for idx, chunk_text in enumerate(chunks):
                embedding = await embedding_service.create_embedding(chunk_text)
                if embedding is None:
                    logger.warning("Embedding failed for KB item %s chunk %s", item_id, idx)
                    continue

                await session.execute(
                    text(
                        """
                        INSERT INTO knowledge_chunks
                            (knowledge_base_id, chunk_index, content, embedding, created_at)
                        VALUES
                            (:kb_id, :chunk_index, :content, :embedding::vector, NOW())
                        """
                    ),
                    {
                        "kb_id": item_id,
                        "chunk_index": idx,
                        "content": chunk_text,
                        "embedding": _vector_literal(embedding),
                    },
                )
                chunks_inserted += 1

            if chunks_inserted <= 0:
                await session.execute(
                    text(
                        """
                        UPDATE knowledge_base
                        SET indexing_status = 'error',
                            indexing_error = 'Failed to create embeddings for all chunks',
                            chunks_count = 0,
                            updated_at = NOW()
                        WHERE id = :id
                        """
                    ),
                    {"id": item_id},
                )
                logger.error("KB item %s produced 0 chunks with embeddings: %s", item_id, title)
                return False

            await session.execute(
                text(
                    """
                    UPDATE knowledge_base
                    SET indexing_status = 'indexed',
                        indexing_error = NULL,
                        chunks_count = :chunks_count,
                        updated_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": item_id, "chunks_count": chunks_inserted},
            )

            logger.info("✅ KB indexed: id=%s title=%s chunks=%s", item_id, title, chunks_inserted)
            return True

        except Exception as e:
            logger.exception("❌ KB index error for item %s: %s", item_id, e)
            await session.rollback()
            # Best effort: mark item as error
            await session.execute(
                text(
                    """
                    UPDATE knowledge_base
                    SET indexing_status = 'error',
                        indexing_error = :err,
                        updated_at = NOW()
                    WHERE id = :id
                    """
                ),
                {"id": item_id, "err": str(e)[:1000]},
            )
            return False


async def index_pending(limit: int = 50) -> None:
    pending = await _fetch_pending_items(limit=limit)
    if not pending:
        logger.info("No pending KB items.")
        return

    logger.info("Found %s pending KB item(s)", len(pending))
    embedding_service = EmbeddingService()

    for item_id, title in pending:
        logger.info("Indexing KB item %s: %s", item_id, title)
        await index_item(item_id, embedding_service)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    await init_db()
    try:
        await index_pending()
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())


