"""
MINDSETHAPPYBOT - Main bot entry point
Initializes and runs the Telegram bot using aiogram 3.x
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from src.config import get_settings
from src.db.database import init_db, close_db
from src.bot.handlers import commands, messages, callbacks, feedback
from src.bot.middlewares.logging import LoggingMiddleware
from src.services.scheduler import NotificationScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to run the bot"""
    settings = get_settings()

    # Initialize bot with default properties
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Initialize dispatcher
    dp = Dispatcher()

    # Register middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # Register routers
    dp.include_router(commands.router)
    dp.include_router(feedback.router)  # Feedback router before messages for button handling
    dp.include_router(messages.router)
    dp.include_router(callbacks.router)

    # Initialize database
    logger.info("Initializing database connection...")
    await init_db()

    # Initialize scheduler
    logger.info("Initializing notification scheduler...")
    scheduler = NotificationScheduler(bot)
    await scheduler.start()

    try:
        logger.info("Starting MINDSETHAPPYBOT...")
        # Delete webhook to use long polling
        await bot.delete_webhook(drop_pending_updates=True)
        # Start polling
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down...")
        await scheduler.stop()
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
