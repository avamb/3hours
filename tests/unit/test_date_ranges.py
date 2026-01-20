"""
MINDSETHAPPYBOT - Unit tests for date range utilities
Tests the calendar-based date range calculations for summaries
"""
import pytest
from datetime import datetime, timezone as dt_timezone
from freezegun import freeze_time

from src.utils.date_ranges import (
    get_today_range,
    get_week_range,
    get_month_range,
    get_previous_week_range,
    get_previous_month_range,
    parse_timezone,
    DateRange,
    format_summary_header,
)


class TestDateRange:
    """Tests for DateRange dataclass"""

    def test_format_range_same_day(self):
        """Test format_range when start and end are on the same day"""
        from datetime import datetime
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        tz = ZoneInfo("Europe/Moscow")
        start = datetime(2025, 1, 20, 0, 0, 0, tzinfo=tz)
        end = datetime(2025, 1, 20, 23, 59, 59, tzinfo=tz)
        dr = DateRange(start=start, end=end, timezone="Europe/Moscow")

        assert dr.format_range("%d.%m.%Y") == "20.01.2025"

    def test_format_range_different_days(self):
        """Test format_range when start and end are on different days"""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        tz = ZoneInfo("Europe/Moscow")
        start = datetime(2025, 1, 13, 0, 0, 0, tzinfo=tz)
        end = datetime(2025, 1, 19, 23, 59, 59, tzinfo=tz)
        dr = DateRange(start=start, end=end, timezone="Europe/Moscow")

        assert dr.format_range("%d.%m.%Y") == "13.01.2025 – 19.01.2025"

    def test_utc_conversion(self):
        """Test that UTC conversion works correctly"""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        # Moscow is UTC+3
        tz = ZoneInfo("Europe/Moscow")
        start = datetime(2025, 1, 20, 0, 0, 0, tzinfo=tz)  # 00:00 Moscow = 21:00 UTC prev day
        dr = DateRange(start=start, end=start, timezone="Europe/Moscow")

        # Moscow 00:00 = UTC 21:00 (prev day)
        assert dr.start_utc.hour == 21
        assert dr.start_utc.day == 19


class TestParseTimezone:
    """Tests for parse_timezone function"""

    def test_utc_string(self):
        """Test parsing 'UTC' string"""
        tz = parse_timezone("UTC")
        assert tz == dt_timezone.utc

    def test_none_returns_utc(self):
        """Test that None returns UTC"""
        tz = parse_timezone(None)
        assert tz == dt_timezone.utc

    def test_empty_string_returns_utc(self):
        """Test that empty string returns UTC"""
        tz = parse_timezone("")
        assert tz == dt_timezone.utc

    def test_iana_timezone(self):
        """Test parsing IANA timezone name"""
        tz = parse_timezone("Europe/Moscow")
        # Should return a ZoneInfo object
        assert tz is not None

    def test_offset_format_with_colon(self):
        """Test parsing offset format with colon (+03:00)"""
        tz = parse_timezone("+03:00")
        # Should return a timezone with 3 hour offset
        assert tz is not None

    def test_offset_format_without_colon(self):
        """Test parsing offset format without colon (+0300)"""
        tz = parse_timezone("+0300")
        # Should return a timezone with 3 hour offset
        assert tz is not None


class TestGetTodayRange:
    """Tests for get_today_range function"""

    @freeze_time("2025-01-20 14:30:00")
    def test_today_range_utc(self):
        """Test today's range in UTC"""
        dr = get_today_range("UTC")

        # Should be Jan 20, 2025 00:00:00 to 23:59:59
        assert dr.start.day == 20
        assert dr.start.month == 1
        assert dr.start.year == 2025
        assert dr.start.hour == 0
        assert dr.start.minute == 0

        assert dr.end.day == 20
        assert dr.end.hour == 23
        assert dr.end.minute == 59

    @freeze_time("2025-01-20 01:00:00")  # 01:00 UTC = 04:00 Moscow
    def test_today_range_moscow(self):
        """Test today's range in Moscow timezone"""
        dr = get_today_range("Europe/Moscow")

        # Moscow is UTC+3, so at 01:00 UTC it's 04:00 Moscow (Jan 20)
        # The range should cover Jan 20 in Moscow time
        assert dr.start.day == 20
        assert dr.start.hour == 0
        assert dr.end.day == 20
        assert dr.end.hour == 23


