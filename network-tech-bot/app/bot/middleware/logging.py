"""
Logging middleware for the bot.
Logs all incoming messages and callback queries.
"""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from structlog import get_logger

logger = get_logger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging user interactions."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process and log incoming event."""
        start_time = time.time()
        
        # Extract event info
        event_type = type(event).__name__
        user_id = None
        content = None
        
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            content = event.text or event.caption or f"[{event.content_type}]"
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
            content = f"callback:{event.data}"
        
        # Log incoming event
        logger.info(
            "Incoming event",
            event_type=event_type,
            user_id=user_id,
            content=content[:100] if content else None,
        )
        
        # Process event
        result = await handler(event, data)
        
        # Log processing time
        processing_time = (time.time() - start_time) * 1000
        logger.debug(
            "Event processed",
            event_type=event_type,
            user_id=user_id,
            processing_time_ms=round(processing_time, 2),
        )
        
        return result
