"""
MINDSETHAPPYBOT - Date range utilities
Provides calendar-based date range calculations for summaries and filters.

All ranges are timezone-aware and return:
- start: Beginning of the period (00:00:00 in user's timezone)
- end: End of the period (23:59:59.999999 in user's timezone)
"""
import logging
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Optional
from dataclasses import dataclass
import calendar

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

# Default fallback timezone when user timezone is missing or invalid
DEFAULT_TIMEZONE = "UTC"


@dataclass
class DateRange:
    """Represents a date range with start and end timestamps."""
    start: datetime  # Start of period (aware datetime)
    end: datetime    # End of period (aware datetime)
    timezone: str    # Timezone name used for calculation

    @property
    def start_utc(self) -> datetime:
        """Return start as UTC datetime (naive for DB compatibility)."""
        return self.start.astimezone(dt_timezone.utc).replace(tzinfo=None)

    @property
    def end_utc(self) -> datetime:
        """Return end as UTC datetime (naive for DB compatibility)."""
        return self.end.astimezone(dt_timezone.utc).replace(tzinfo=None)

    def format_range(self, date_format: str = "%Y-%m-%d") -> str:
        """Format the range for display (using local dates)."""
        start_local = self.start.strftime(date_format)
        end_local = self.end.strftime(date_format)
        if start_local == end_local:
            return start_local
        return f"{start_local} – {end_local}"

    def __str__(self) -> str:
        return (
            f"DateRange(start={self.start.isoformat()}, "
            f"end={self.end.isoformat()}, tz={self.timezone})"
        )


def parse_timezone(tz_str: Optional[str]) -> ZoneInfo | dt_timezone:
    """
    Parse timezone string to timezone object.

    Supports:
    - IANA timezone names (e.g., "Europe/Moscow", "America/New_York")
    - UTC offset format (e.g., "+03:00", "-05:00", "+0300", "-0500")
    - "UTC" string
    - None or empty string (returns UTC)

    Returns:
        timezone object (ZoneInfo for IANA names, datetime.timezone for offsets)
    """
    import re

    if not tz_str or tz_str == "UTC":
        return dt_timezone.utc

    # Try to parse as offset format (+03:00, -05:00, +0300, -0500)
    offset_match = re.match(r'^([+-])(\d{2}):?(\d{2})$', tz_str)
    if offset_match:
        sign = 1 if offset_match.group(1) == '+' else -1
        hours = int(offset_match.group(2))
        minutes = int(offset_match.group(3))
        offset = timedelta(hours=hours, minutes=minutes) * sign
        return dt_timezone(offset)

    # Try as IANA timezone name
    try:
        return ZoneInfo(tz_str)
    except Exception:
        logger.warning(f"Unknown timezone: {tz_str}, falling back to {DEFAULT_TIMEZONE}")
        return dt_timezone.utc


def get_user_local_now(user_timezone: Optional[str]) -> datetime:
    """
    Get current time in user's timezone (aware datetime).

    Args:
        user_timezone: User's timezone string (IANA name or offset)

    Returns:
        Current datetime in user's timezone (timezone-aware)
    """
    tz = parse_timezone(user_timezone)
    return datetime.now(tz)


def get_today_range(user_timezone: Optional[str] = None) -> DateRange:
    """
    Get the full calendar day range for today in user's timezone.

    Returns the range from 00:00:00.000000 to 23:59:59.999999 of today
    in the user's local timezone.

    Args:
        user_timezone: User's timezone string (IANA name or offset).
                      If None or invalid, uses UTC.

    Returns:
        DateRange with start (today 00:00) and end (today 23:59:59.999999)
    """
    tz = parse_timezone(user_timezone)
    tz_name = user_timezone or DEFAULT_TIMEZONE

    now = datetime.now(tz)

    # Start of today (00:00:00.000000)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # End of today (23:59:59.999999)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

    result = DateRange(start=start, end=end, timezone=tz_name)

    logger.debug(
        f"get_today_range: tz={tz_name}, "
        f"start={start.isoformat()}, end={end.isoformat()}, "
        f"start_utc={result.start_utc}, end_utc={result.end_utc}"
    )

    return result


def get_week_range(user_timezone: Optional[str] = None) -> DateRange:
    """
    Get the full calendar week range (Monday-Sunday) for the current week
    in user's timezone.

    The week starts on Monday (ISO standard) and ends on Sunday.
    Returns the range from Monday 00:00:00 to Sunday 23:59:59.999999.

    Args:
        user_timezone: User's timezone string (IANA name or offset).
                      If None or invalid, uses UTC.

    Returns:
        DateRange with start (Monday 00:00) and end (Sunday 23:59:59.999999)
    """
    tz = parse_timezone(user_timezone)
    tz_name = user_timezone or DEFAULT_TIMEZONE

    now = datetime.now(tz)

    # Calculate days since Monday (weekday() returns 0=Monday, 6=Sunday)
    days_since_monday = now.weekday()

    # Start of week (Monday 00:00:00.000000)
    monday = now - timedelta(days=days_since_monday)
    start = monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # End of week (Sunday 23:59:59.999999)
    sunday = start + timedelta(days=6)
    end = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    result = DateRange(start=start, end=end, timezone=tz_name)

    logger.debug(
        f"get_week_range: tz={tz_name}, today_weekday={now.weekday()}, "
        f"start={start.isoformat()}, end={end.isoformat()}, "
        f"start_utc={result.start_utc}, end_utc={result.end_utc}"
    )

    return result


