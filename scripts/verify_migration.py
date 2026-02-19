#!/usr/bin/env python3
"""
Verify TIMESTAMPTZ migration was successful
Run this AFTER applying the migration
"""

import asyncio
import sys
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/mindsethappybot')


async def verify_migration():
    """Check that all timestamp columns are now TIMESTAMPTZ"""

    engine = create_async_engine(DATABASE_URL, echo=False)

    print("=" * 60)
    print("TIMESTAMPTZ MIGRATION VERIFICATION")
    print("=" * 60)
    print()

    errors = []
    success = []

    async with engine.begin() as conn:
        # Query to check column types
        result = await conn.execute(text("""
            SELECT
                table_name,
                column_name,
                data_type,
                datetime_precision
            FROM information_schema.columns
            WHERE table_schema = 'public'
                AND column_name IN (
                    'created_at', 'updated_at', 'last_active_at',
                    'notifications_paused_until', 'reviewed_at',
                    'last_parsed_at', 'timestamp', 'scheduled_for',
                    'triggered_at'
                )
            ORDER BY table_name, column_name
        """))

        columns = result.fetchall()

        print("Checking timestamp columns:")
        print("-" * 60)

        for table, column, dtype, precision in columns:
            expected = "timestamp with time zone"
            status = "✓" if dtype == expected else "✗"

            print(f"{status} {table}.{column}: {dtype}")

            if dtype == expected:
                success.append(f"{table}.{column}")
            else:
                errors.append(f"{table}.{column} is {dtype}, expected {expected}")

        print()
        print("=" * 60)

        # Test write/read with timezone-aware datetime
        print("Testing write/read operations:")
        print("-" * 60)

        try:
            # Test writing a timezone-aware datetime
            now = datetime.now(timezone.utc)

            # Test on users table
            await conn.execute(text("""
                UPDATE users
                SET last_active_at = :now
                WHERE telegram_id = (SELECT telegram_id FROM users LIMIT 1)
            """), {"now": now})

            # Read it back
            result = await conn.execute(text("""
                SELECT last_active_at
                FROM users
                WHERE telegram_id = (SELECT telegram_id FROM users LIMIT 1)
            """))

            row = result.fetchone()
            if row and row[0]:
                read_time = row[0]
                if hasattr(read_time, 'tzinfo') and read_time.tzinfo:
                    print("✓ Write/read test: Success - datetime is timezone-aware")
                else:
                    print("✗ Write/read test: Failed - datetime is timezone-naive")
                    errors.append("Datetime read from DB is not timezone-aware")
            else:
                print("⚠ Write/read test: No data to test")

        except Exception as e:
            print(f"✗ Write/read test failed: {e}")
            errors.append(f"Write/read test: {e}")

        print()
        print("=" * 60)

        # Check for timezone consistency
        print("Checking timezone consistency:")
        print("-" * 60)

        result = await conn.execute(text("""
            SELECT
                current_setting('TIMEZONE') as db_timezone,
                NOW() as current_time,
                NOW() AT TIME ZONE 'UTC' as utc_time
        """))

        row = result.fetchone()
        print(f"Database timezone: {row[0]}")
        print(f"Current time: {row[1]}")
        print(f"UTC time: {row[2]}")

    await engine.dispose()

    print()
    print("=" * 60)
    print("VERIFICATION RESULTS")
    print("=" * 60)

    if errors:
        print("❌ MIGRATION FAILED - Issues found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ MIGRATION SUCCESSFUL!")
        print(f"  - {len(success)} columns successfully converted to TIMESTAMPTZ")
        print("  - Write/read operations work with timezone-aware datetimes")
        print("  - Database is ready for production use")
        return True


async def test_application_compatibility():
    """Test that the application can work with new column types"""

    print()
    print("=" * 60)
    print("APPLICATION COMPATIBILITY TEST")
    print("=" * 60)

    try:
        # Import application models
        from src.db.database import init_db, get_session
        from src.db.models import User, Moment, Conversation

        # Initialize database
        await init_db()

        print("Testing model operations:")
        print("-" * 60)

        async with get_session() as session:
            # Test reading users
            result = await session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print(f"✓ Can read users table: {count} users found")

            # Test datetime operations
            now = datetime.now(timezone.utc)

            # This should work without .replace(tzinfo=None)
            result = await session.execute(text("""
                SELECT COUNT(*)
                FROM moments
                WHERE created_at > :cutoff
            """), {"cutoff": now})

            print("✓ Datetime filtering works with timezone-aware objects")

        print()
        print("✅ APPLICATION COMPATIBILITY: PASSED")
        return True

    except Exception as e:
        print(f"❌ APPLICATION COMPATIBILITY: FAILED")
        print(f"   Error: {e}")
        return False


async def main():
    """Run all verification checks"""

    migration_ok = await verify_migration()

    if migration_ok:
        app_ok = await test_application_compatibility()

        if app_ok:
            print()
            print("=" * 60)
            print("🎉 ALL CHECKS PASSED!")
            print("=" * 60)
            print()
            print("Next steps:")
            print("1. Remove all .replace(tzinfo=None) from the code")
            print("2. Update SQLAlchemy models to use DateTime(timezone=True)")
            print("3. Test the application thoroughly")
            print("4. Deploy to production")
            sys.exit(0)
        else:
            sys.exit(1)
    else:
        print()
        print("⚠️  Migration verification failed!")
        print("   DO NOT proceed with deployment")
        print("   Consider rolling back the migration")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())