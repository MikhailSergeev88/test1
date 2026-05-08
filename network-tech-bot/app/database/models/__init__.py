"""
SQLAlchemy models for the application database.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class UserRole(str, Enum):
    """User role enumeration."""

    EMPLOYEE = "employee"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User status enumeration."""

    PENDING = "pending"
    ACTIVE = "active"
    BANNED = "banned"
    REJECTED = "rejected"


class User(Base):
    """User model for storing Telegram user information."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role"), default=UserRole.EMPLOYEE
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, name="user_status"), default=UserStatus.PENDING
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_seen_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="user")
    access_requests: Mapped[list["AccessRequest"]] = relationship(
        "AccessRequest", back_populates="user"
    )

    __table_args__ = (
        Index("ix_users_status", "status"),
        Index("ix_users_role", "role"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, status={self.status})>"


class AccessRequest(Base):
    """Model for storing user access requests."""

    __tablename__ = "access_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        SQLEnum(UserStatus, name="access_request_status"), default=UserStatus.PENDING
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    reviewed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    review_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="access_requests")

    __table_args__ = (Index("ix_access_requests_user_id", "user_id"),)

    def __repr__(self) -> str:
        return f"<AccessRequest(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Document(Base):
    """Model for storing indexed documents."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    google_doc_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)  # google_doc, pdf, docx, txt
    file_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)
    is_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        String(1000), nullable=True
    )  # Store as JSON string

    # Relationships
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_documents_is_indexed", "is_indexed"),)

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title='{self.title}')>"


class DocumentChunk(Base):
    """Model for storing document chunks with embeddings."""

    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[bytes]] = mapped_column(
        String(2048), nullable=True
    )  # Stored as bytes, will use pgvector in migration
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        String(1000), nullable=True
    )  # Store as JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_document_chunk"),
        Index("ix_document_chunks_document_id", "document_id"),
    )

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index})>"


class Message(Base):
    """Model for storing user messages and bot responses."""

    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    message_type: Mapped[str] = mapped_column(String(50), default="text")  # text, voice, image, document
    sources: Mapped[Optional[dict]] = mapped_column(
        String(2000), nullable=True
    )  # Store cited sources as JSON string
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="messages")

    __table_args__ = (
        Index("ix_messages_user_id", "user_id"),
        Index("ix_messages_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, user_id={self.user_id})>"


class LogEntry(Base):
    """Model for storing application logs."""

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    logger_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    extra_data: Mapped[Optional[dict]] = mapped_column(
        String(2000), nullable=True
    )  # Store as JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_logs_level", "level"),
        Index("ix_logs_created_at", "created_at"),
        Index("ix_logs_user_id", "user_id"),
    )

    def __repr__(self) -> str:
        return f"<LogEntry(id={self.id}, level={self.level})>"


class AuditLog(Base):
    """Model for storing audit logs of admin actions."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=True)  # user, document, etc.
    target_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    old_value: Mapped[Optional[dict]] = mapped_column(
        String(2000), nullable=True
    )  # Store as JSON string
    new_value: Mapped[Optional[dict]] = mapped_column(
        String(2000), nullable=True
    )  # Store as JSON string
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_audit_logs_admin_user_id", "admin_user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action})>"
