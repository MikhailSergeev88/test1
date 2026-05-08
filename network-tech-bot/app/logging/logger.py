"""
Logging configuration for the application.
Provides structured logging with JSON format support.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog
from structlog.types import Processor


def setup_logging(
    log_level: str = "INFO",
    log_file_path: Optional[str] = None,
    log_format: str = "json",
    is_debug: bool = False,
) -> None:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file_path: Path to log file
        log_format: Log format (json or text)
        is_debug: Debug mode flag
    """
    # Create logs directory if needed
    if log_file_path:
        log_path = Path(log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Set up processors based on format
    if log_format == "json":
        processors = setup_json_processors(is_debug)
    else:
        processors = setup_text_processors(is_debug)

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    setup_standard_logging(numeric_level, log_file_path)


def setup_json_processors(is_debug: bool) -> list[Processor]:
    """Set up JSON format processors."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if is_debug:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer())

    return processors


def setup_text_processors(is_debug: bool) -> list[Processor]:
    """Set up text format processors."""
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if is_debug:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=False))

    return processors


def setup_standard_logging(level: int, log_file_path: Optional[str]) -> None:
    """Configure standard library logging handlers."""
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (if path provided)
    if log_file_path:
        try:
            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(console_formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)
