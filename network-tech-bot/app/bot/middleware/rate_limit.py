"""
Rate limiting middleware for the bot.
Prevents spam and flood attacks.
"""

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from structlog import get_logger

from app.config.settings import settings

logger = get_logger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware for rate limiting user requests."""

    def __init__(self):
        self._requests: Dict[int, list] = {}
        self._rate_limit = settings.rate_limit_per_minute

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process incoming message with rate limiting."""
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id
        current_time = time.time()
        
        # Initialize user request history
        if user_id not in self._requests:
            self._requests[user_id] = []
        
        # Clean old requests (older than 1 minute)
        self._requests[user_id] = [
            req_time for req_time in self._requests[user_id]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        if len(self._requests[user_id]) >= self._rate_limit:
            logger.warning(
                "Rate limit exceeded",
                user_id=user_id,
                requests_count=len(self._requests[user_id]),
            )
            await event.answer(
                "⚠️ Слишком много запросов. Пожалуйста, подождите немного.",
                show_alert=True,
            )
            return None
        
        # Record this request
        self._requests[user_id].append(current_time)
        
        return await handler(event, data)

    def cleanup(self) -> None:
        """Cleanup old request records."""
        current_time = time.time()
        for user_id in list(self._requests.keys()):
            self._requests[user_id] = [
                req_time for req_time in self._requests[user_id]
                if current_time - req_time < 60
            ]
            if not self._requests[user_id]:
                del self._requests[user_id]
