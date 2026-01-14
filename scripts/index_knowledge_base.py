"""
Legacy entrypoint kept for convenience.
NOTE: This file is NOT copied into the Docker image by default.
Prefer running inside Docker: `python -m src.knowledge_indexer`.
"""

import asyncio

from src.knowledge_indexer import main


if __name__ == "__main__":
    asyncio.run(main())

