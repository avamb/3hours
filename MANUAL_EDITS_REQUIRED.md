# Manual Edits Required for Feature #184

Due to file editing tool issues, the following edits need to be applied manually:

## 1. Scheduler (src/services/scheduler.py)

Add this job inside the `start()` method, before `self.scheduler.start()`:

```python
        # Index conversation memories every 15 minutes (incremental)
        # This extracts memory-worthy facts from user conversations for RAG
        from src.services.memory_indexer_job import index_conversation_memories
        self.scheduler.add_job(
            index_conversation_memories,
            trigger=IntervalTrigger(minutes=15),
            id="memory_indexing",
            replace_existing=True,
        )
```

## 2. Personalization Service (src/services/personalization_service.py)

In the `_get_rag_instruction()` method, add support for query type 'R' (remember queries).

Find this code around line 783:
```python
        has_moments = bool(rag_context.moments)
        has_kb = bool(rag_context.kb_chunks)

        if rag_context.query_type == 'A':
```

Replace with:
```python
        has_moments = bool(rag_context.moments)
        has_kb = bool(rag_context.kb_chunks)
        has_dialog_memories = bool(rag_context.dialog_memories)

        if rag_context.query_type == 'R':
            # Remember query - anti-hallucination mode
            if has_dialog_memories or has_moments:
                return """
=== RAG MODE: REMEMBER (Anti-Hallucination) ===
The user is asking about something they told you before.
You MUST ONLY use facts from "FACTS USER TOLD YOU" and "USER'S PERSONAL HISTORY" sections.
If the requested information is NOT in those sections, say you don't have it stored.
NEVER invent or assume facts the user didn't tell you.
Be honest if you don't have the information.

(Русский): Пользователь спрашивает о том, что рассказывал раньше.
Используй ТОЛЬКО факты из секций выше.
Если запрошенной информации НЕТ, скажи, что у тебя её нет.
НИКОГДА не выдумывай факты, которые пользователь не сообщал."""
            else:
                return """
=== RAG MODE: REMEMBER (No Data) ===
The user is asking about something they told you before, but you have NO stored information.
Be HONEST and say you don't have that information stored.
Ask them to tell you again if they want you to remember it.
NEVER invent or guess facts about the user.

(Русский): Пользователь спрашивает о том, что рассказывал, но у тебя НЕТ информации.
Честно скажи, что у тебя нет этой информации.
Предложи рассказать снова.
НИКОГДА не выдумывай факты о пользователе."""

        elif rag_context.query_type == 'A':
```

## Summary of Completed Work

The following files were successfully created/updated:

1. ✅ `alembic/versions/20260115_0012_add_conversation_memories_table.py` - Migration
2. ✅ `src/db/models/conversation_memory.py` - SQLAlchemy model
3. ✅ `src/db/models/__init__.py` - Added ConversationMemory export
4. ✅ `src/db/models/user.py` - Added tracking field and relationship
5. ✅ `src/services/conversation_memory_service.py` - Full memory extraction/retrieval service
6. ✅ `src/services/knowledge_retrieval_service.py` - Updated with dialog memory support
7. ✅ `src/services/memory_indexer_job.py` - Scheduled job module

## Testing Steps

After applying manual edits:

1. Run database migration: `alembic upgrade head`
2. Rebuild Docker: `docker-compose build && docker-compose up -d`
3. Test memory extraction by sending messages with facts
4. Test remember queries (e.g., "помнишь, что я тебе рассказывал?")
5. Verify user isolation by checking that User A's memories don't appear for User B
