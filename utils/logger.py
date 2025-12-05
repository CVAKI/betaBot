"""
Logging Configuration and Management
Handles all logging for the β-bot system
"""

import logging
import os
from datetime import datetime
from typing import Optional
import config

# Global loggers dictionary
_loggers = {}


def setup_logger(name: str, log_file: Optional[str] = None, level=logging.INFO) -> logging.Logger:
    """
    Setup and configure a logger

    Args:
        name: Name of the logger
        log_file: Optional specific log file path
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    # Return existing logger if already setup
    if name in _loggers:
        return _loggers[name]

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level if config.VERBOSE_LOGGING else logging.INFO)

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s'
    )

    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file is None:
        # Default log file based on logger name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(config.GAME_LOGS_DIR, f"{name}_{timestamp}.log")

    # Ensure directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

    # Store logger
    _loggers[name] = logger

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get existing logger or create new one"""
    if name in _loggers:
        return _loggers[name]
    return setup_logger(name)


# Convenience functions
def log_info(message: str, logger_name: str = 'main'):
    """Log info message"""
    logger = get_logger(logger_name)
    logger.info(message)


def log_warning(message: str, logger_name: str = 'main'):
    """Log warning message"""
    logger = get_logger(logger_name)
    logger.warning(message)


def log_error(message: str, logger_name: str = 'main'):
    """Log error message"""
    logger = get_logger(logger_name)
    logger.error(message)


def log_debug(message: str, logger_name: str = 'main'):
    """Log debug message"""
    logger = get_logger(logger_name)
    logger.debug(message)


def log_critical(message: str, logger_name: str = 'main'):
    """Log critical message"""
    logger = get_logger(logger_name)
    logger.critical(message)


def log_exception(exception: Exception, logger_name: str = 'main'):
    """Log exception with traceback"""
    logger = get_logger(logger_name)
    logger.exception(f"Exception occurred: {exception}")


def close_all_loggers():
    """Close all logger handlers"""
    for logger in _loggers.values():
        for handler in logger.handlers:
            handler.close()
    _loggers.clear()