"""
Callback query handlers for inline keyboard buttons.
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery
from structlog import get_logger

from app.database.session import AsyncSessionLocal
from app.auth.service import AuthorizationService
from app.database.models import UserRole
from app.bot.keyboards.inline import get_admin_keyboard

logger = get_logger(__name__)

router = Router()


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery) -> None:
    """Handle help button."""
    help_text = """
📚 <b>Помощь</b>

Я AI-ассистент компании Network Technologies.

<b>Как пользоваться:</b>
• Напишите свой вопрос текстом
• Я найду ответ в корпоративных регламентах
• Предоставлю цитаты и источники

<b>Важно:</b>
⚠️ Отвечаю ТОЛЬКО по загруженным документам
⚠️ Если информации нет - честно скажу об этом
"""
    await callback.answer(help_text, show_alert=True)


@router.callback_query(F.data == "support")
async def callback_support(callback: CallbackQuery) -> None:
    """Handle support button."""
    await callback.answer(
        "📞 По техническим вопросам обратитесь к администратору системы.",
        show_alert=True,
    )


@router.callback_query(F.data == "admin_users")
async def callback_admin_users(callback: CallbackQuery) -> None:
    """Handle admin users button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        users = await auth_service.get_all_users()
        
        users_text = "👥 <b>Все пользователи:</b>\n\n"
        for u in users[:15]:
            status_emoji = {"active": "✅", "pending": "⏳", "banned": "🚫", "rejected": "❌"}
            emoji = status_emoji.get(u.status.value, "❓")
            users_text += f"{emoji} {u.telegram_id} - @{u.username or 'no_username'}\n"
        
        await callback.message.edit_text(users_text, reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery) -> None:
    """Handle admin stats button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        stats = await auth_service.get_user_stats()
        
        stats_text = f"""
📊 <b>Статистика</b>

👥 Пользователи:
• Всего: {stats['total']}
• Активные: {stats['active']}
• Ожидают: {stats['pending']}
• Забанены: {stats['banned']}
• Отклонены: {stats['rejected']}
"""
        await callback.message.edit_text(stats_text, reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin_pending")
async def callback_admin_pending(callback: CallbackQuery) -> None:
    """Handle admin pending requests button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        pending = await auth_service.get_pending_requests()
        
        if not pending:
            await callback.answer("✅ Нет ожидающих заявок", show_alert=True)
            return
        
        pending_text = "📋 <b>Ожидающие заявки:</b>\n\n"
        for req in pending[:10]:
            u = req.user
            pending_text += f"⏳ {u.telegram_id} - @{u.username or 'no_username'}\n"
        
        await callback.message.edit_text(pending_text, reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin_docs")
async def callback_admin_docs(callback: CallbackQuery) -> None:
    """Handle admin documents button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        docs = await auth_service.repos.documents.get_all()
        
        docs_text = "📄 <b>Документы:</b>\n\n"
        for doc in docs[:10]:
            status = "✅" if doc.is_indexed else "⏳"
            docs_text += f"{status} {doc.title[:40]}...\n"
        
        if not docs:
            docs_text = "📄 <b>Документы:</b>\n\nНет загруженных документов."
        
        await callback.message.edit_text(docs_text, reply_markup=get_admin_keyboard())


@router.callback_query(F.data == "admin_reindex")
async def callback_admin_reindex(callback: CallbackQuery) -> None:
    """Handle admin reindex button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        # Trigger reindex (placeholder)
        await callback.message.answer("🔄 Запуск переиндексации документов...")
        # TODO: Implement actual reindex logic
        
        await callback.answer("✅ Переиндексация запущена", show_alert=True)


@router.callback_query(F.data.startswith("approve_"))
async def callback_approve(callback: CallbackQuery) -> None:
    """Handle approve user button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        target_id = int(callback.data.split("_")[1])
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        
        if not target_user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        success = await auth_service.approve_user(target_user, db_user)
        
        if success:
            await callback.answer(f"✅ Пользователь {target_id} одобрен", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при одобрении", show_alert=True)


@router.callback_query(F.data.startswith("reject_"))
async def callback_reject(callback: CallbackQuery) -> None:
    """Handle reject user button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        target_id = int(callback.data.split("_")[1])
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        
        if not target_user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        success = await auth_service.reject_user(target_user, db_user)
        
        if success:
            await callback.answer(f"❌ Пользователь {target_id} отклонен", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при отклонении", show_alert=True)


@router.callback_query(F.data.startswith("ban_"))
async def callback_ban(callback: CallbackQuery) -> None:
    """Handle ban user button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        target_id = int(callback.data.split("_")[1])
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        
        if not target_user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        success = await auth_service.ban_user(target_user, db_user)
        
        if success:
            await callback.answer(f"🚫 Пользователь {target_id} забанен", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при бане", show_alert=True)


@router.callback_query(F.data.startswith("unban_"))
async def callback_unban(callback: CallbackQuery) -> None:
    """Handle unban user button."""
    user = callback.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await callback.answer("❌ Нет прав", show_alert=True)
            return
        
        target_id = int(callback.data.split("_")[1])
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        
        if not target_user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        success = await auth_service.unban_user(target_user, db_user)
        
        if success:
            await callback.answer(f"🔓 Пользователь {target_id} разбанен", show_alert=True)
        else:
            await callback.answer("❌ Ошибка при разбане", show_alert=True)


@router.callback_query(F.data == "cancel")
async def callback_cancel(callback: CallbackQuery) -> None:
    """Handle cancel button."""
    await callback.message.delete()
    await callback.answer()
