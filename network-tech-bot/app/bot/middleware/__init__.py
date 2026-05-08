"""Middleware package initialization."""

from app.bot.middleware.auth import AuthMiddleware
from app.bot.middleware.rate_limit import RateLimitMiddleware
from app.bot.middleware.logging import LoggingMiddleware


def setup_middleware(dp) -> None:
    """Setup all middleware for dispatcher."""
    # Auth middleware - check user access
    dp.message.outer_middleware(AuthMiddleware())
    dp.callback_query.outer_middleware(AuthMiddleware())
    
    # Rate limit middleware
    dp.message.middleware(RateLimitMiddleware())
    
    # Logging middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())


__all__ = [
    "AuthMiddleware",
    "RateLimitMiddleware", 
    "LoggingMiddleware",
    "setup_middleware",
]
