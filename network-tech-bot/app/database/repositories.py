"""
Repository pattern for database access.
Provides clean abstraction over database operations.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    User,
    UserRole,
    UserStatus,
    AccessRequest,
    Document,
    DocumentChunk,
    Message,
    LogEntry,
    AuditLog,
)
from structlog import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Repository for User operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            status=UserStatus.PENDING,
        )
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_status(
        self, user: User, status: UserStatus
    ) -> User:
        """Update user status."""
        user.status = status
        if status == UserStatus.ACTIVE:
            user.is_active = True
        elif status in (UserStatus.BANNED, UserStatus.REJECTED):
            user.is_active = False
        await self.session.flush()
        return user

    async def update_role(self, user: User, role: UserRole) -> User:
        """Update user role."""
        user.role = role
        await self.session.flush()
        return user

    async def update_last_seen(self, user: User) -> None:
        """Update user's last seen timestamp."""
        user.last_seen_at = datetime.utcnow()
        await self.session.flush()

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        result = await self.session.execute(select(User).order_by(User.created_at.desc()))
        return list(result.scalars().all())

    async def get_users_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status."""
        result = await self.session.execute(
            select(User).where(User.status == status).order_by(User.created_at.desc())
        )
        return list(result.scalars().all())

    async def count_users(self) -> dict:
        """Count users by status."""
        result = await self.session.execute(
            select(User.status, func.count(User.id))
            .group_by(User.status)
        )
        return {status.value: count for status, count in result.all()}


class AccessRequestRepository:
    """Repository for AccessRequest operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int) -> AccessRequest:
        """Create a new access request."""
        request = AccessRequest(user_id=user_id)
        self.session.add(request)
        await self.session.flush()
        await self.session.refresh(request)
        return request

    async def get_pending_for_user(self, user_id: int) -> Optional[AccessRequest]:
        """Get pending access request for user."""
        result = await self.session.execute(
            select(AccessRequest)
            .where(AccessRequest.user_id == user_id)
            .where(AccessRequest.status == UserStatus.PENDING.value)
            .order_by(AccessRequest.requested_at.desc())
        )
        return result.scalar_one_or_none()

    async def approve(
        self, request: AccessRequest, admin_user_id: int
    ) -> AccessRequest:
        """Approve access request."""
        request.status = UserStatus.ACTIVE.value
        request.reviewed_at = datetime.utcnow()
        request.reviewed_by = admin_user_id
        await self.session.flush()
        return request

    async def reject(
        self, request: AccessRequest, admin_user_id: int, comment: Optional[str] = None
    ) -> AccessRequest:
        """Reject access request."""
        request.status = UserStatus.REJECTED.value
        request.reviewed_at = datetime.utcnow()
        request.reviewed_by = admin_user_id
        request.review_comment = comment
        await self.session.flush()
        return request

    async def get_all_pending(self) -> List[AccessRequest]:
        """Get all pending access requests."""
        result = await self.session.execute(
            select(AccessRequest)
            .where(AccessRequest.status == UserStatus.PENDING.value)
            .options(selectinload(AccessRequest.user))
            .order_by(AccessRequest.requested_at.desc())
        )
        return list(result.scalars().all())


class DocumentRepository:
    """Repository for Document operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_google_id(self, google_doc_id: str) -> Optional[Document]:
        """Get document by Google Doc ID."""
        result = await self.session.execute(
            select(Document).where(Document.google_doc_id == google_doc_id)
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> Document:
        """Create a new document."""
        document = Document(**kwargs)
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def update(self, document: Document, **kwargs) -> Document:
        """Update document."""
        for key, value in kwargs.items():
            setattr(document, key, value)
        document.updated_at = datetime.utcnow()
        await self.session.flush()
        return document

    async def mark_indexed(self, document: Document) -> None:
        """Mark document as indexed."""
        document.is_indexed = True
        document.indexed_at = datetime.utcnow()
        await self.session.flush()

    async def get_all(self) -> List[Document]:
        """Get all documents."""
        result = await self.session.execute(
            select(Document).order_by(Document.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_not_indexed(self) -> List[Document]:
        """Get documents that are not indexed."""
        result = await self.session.execute(
            select(Document).where(Document.is_indexed == False)
        )
        return list(result.scalars().all())

    async def delete(self, document: Document) -> None:
        """Delete document."""
        await self.session.delete(document)
        await self.session.flush()

    async def count(self) -> int:
        """Count total documents."""
        result = await self.session.execute(select(func.count(Document.id)))
        return result.scalar()


class DocumentChunkRepository:
    """Repository for DocumentChunk operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> DocumentChunk:
        """Create a new document chunk."""
        chunk = DocumentChunk(**kwargs)
        self.session.add(chunk)
        await self.session.flush()
        await self.session.refresh(chunk)
        return chunk

    async def bulk_create(self, chunks: List[DocumentChunk]) -> None:
        """Bulk create document chunks."""
        self.session.add_all(chunks)
        await self.session.flush()

    async def delete_by_document(self, document_id: int) -> None:
        """Delete all chunks for a document."""
        await self.session.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        )
        await self.session.flush()

    async def search_by_content(self, query: str, limit: int = 10) -> List[DocumentChunk]:
        """Search chunks by content (full-text search fallback)."""
        result = await self.session.execute(
            select(DocumentChunk)
            .where(DocumentChunk.content.ilike(f"%{query}%"))
            .limit(limit)
        )
        return list(result.scalars().all())


class MessageRepository:
    """Repository for Message operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Message:
        """Create a new message."""
        message = Message(**kwargs)
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_user_messages(
        self, user_id: int, limit: int = 50
    ) -> List[Message]:
        """Get user's messages."""
        result = await self.session.execute(
            select(Message)
            .where(Message.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def count_total(self) -> int:
        """Count total messages."""
        result = await self.session.execute(select(func.count(Message.id)))
        return result.scalar()


class AuditLogRepository:
    """Repository for AuditLog operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> AuditLog:
        """Create a new audit log entry."""
        log_entry = AuditLog(**kwargs)
        self.session.add(log_entry)
        await self.session.flush()
        await self.session.refresh(log_entry)
        return log_entry

    async def get_admin_logs(
        self, admin_user_id: int, limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs for admin."""
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.admin_user_id == admin_user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class RepositoryContainer:
    """Container for all repositories."""

    def __init__(self, session: AsyncSession):
        self.users = UserRepository(session)
        self.access_requests = AccessRequestRepository(session)
        self.documents = DocumentRepository(session)
        self.document_chunks = DocumentChunkRepository(session)
        self.messages = MessageRepository(session)
        self.audit_logs = AuditLogRepository(session)
