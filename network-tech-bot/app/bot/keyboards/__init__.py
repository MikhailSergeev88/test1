"""Keyboards package initialization."""

from app.bot.keyboards.inline import (
    get_admin_keyboard,
    get_pending_keyboard,
    get_main_keyboard,
)

__all__ = [
    "get_admin_keyboard",
    "get_pending_keyboard",
    "get_main_keyboard",
]
