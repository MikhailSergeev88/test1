"""
Main application entry point.
Initializes and runs the Telegram bot.
"""

import asyncio
import signal
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from structlog import get_logger

from app.config.settings import settings
from app.logging.logger import setup_logging
from app.database.session import init_db, close_db
from app.llm import shutdown_llm_provider
from app.rag import initialize_rag
from app.bot.handlers import register_handlers
from app.bot.middleware import setup_middleware


logger = get_logger(__name__)

# Global bot and dispatcher
bot: Optional[Bot] = None
dp: Optional[Dispatcher] = None


async def on_startup() -> None:
    """Called when bot starts."""
    logger.info("Starting up bot...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize RAG pipeline
    await initialize_rag()
    logger.info("RAG pipeline initialized")
    
    # Get bot info
    bot_info = await bot.get_me()
    logger.info(f"Bot started", username=bot_info.username, name=bot_info.first_name)


async def on_shutdown() -> None:
    """Called when bot shuts down."""
    logger.info("Shutting down bot...")
    
    # Close LLM provider
    await shutdown_llm_provider()
    
    # Close database connections
    await close_db()
    
    # Close bot session
    await bot.session.close()
    
    logger.info("Bot shut down")


def create_bot() -> Bot:
    """Create bot instance."""
    return Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Create dispatcher instance."""
    dp = Dispatcher()
    
    # Register middleware
    setup_middleware(dp)
    
    # Register handlers
    register_handlers(dp)
    
    return dp


async def main() -> None:
    """Main function to run the bot."""
    global bot, dp
    
    # Setup logging
    setup_logging(
        log_level=settings.log_level,
        log_file_path=settings.log_file_path,
        log_format=settings.log_format,
        is_debug=settings.is_debug,
    )
    
    logger.info("Initializing Network Technologies AI Assistant...")
    
    # Create bot and dispatcher
    bot = create_bot()
    dp = create_dispatcher()
    
    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(
            sig,
            lambda: asyncio.create_task(shutdown()),
        )
    
    # Call startup hook
    await on_startup()
    
    try:
        # Start polling
        logger.info("Starting bot polling...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error("Bot polling error", error=str(e))
        raise
    finally:
        # Call shutdown hook
        await on_shutdown()


async def shutdown() -> None:
    """Graceful shutdown."""
    logger.info("Shutdown signal received")
    
    if dp:
        await dp.emit_shutdown()
    
    if bot:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error("Fatal error", error=str(e))
        raise
