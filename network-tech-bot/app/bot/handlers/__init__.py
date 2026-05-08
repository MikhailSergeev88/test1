"""Handlers package initialization."""

from aiogram import Dispatcher

from app.bot.handlers.commands import register_command_handlers
from app.bot.handlers.messages import register_message_handlers
from app.bot.handlers.callbacks import register_callback_handlers
from app.bot.handlers.admin import register_admin_handlers


def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers with dispatcher."""
    register_command_handlers(dp)
    register_message_handlers(dp)
    register_callback_handlers(dp)
    register_admin_handlers(dp)


__all__ = ["register_handlers"]
