"""
Inline keyboards for the bot.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Get admin panel keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users"),
            InlineKeyboardButton(text="📄 Документы", callback_data="admin_docs"),
        ],
        [
            InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton(text="📋 Заявки", callback_data="admin_pending"),
        ],
        [
            InlineKeyboardButton(text="🔄 Переиндексация", callback_data="admin_reindex"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pending_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard for pending users."""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data="approve_me"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Get main user keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
            InlineKeyboardButton(text="📞 Поддержка", callback_data="support"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_user_action_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for user actions (admin view)."""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}"),
        ],
        [
            InlineKeyboardButton(text="🚫 Забанить", callback_data=f"ban_{user_id}"),
            InlineKeyboardButton(text="🔓 Разбанить", callback_data=f"unban_{user_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_document_action_keyboard(doc_id: int) -> InlineKeyboardMarkup:
    """Get keyboard for document actions."""
    keyboard = [
        [
            InlineKeyboardButton(text="🔄 Переиндексировать", callback_data=f"reindex_doc_{doc_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_doc_{doc_id}"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
