"""
Configuration management for the application.
Uses pydantic-settings for environment variable validation.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Bot Configuration
    telegram_bot_token: str = Field(..., description="Telegram bot token")
    telegram_api_id: Optional[int] = Field(None, description="Telegram API ID")
    telegram_api_hash: Optional[str] = Field(None, description="Telegram API hash")

    # Qwen LLM Configuration
    qwen_api_key: str = Field(..., description="Qwen API key")
    qwen_model_name: str = Field(default="qwen-max", description="Qwen model name")
    qwen_base_url: str = Field(
        default="https://dashscope.aliyuncs.com/compatible-mode/v1",
        description="Qwen API base URL",
    )
    qwen_max_tokens: int = Field(default=2048, description="Maximum tokens in response")
    qwen_temperature: float = Field(default=0.3, description="LLM temperature")

    # Database Configuration
    database_url: str = Field(..., description="Database connection URL")
    database_pool_size: int = Field(default=10, description="Database pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")

    # Google Drive API Configuration
    google_client_id: Optional[str] = Field(None, description="Google client ID")
    google_client_secret: Optional[str] = Field(None, description="Google client secret")
    google_drive_folder_id: Optional[str] = Field(None, description="Google Drive folder ID")
    google_credentials_path: str = Field(
        default="./credentials/google_credentials.json",
        description="Path to Google credentials file",
    )

    # Admin Configuration
    admin_ids: str = Field(..., description="Comma-separated admin Telegram IDs")
    
    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: str) -> str:
        """Validate admin IDs format."""
        if not v:
            raise ValueError("ADMIN_IDS cannot be empty")
        ids = [id.strip() for id in v.split(",")]
        for id_val in ids:
            if not id_val.isdigit():
                raise ValueError(f"Invalid admin ID: {id_val}")
        return v

    # Security Configuration
    secret_key: str = Field(..., description="Secret key for sessions")
    rate_limit_per_minute: int = Field(default=10, description="Rate limit per minute")
    session_expire_hours: int = Field(default=24, description="Session expiration hours")

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file_path: str = Field(default="./logs/bot.log", description="Log file path")
    log_format: str = Field(default="json", description="Log format (json or text)")

    # Application Configuration
    app_env: str = Field(default="production", description="Application environment")
    debug: bool = Field(default=False, description="Debug mode")
    allowed_telegram_domains: str = Field(
        default="telegram.org", description="Allowed Telegram domains"
    )

    # RAG Configuration
    rag_chunk_size: int = Field(default=1000, description="RAG chunk size")
    rag_chunk_overlap: int = Field(default=200, description="RAG chunk overlap")
    rag_top_k_results: int = Field(default=5, description="Top K results for retrieval")
    rag_similarity_threshold: float = Field(
        default=0.7, description="Similarity threshold for retrieval"
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Embedding model name",
    )

    # Cache Configuration
    cache_ttl_seconds: int = Field(default=3600, description="Cache TTL in seconds")
    cache_enabled: bool = Field(default=True, description="Enable caching")

    # Scheduler Configuration
    sync_interval_hours: int = Field(default=6, description="Sync interval in hours")
    cleanup_interval_hours: int = Field(default=24, description="Cleanup interval in hours")

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"

    @property
    def parsed_admin_ids(self) -> List[int]:
        """Parse admin IDs into list of integers."""
        return [int(id.strip()) for id in self.admin_ids.split(",")]

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.debug or not self.is_production


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
