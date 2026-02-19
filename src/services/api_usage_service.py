"""
MINDSETHAPPYBOT - API Usage Service
Tracks and calculates costs for API usage
"""
import logging
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, Dict, Any
from functools import wraps

from sqlalchemy import select, func, and_

from src.db.database import get_session
from src.db.models import User, APIUsage

logger = logging.getLogger(__name__)


# OpenAI pricing per 1M tokens (as of Jan 2024)
# Prices in USD
OPENAI_PRICING = {
    # GPT-4o models
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-2024-08-06": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o-mini-2024-07-18": {"input": 0.15, "output": 0.60},

    # GPT-4 models
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4-turbo-preview": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},

    # GPT-3.5 models
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    "gpt-3.5-turbo-0125": {"input": 0.50, "output": 1.50},

    # Whisper
    "whisper-1": {"input": 0.006, "output": 0},  # $0.006 per minute

    # Embeddings
    "text-embedding-3-small": {"input": 0.02, "output": 0},
    "text-embedding-3-large": {"input": 0.13, "output": 0},
    "text-embedding-ada-002": {"input": 0.10, "output": 0},
}


class APIUsageService:
    """Service for tracking API usage and costs"""

    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
        """Calculate cost in USD for given token usage"""
        pricing = OPENAI_PRICING.get(model, {"input": 0, "output": 0})

        # Calculate cost (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return Decimal(str(round(input_cost + output_cost, 6)))

    @staticmethod
    async def log_usage(
        api_provider: str,
        model: str,
        operation_type: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        duration_ms: int = None,
        user_id: int = None,
        telegram_id: int = None,
        success: bool = True,
        error_message: str = None,
        extra_data: Dict[str, Any] = None,
    ) -> Optional[APIUsage]:
        """Log an API usage record"""
        try:
            async with get_session() as session:
                # Resolve user_id from telegram_id if needed
                db_user_id = user_id
                if telegram_id and not user_id:
                    result = await session.execute(
                        select(User.id).where(User.telegram_id == telegram_id)
                    )
                    row = result.first()
                    if row:
                        db_user_id = row[0]

                # Calculate cost
                total_tokens = input_tokens + output_tokens
                cost_usd = APIUsageService.calculate_cost(model, input_tokens, output_tokens)

                usage = APIUsage(
                    user_id=db_user_id,
                    api_provider=api_provider,
                    model=model,
                    operation_type=operation_type,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost_usd=cost_usd,
                    duration_ms=duration_ms,
                    success=success,
                    error_message=error_message,
                    extra_data=extra_data,
                )

                session.add(usage)
                await session.commit()

                logger.debug(
                    f"API usage logged: {api_provider}/{model} - "
                    f"{total_tokens} tokens, ${cost_usd}"
                )

                return usage

        except Exception as e:
            logger.error(f"Failed to log API usage: {e}")
            return None

    @staticmethod
    async def get_usage_stats(
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> Dict[str, Any]:
        """Get aggregated usage statistics"""
        if not start_date:
            start_date = datetime.now(timezone.utc) - timedelta(days=30)
        if not end_date:
            end_date = datetime.now(timezone.utc)

        async with get_session() as session:
            # Total stats
            total_result = await session.execute(
                select(
                    func.count(APIUsage.id).label("total_requests"),
                    func.sum(APIUsage.total_tokens).label("total_tokens"),
                    func.sum(APIUsage.cost_usd).label("total_cost"),
                ).where(
                    and_(
                        APIUsage.created_at >= start_date,
                        APIUsage.created_at <= end_date,
                    )
                )
            )
            total_row = total_result.first()

            # Stats by model
            model_result = await session.execute(
                select(
                    APIUsage.model,
                    func.count(APIUsage.id).label("requests"),
                    func.sum(APIUsage.total_tokens).label("tokens"),
                    func.sum(APIUsage.cost_usd).label("cost"),
                ).where(
                    and_(
                        APIUsage.created_at >= start_date,
                        APIUsage.created_at <= end_date,
                    )
                ).group_by(APIUsage.model)
                .order_by(func.sum(APIUsage.cost_usd).desc())
            )
            model_stats = [
                {
                    "model": row.model,
                    "requests": row.requests,
                    "tokens": row.tokens or 0,
                    "cost": float(row.cost or 0),
                }
                for row in model_result
            ]

            # Stats by operation type
            operation_result = await session.execute(
                select(
                    APIUsage.operation_type,
                    func.count(APIUsage.id).label("requests"),
                    func.sum(APIUsage.total_tokens).label("tokens"),
                    func.sum(APIUsage.cost_usd).label("cost"),
                ).where(
                    and_(
                        APIUsage.created_at >= start_date,
                        APIUsage.created_at <= end_date,
                    )
                ).group_by(APIUsage.operation_type)
                .order_by(func.sum(APIUsage.cost_usd).desc())
            )
            operation_stats = [
                {
                    "operation": row.operation_type,
                    "requests": row.requests,
                    "tokens": row.tokens or 0,
                    "cost": float(row.cost or 0),
                }
                for row in operation_result
            ]

            # Daily stats for the period
            daily_result = await session.execute(
                select(
                    func.date_trunc('day', APIUsage.created_at).label("date"),
                    func.count(APIUsage.id).label("requests"),
                    func.sum(APIUsage.total_tokens).label("tokens"),
                    func.sum(APIUsage.cost_usd).label("cost"),
                ).where(
                    and_(
                        APIUsage.created_at >= start_date,
                        APIUsage.created_at <= end_date,
                    )
                ).group_by(func.date_trunc('day', APIUsage.created_at))
                .order_by(func.date_trunc('day', APIUsage.created_at))
            )
            daily_stats = [
                {
                    "date": row.date.isoformat() if row.date else None,
                    "requests": row.requests,
                    "tokens": row.tokens or 0,
                    "cost": float(row.cost or 0),
                }
                for row in daily_result
            ]

            return {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "totals": {
                    "requests": total_row.total_requests or 0,
                    "tokens": total_row.total_tokens or 0,
                    "cost": float(total_row.total_cost or 0),
                },
                "by_model": model_stats,
                "by_operation": operation_stats,
                "daily": daily_stats,
            }

    @staticmethod
    async def get_recent_usage(limit: int = 50) -> list:
        """Get recent API usage records"""
        async with get_session() as session:
            result = await session.execute(
                select(APIUsage)
                .order_by(APIUsage.created_at.desc())
                .limit(limit)
            )
            records = result.scalars().all()

            return [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "api_provider": r.api_provider,
                    "model": r.model,
                    "operation_type": r.operation_type,
                    "input_tokens": r.input_tokens,
                    "output_tokens": r.output_tokens,
                    "total_tokens": r.total_tokens,
                    "cost_usd": float(r.cost_usd) if r.cost_usd else 0,
                    "duration_ms": r.duration_ms,
                    "success": r.success,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in records
            ]


def track_openai_usage(operation_type: str):
    """Decorator to track OpenAI API usage"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                raise
            finally:
                _duration_ms = int((time.time() - start_time) * 1000)

                # Try to extract usage info from the result
                # This depends on how OpenAI client returns data
                # You may need to adapt this based on your actual implementation

        return wrapper
    return decorator