def get_month_range(user_timezone: Optional[str] = None) -> DateRange:
    """
    Get the full calendar month range for the current month in user's timezone.

    Returns the range from the 1st day 00:00:00 to the last day 23:59:59.999999
    of the current month.

    Args:
        user_timezone: User's timezone string (IANA name or offset).
                      If None or invalid, uses UTC.

    Returns:
        DateRange with start (1st day 00:00) and end (last day 23:59:59.999999)
    """
    tz = parse_timezone(user_timezone)
    tz_name = user_timezone or DEFAULT_TIMEZONE

    now = datetime.now(tz)

    # Start of month (1st day 00:00:00.000000)
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get the last day of the month
    _, last_day = calendar.monthrange(now.year, now.month)

    # End of month (last day 23:59:59.999999)
    end = now.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    result = DateRange(start=start, end=end, timezone=tz_name)

    logger.debug(
        f"get_month_range: tz={tz_name}, year={now.year}, month={now.month}, "
        f"last_day={last_day}, start={start.isoformat()}, end={end.isoformat()}, "
        f"start_utc={result.start_utc}, end_utc={result.end_utc}"
    )

    return result


def get_previous_week_range(user_timezone: Optional[str] = None) -> DateRange:
    """
    Get the full calendar week range for the previous week (Monday-Sunday)
    in user's timezone.

    Useful for scheduled weekly summaries that run on Sunday/Monday.

    Args:
        user_timezone: User's timezone string (IANA name or offset).
                      If None or invalid, uses UTC.

    Returns:
        DateRange with start (previous Monday 00:00) and end (previous Sunday 23:59:59.999999)
    """
    tz = parse_timezone(user_timezone)
    tz_name = user_timezone or DEFAULT_TIMEZONE

    now = datetime.now(tz)

    # Calculate days since Monday
    days_since_monday = now.weekday()

    # This week's Monday
    this_monday = now - timedelta(days=days_since_monday)

    # Previous week's Monday (7 days before this Monday)
    prev_monday = this_monday - timedelta(days=7)
    start = prev_monday.replace(hour=0, minute=0, second=0, microsecond=0)

    # Previous week's Sunday
    prev_sunday = start + timedelta(days=6)
    end = prev_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    result = DateRange(start=start, end=end, timezone=tz_name)

    logger.debug(
        f"get_previous_week_range: tz={tz_name}, "
        f"start={start.isoformat()}, end={end.isoformat()}, "
        f"start_utc={result.start_utc}, end_utc={result.end_utc}"
    )

    return result


def get_previous_month_range(user_timezone: Optional[str] = None) -> DateRange:
    """
    Get the full calendar month range for the previous month in user's timezone.

    Useful for scheduled monthly summaries that run on the 1st.

    Args:
        user_timezone: User's timezone string (IANA name or offset).
                      If None or invalid, uses UTC.

    Returns:
        DateRange with start (1st day of prev month 00:00)
        and end (last day of prev month 23:59:59.999999)
    """
    tz = parse_timezone(user_timezone)
    tz_name = user_timezone or DEFAULT_TIMEZONE

    now = datetime.now(tz)

    # Calculate first day of previous month
    if now.month == 1:
        prev_month = 12
        prev_year = now.year - 1
    else:
        prev_month = now.month - 1
        prev_year = now.year

    # Start of previous month (1st day 00:00:00.000000)
    start = now.replace(year=prev_year, month=prev_month, day=1,
                       hour=0, minute=0, second=0, microsecond=0)

    # Get the last day of the previous month
    _, last_day = calendar.monthrange(prev_year, prev_month)

    # End of previous month (last day 23:59:59.999999)
    end = start.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)

    result = DateRange(start=start, end=end, timezone=tz_name)

    logger.debug(
        f"get_previous_month_range: tz={tz_name}, year={prev_year}, month={prev_month}, "
        f"last_day={last_day}, start={start.isoformat()}, end={end.isoformat()}, "
        f"start_utc={result.start_utc}, end_utc={result.end_utc}"
    )

    return result


# Convenience function to format date range header for summaries
def format_summary_header(
    range_obj: DateRange,
    summary_type: str = "weekly",
    language_code: str = "ru"
) -> str:
    """
    Format a human-readable header for summary messages.

    Args:
        range_obj: DateRange object with the period boundaries
        summary_type: "today", "weekly", or "monthly"
        language_code: User's language code for localization

    Returns:
        Formatted header string with emoji and date range
    """
    date_range_str = range_obj.format_range("%d.%m.%Y")

    if language_code == "ru":
        headers = {
            "today": f"📅 Саммари за сегодня ({date_range_str})",
            "weekly": f"📅 Еженедельное саммари ({date_range_str})",
            "monthly": f"🗓 Месячное саммари ({date_range_str})",
        }
    elif language_code == "uk":
        headers = {
            "today": f"📅 Підсумок за сьогодні ({date_range_str})",
            "weekly": f"📅 Тижневий підсумок ({date_range_str})",
            "monthly": f"🗓 Місячний підсумок ({date_range_str})",
        }
    else:
        headers = {
            "today": f"📅 Today's Summary ({date_range_str})",
            "weekly": f"📅 Weekly Summary ({date_range_str})",
            "monthly": f"🗓 Monthly Summary ({date_range_str})",
        }

    return headers.get(summary_type, headers["weekly"])
