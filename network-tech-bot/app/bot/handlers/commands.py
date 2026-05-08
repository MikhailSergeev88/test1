"""
Command handlers for the bot.
Handles /start, /help, /admin and other slash commands.
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.database.session import AsyncSessionLocal
from app.auth.service import AuthorizationService
from app.bot.keyboards.inline import get_admin_keyboard, get_main_keyboard
from app.database.models import UserRole

logger = get_logger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user, is_new = await auth_service.get_or_create_user(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        
        if db_user.role == UserRole.ADMIN and db_user.status.value == "active":
            keyboard = get_admin_keyboard()
            await message.answer(
                f"👋 <b>Добро пожаловать, {user.first_name}!</b>\n\n"
                f"Я AI-ассистент компании Network Technologies.\n\n"
                f"Я могу отвечать на вопросы по корпоративным регламентам.\n"
                f"Просто напишите мне свой вопрос.\n\n"
                f"<i>Вы администратор - вам доступна панель управления.</i>",
                reply_markup=keyboard,
            )
        elif db_user.status.value == "pending":
            await message.answer(
                f"👋 <b>Добро пожаловать, {user.first_name}!</b>\n\n"
                f"Ваша заявка на доступ отправлена администраторам.\n"
                f"Ожидайте подтверждения.",
                reply_markup=get_main_keyboard(),
            )
        elif db_user.status.value == "active":
            await message.answer(
                f"👋 <b>Добро пожаловать, {user.first_name}!</b>\n\n"
                f"Я AI-ассистент компании Network Technologies.\n\n"
                f"Я могу отвечать на вопросы по корпоративным регламентам.\n"
                f"Просто напишите мне свой вопрос.",
                reply_markup=get_main_keyboard(),
            )
        else:
            await message.answer(
                f"❌ <b>Доступ запрещен</b>\n\n"
                f"{db_user.status.value}",
            )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    help_text = """
📚 <b>Помощь - AI Ассистент Network Technologies</b>

Я помогаю сотрудникам находить информацию в корпоративных регламентах.

<b>Как пользоваться:</b>
• Просто напишите свой вопрос текстом
• Можно отправить голосовое сообщение
• Можно отправить скриншот или фото документа
• Можно отправить файл (PDF, DOCX, TXT)

<b>Что я умею:</b>
✅ Отвечать на вопросы по регламентам
✅ Цитировать источники информации
✅ Распознавать голосовые сообщения
✅ Читать текст с изображений

<b>Важно:</b>
⚠️ Я отвечаю ТОЛЬКО на основе загруженных документов
⚠️ Если информации нет в регламентах, я честно скажу об этом

<b>Команды:</b>
/start - Запустить бота
/help - Эта справка
/admin - Панель администратора (для админов)
"""
    await message.answer(help_text)


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """Handle /admin command - show admin panel."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        if db_user.status.value != "active":
            await message.answer("❌ Ваш аккаунт не активен")
            return
        
        stats = await auth_service.get_user_stats()
        
        admin_text = f"""
🔧 <b>Панель администратора</b>

📊 <b>Статистика:</b>
• Всего пользователей: {stats['total']}
• Активные: {stats['active']}
• Ожидают: {stats['pending']}
• Забанены: {stats['banned']}

Выберите действие:
"""
        await message.answer(admin_text, reply_markup=get_admin_keyboard())


@router.message(Command("users"))
async def cmd_users(message: Message) -> None:
    """Handle /users command - list all users."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        users = await auth_service.get_all_users()
        
        users_text = "👥 <b>Пользователи:</b>\n\n"
        for u in users[:20]:  # Limit to 20
            status_emoji = {"active": "✅", "pending": "⏳", "banned": "🚫", "rejected": "❌"}
            emoji = status_emoji.get(u.status.value, "❓")
            users_text += f"{emoji} {u.telegram_id} - @{u.username or 'no_username'} ({u.status.value})\n"
        
        if len(users) > 20:
            users_text += f"\n... и еще {len(users) - 20} пользователей"
        
        await message.answer(users_text)


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Handle /stats command - show statistics."""
    user = message.from_user
    
    async with AsyncSessionLocal() as session:
        auth_service = AuthorizationService(session)
        db_user = await auth_service.repos.users.get_by_telegram_id(user.id)
        
        if not db_user or db_user.role != UserRole.ADMIN:
            await message.answer("❌ У вас нет прав администратора")
            return
        
        stats = await auth_service.get_user_stats()
        
        stats_text = f"""
📊 <b>Статистика системы</b>

👥 <b>Пользователи:</b>
• Всего: {stats['total']}
• Активные: {stats['active']}
• Ожидают подтверждения: {stats['pending']}
• Забанены: {stats['banned']}
• Отклонены: {stats['rejected']}

📈 <b>Документы:</b>
• Всего: TBD
• Проиндексировано: TBD
"""
        await message.answer(stats_text)
