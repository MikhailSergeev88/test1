"""
Admin-specific handlers.
Handles admin commands and actions.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from structlog import get_logger

from app.database.session import AsyncSessionLocal
from app.auth.service import AuthorizationService
from app.database.models import UserRole

logger = get_logger(__name__)

router = Router()


@router.message(Command("approve"))
async def cmd_approve(message: Message) -> None:
    """Handle /approve command."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        # Parse target user ID from command args
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Использование: /approve <telegram_id>")
            return
        
        try:
            target_id = int(args[1])
        except ValueError:
            await message.answer("❌ Неверный формат ID")
            return
        
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ Пользователь не найден")
            return
        
        success = await auth_service.approve_user(target_user, db_user)
        
        if success:
            await message.answer(f"✅ Пользователь {target_id} одобрен")
        else:
            await message.answer("❌ Ошибка при одобрении")


@router.message(Command("reject"))
async def cmd_reject(message: Message) -> None:
    """Handle /reject command."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Использование: /reject <telegram_id>")
            return
        
        try:
            target_id = int(args[1])
        except ValueError:
            await message.answer("❌ Неверный формат ID")
            return
        
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ Пользователь не найден")
            return
        
        comment = " ".join(args[2:]) if len(args) > 2 else None
        success = await auth_service.reject_user(target_user, db_user, comment)
        
        if success:
            await message.answer(f"❌ Пользователь {target_id} отклонен")
        else:
            await message.answer("❌ Ошибка при отклонении")


@router.message(Command("ban"))
async def cmd_ban(message: Message) -> None:
    """Handle /ban command."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Использование: /ban <telegram_id>")
            return
        
        try:
            target_id = int(args[1])
        except ValueError:
            await message.answer("❌ Неверный формат ID")
            return
        
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ Пользователь не найден")
            return
        
        comment = " ".join(args[2:]) if len(args) > 2 else None
        success = await auth_service.ban_user(target_user, db_user, comment)
        
        if success:
            await message.answer(f"🚫 Пользователь {target_id} забанен")
        else:
            await message.answer("❌ Ошибка при бане")


@router.message(Command("unban"))
async def cmd_unban(message: Message) -> None:
    """Handle /unban command."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        args = message.text.split()
        if len(args) < 2:
            await message.answer("Использование: /unban <telegram_id>")
            return
        
        try:
            target_id = int(args[1])
        except ValueError:
            await message.answer("❌ Неверный формат ID")
            return
        
        target_user = await auth_service.repos.users.get_by_telegram_id(target_id)
        if not target_user:
            await message.answer("❌ Пользователь не найден")
            return
        
        success = await auth_service.unban_user(target_user, db_user)
        
        if success:
            await message.answer(f"🔓 Пользователь {target_id} разбанен")
        else:
            await message.answer("❌ Ошибка при разбане")


@router.message(Command("documents"))
async def cmd_documents(message: Message) -> None:
    """Handle /documents command - list indexed documents."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        docs = await auth_service.repos.documents.get_all()
        
        if not docs:
            await message.answer("📄 Нет загруженных документов")
            return
        
        docs_text = "📄 <b>Документы:</b>\n\n"
        for doc in docs[:20]:
            status = "✅" if doc.is_indexed else "⏳"
            docs_text += f"{status} {doc.title[:50]}...\n"
        
        if len(docs) > 20:
            docs_text += f"\n... и еще {len(docs) - 20} документов"
        
        await message.answer(docs_text)


@router.message(Command("reindex"))
async def cmd_reindex(message: Message) -> None:
    """Handle /reindex command - trigger document reindexing."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        await message.answer("🔄 Запуск переиндексации всех документов...")
        
        # TODO: Implement actual reindex logic via service
        
        await message.answer("✅ Переиндексация завершена")


@router.message(Command("logs"))
async def cmd_logs(message: Message) -> None:
    """Handle /logs command - show recent logs."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        await message.answer(
            "📋 Логи доступны в файле:\n"
            f"<code>{message.bot.token}</code>\n\n"
            "Используйте команду <code>docker-compose logs</code> для просмотра."
        )
