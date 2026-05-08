"""
Authorization service for user management.
Handles user registration, approval, and access control.
"""

from typing import Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from app.config.settings import settings
from app.database.models import User, UserRole, UserStatus, AccessRequest
from app.database.repositories import RepositoryContainer
from app.logging.logger import get_logger as get_app_logger

logger = get_app_logger(__name__)


class AuthorizationService:
    """Service for handling user authorization."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repos = RepositoryContainer(session)

    async def get_or_create_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> Tuple[User, bool]:
        """
        Get existing user or create new one.

        Returns:
            Tuple of (user, is_new)
        """
        user = await self.repos.users.get_by_telegram_id(telegram_id)
        
        if user:
            # Update user info if changed
            if username and username != user.username:
                user.username = username
            if first_name and first_name != user.first_name:
                user.first_name = first_name
            if last_name and last_name != user.last_name:
                user.last_name = last_name
            
            await self.repos.users.update_last_seen(user)
            return user, False

        # Check if this should be auto-approved admin
        if telegram_id in settings.parsed_admin_ids:
            user = await self.repos.users.create(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            user.role = UserRole.ADMIN
            user.status = UserStatus.ACTIVE
            user.is_active = True
            logger.info("Auto-registered admin user", telegram_id=telegram_id)
            return user, True

        # Create new pending user
        user = await self.repos.users.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        
        # Create access request
        await self.repos.access_requests.create(user.id)
        
        logger.info("New user registered, awaiting approval", telegram_id=telegram_id)
        return user, True

    async def check_access(self, user: User) -> Tuple[bool, str]:
        """
        Check if user has access.

        Returns:
            Tuple of (has_access, reason)
        """
        if not user.is_active:
            return False, "Ваш аккаунт деактивирован"

        if user.status == UserStatus.BANNED:
            return False, "Ваш аккаунт заблокирован"

        if user.status == UserStatus.PENDING:
            return False, "Ваша заявка на доступ ожидает подтверждения администратора"

        if user.status == UserStatus.REJECTED:
            return False, "Ваша заявка на доступ была отклонена"

        if user.status == UserStatus.ACTIVE:
            return True, "Доступ разрешен"

        return False, "Неизвестный статус пользователя"

    async def approve_user(
        self,
        user: User,
        admin_user: User,
        comment: Optional[str] = None,
    ) -> bool:
        """Approve user access."""
        if admin_user.role != UserRole.ADMIN:
            logger.warning("Non-admin tried to approve user", admin_id=admin_user.telegram_id)
            return False

        # Update user status
        await self.repos.users.update_status(user, UserStatus.ACTIVE)

        # Update access request
        pending_request = await self.repos.access_requests.get_pending_for_user(user.id)
        if pending_request:
            await self.repos.access_requests.approve(pending_request, admin_user.id)

        # Log audit
        await self.repos.audit_logs.create(
            admin_user_id=admin_user.id,
            action="approve_user",
            target_type="user",
            target_id=user.id,
            new_value={"status": UserStatus.ACTIVE.value, "comment": comment},
        )

        logger.info(
            "User approved",
            user_id=user.id,
            telegram_id=user.telegram_id,
            admin_id=admin_user.telegram_id,
        )
        return True

    async def reject_user(
        self,
        user: User,
        admin_user: User,
        comment: Optional[str] = None,
    ) -> bool:
        """Reject user access."""
        if admin_user.role != UserRole.ADMIN:
            logger.warning("Non-admin tried to reject user", admin_id=admin_user.telegram_id)
            return False

        # Update user status
        await self.repos.users.update_status(user, UserStatus.REJECTED)

        # Update access request
        pending_request = await self.repos.access_requests.get_pending_for_user(user.id)
        if pending_request:
            await self.repos.access_requests.reject(pending_request, admin_user.id, comment)

        # Log audit
        await self.repos.audit_logs.create(
            admin_user_id=admin_user.id,
            action="reject_user",
            target_type="user",
            target_id=user.id,
            new_value={"status": UserStatus.REJECTED.value, "comment": comment},
        )

        logger.info(
            "User rejected",
            user_id=user.id,
            telegram_id=user.telegram_id,
            admin_id=admin_user.telegram_id,
        )
        return True

    async def ban_user(
        self,
        user: User,
        admin_user: User,
        comment: Optional[str] = None,
    ) -> bool:
        """Ban user."""
        if admin_user.role != UserRole.ADMIN:
            logger.warning("Non-admin tried to ban user", admin_id=admin_user.telegram_id)
            return False

        old_status = user.status.value

        # Update user status
        await self.repos.users.update_status(user, UserStatus.BANNED)

        # Log audit
        await self.repos.audit_logs.create(
            admin_user_id=admin_user.id,
            action="ban_user",
            target_type="user",
            target_id=user.id,
            old_value={"status": old_status},
            new_value={"status": UserStatus.BANNED.value, "comment": comment},
        )

        logger.info(
            "User banned",
            user_id=user.id,
            telegram_id=user.telegram_id,
            admin_id=admin_user.telegram_id,
        )
        return True

    async def unban_user(
        self,
        user: User,
        admin_user: User,
    ) -> bool:
        """Unban user."""
        if admin_user.role != UserRole.ADMIN:
            logger.warning("Non-admin tried to unban user", admin_id=admin_user.telegram_id)
            return False

        # Update user status
        await self.repos.users.update_status(user, UserStatus.ACTIVE)

        # Log audit
        await self.repos.audit_logs.create(
            admin_user_id=admin_user.id,
            action="unban_user",
            target_type="user",
            target_id=user.id,
            new_value={"status": UserStatus.ACTIVE.value},
        )

        logger.info(
            "User unbanned",
            user_id=user.id,
            telegram_id=user.telegram_id,
            admin_id=admin_user.telegram_id,
        )
        return True

    async def is_admin(self, user: User) -> bool:
        """Check if user is admin."""
        return user.role == UserRole.ADMIN and user.status == UserStatus.ACTIVE

    async def get_pending_requests(self) -> list[AccessRequest]:
        """Get all pending access requests."""
        return await self.repos.access_requests.get_all_pending()

    async def get_all_users(self) -> list[User]:
        """Get all users."""
        return await self.repos.users.get_all_users()

    async def get_user_stats(self) -> dict:
        """Get user statistics."""
        counts = await self.repos.users.count_users()
        total = sum(counts.values())
        return {
            "total": total,
            "active": counts.get(UserStatus.ACTIVE.value, 0),
            "pending": counts.get(UserStatus.PENDING.value, 0),
            "banned": counts.get(UserStatus.BANNED.value, 0),
            "rejected": counts.get(UserStatus.REJECTED.value, 0),
        }
