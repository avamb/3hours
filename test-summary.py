#!/usr/bin/env python3
"""
Test script for summary service
"""
import asyncio
import sys
sys.path.insert(0, '.')

from src.services.summary_service import SummaryService
from src.db.database import init_db, close_db


async def test_summaries():
    """Test weekly and monthly summary generation"""
    await init_db()

    summary_service = SummaryService()

    # Test with a known user telegram_id (from the database)
    # Using Andrei's telegram_id from the admin panel
    test_telegram_id = 446002546

    print("Testing weekly summary...")
    weekly = await summary_service.generate_weekly_summary(test_telegram_id)
    if weekly:
        print("Weekly summary generated successfully:")
        print("-" * 50)
        print(weekly)
        print("-" * 50)
    else:
        print("No weekly summary (not enough moments)")

    print("\nTesting monthly summary...")
    monthly = await summary_service.generate_monthly_summary(test_telegram_id)
    if monthly:
        print("Monthly summary generated successfully:")
        print("-" * 50)
        print(monthly)
        print("-" * 50)
    else:
        print("No monthly summary (not enough moments)")

    await close_db()


if __name__ == "__main__":
    asyncio.run(test_summaries())
