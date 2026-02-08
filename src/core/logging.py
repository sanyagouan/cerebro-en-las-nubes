from loguru import logger
import sys
from pathlib import Path


def setup_logger():
    """
    Configure loguru logger with structured output for production.
    Supports both Docker (STDOUT) and local (file) logging.
    """
    logger.remove()  # Remove default handler

    # Format for structured logs (JSON-like but readable)
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Add STDOUT handler (always active - Docker friendly)
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        colorize=False,  # Disable colors in production logs
        backtrace=True,
        diagnose=True,
    )

    # Add file handler for local development (only if running locally)
    try:
        import os

        if os.getenv("ENVIRONMENT") != "production":
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)

            logger.add(
                logs_dir / "cerebro_{time:YYYY-MM-DD}.log",
                format=log_format,
                level="DEBUG",
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                backtrace=True,
                diagnose=True,
            )
    except Exception:
        pass  # Fail silently if file logging fails

    return logger


# Initialize and export logger
setup_logger()
__all__ = ["logger"]
