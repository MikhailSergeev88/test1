"""
Authentication middleware for the bot.
Checks user access before processing messages.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.database.session import AsyncSessionLocal
from app.auth.service import AuthorizationService
from app.bot.keyboards.inline import get_pending_keyboard

logger = get_logger(__name__)


class AuthMiddleware(BaseMiddleware):
    """Middleware for checking user authentication and access."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """Process incoming event."""
        # Get user from event
        user_obj = None
        if isinstance(event, Message):
            user_obj = event.from_user
        elif isinstance(event, CallbackQuery):
            user_obj = event.from_user
        
        if not user_obj:
            return await handler(event, data)
        
        telegram_id = user_obj.id
        
        # Skip auth for admin commands in private chat with admins
        if isinstance(event, Message) and event.text:
            if event.text.startswith('/'):
                # Will be handled by command handlers
                return await handler(event, data)
        
        # Get database session
        async with AsyncSessionLocal() as session:
            auth_service = AuthorizationService(session)
            
            # Get or create user
            user, is_new = await auth_service.get_or_create_user(
                telegram_id=telegram_id,
                username=user_obj.username,
                first_name=user_obj.first_name,
                last_name=user_obj.last_name,
            )
            
            # Add user to handler data
            data["user"] = user
            data["is_new_user"] = is_new
            
            # Check access
            has_access, reason = await auth_service.check_access(user)
            
            if not has_access:
                # Send access denied message for new events
                if isinstance(event, Message):
                    if user.status.value == "pending":
                        await event.answer(
                            f"⏳ {reason}\n\n"
                            f"Ваша заявка отправлена администраторам.\n"
                            f"Ожидайте подтверждения.",
                            reply_markup=get_pending_keyboard(),
                        )
                    else:
                        await event.answer(f"❌ {reason}")
                    return None
                elif isinstance(event, CallbackQuery):
                    await event.answer(f"❌ {reason}", show_alert=True)
                    return None
            
            # Update last seen
            await auth_service.repos.users.update_last_seen(user)
        
        return await handler(event, data)