class TestGetWeekRange:
    """Tests for get_week_range function"""

    @freeze_time("2025-01-15 14:30:00")  # Wednesday
    def test_week_range_mid_week(self):
        """Test week range when called mid-week (Wednesday)"""
        dr = get_week_range("UTC")

        # Jan 15 is Wednesday
        # Week should be Mon Jan 13 to Sun Jan 19
        assert dr.start.day == 13  # Monday
        assert dr.start.weekday() == 0  # Monday = 0

        assert dr.end.day == 19  # Sunday
        assert dr.end.weekday() == 6  # Sunday = 6

    @freeze_time("2025-01-13 14:30:00")  # Monday
    def test_week_range_monday(self):
        """Test week range when called on Monday"""
        dr = get_week_range("UTC")

        # Week should still be Mon Jan 13 to Sun Jan 19
        assert dr.start.day == 13
        assert dr.end.day == 19

    @freeze_time("2025-01-19 23:00:00")  # Sunday
    def test_week_range_sunday(self):
        """Test week range when called on Sunday"""
        dr = get_week_range("UTC")

        # Week should still be Mon Jan 13 to Sun Jan 19
        assert dr.start.day == 13
        assert dr.end.day == 19


class TestGetMonthRange:
    """Tests for get_month_range function"""

    @freeze_time("2025-01-15 14:30:00")
    def test_month_range_january(self):
        """Test month range for January"""
        dr = get_month_range("UTC")

        # January has 31 days
        assert dr.start.day == 1
        assert dr.start.month == 1
        assert dr.end.day == 31
        assert dr.end.month == 1

    @freeze_time("2025-02-15 14:30:00")
    def test_month_range_february_non_leap(self):
        """Test month range for February (non-leap year)"""
        dr = get_month_range("UTC")

        # 2025 is not a leap year, February has 28 days
        assert dr.start.day == 1
        assert dr.start.month == 2
        assert dr.end.day == 28
        assert dr.end.month == 2

    @freeze_time("2024-02-15 14:30:00")
    def test_month_range_february_leap(self):
        """Test month range for February (leap year)"""
        dr = get_month_range("UTC")

        # 2024 is a leap year, February has 29 days
        assert dr.start.day == 1
        assert dr.start.month == 2
        assert dr.end.day == 29
        assert dr.end.month == 2


class TestGetPreviousWeekRange:
    """Tests for get_previous_week_range function"""

    @freeze_time("2025-01-20 14:30:00")  # Monday
    def test_previous_week_from_monday(self):
        """Test previous week range when called on Monday"""
        dr = get_previous_week_range("UTC")

        # Previous week: Mon Jan 6 to Sun Jan 12
        assert dr.start.day == 13  # Actually this Monday's previous week is Jan 13
        # Wait, Jan 20 is a Monday. Previous week would be Jan 13-19
        # Let me recalculate...
        # Actually Jan 20 2025 is Monday
        # This week: Jan 20-26
        # Previous week: Jan 13-19
        assert dr.start.day == 13
        assert dr.end.day == 19


class TestFormatSummaryHeader:
    """Tests for format_summary_header function"""

    def test_russian_weekly_header(self):
        """Test Russian weekly summary header"""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        tz = ZoneInfo("UTC")
        start = datetime(2025, 1, 13, 0, 0, 0, tzinfo=tz)
        end = datetime(2025, 1, 19, 23, 59, 59, tzinfo=tz)
        dr = DateRange(start=start, end=end, timezone="UTC")

        header = format_summary_header(dr, "weekly", "ru")
        assert "Еженедельное саммари" in header
        assert "13.01.2025" in header
        assert "19.01.2025" in header

    def test_english_monthly_header(self):
        """Test English monthly summary header"""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        tz = ZoneInfo("UTC")
        start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=tz)
        end = datetime(2025, 1, 31, 23, 59, 59, tzinfo=tz)
        dr = DateRange(start=start, end=end, timezone="UTC")

        header = format_summary_header(dr, "monthly", "en")
        assert "Monthly Summary" in header

    def test_today_header_single_date(self):
        """Test today's header shows single date"""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo

        tz = ZoneInfo("UTC")
        start = datetime(2025, 1, 20, 0, 0, 0, tzinfo=tz)
        end = datetime(2025, 1, 20, 23, 59, 59, tzinfo=tz)
        dr = DateRange(start=start, end=end, timezone="UTC")

        header = format_summary_header(dr, "today", "ru")
        assert "Саммари за сегодня" in header
        assert "20.01.2025" in header


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
