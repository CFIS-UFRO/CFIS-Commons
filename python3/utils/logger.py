# Standard libraries
import logging
import sys
import traceback
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Union, Optional, Any 
import re

# Third-party libraries
import colorlog
import colorama

# Initialize colorama for Windows compatibility
colorama.init()

# Main class
class Logger:
    """
    Centralized logger.
    """

    @staticmethod
    def get_logger(name: Optional[str] = None,
                   level: int = logging.DEBUG,
                   file_path: Optional[Union[str, Path]] = None,
                   file_max_bytes: int = 100 * 1024, # 100 KB
                   file_backup_count: int = 1
                   ) -> logging.Logger:
        """
        Retrieves an existing configured logger or configures a new one.

        If a logger with the given name already exists and has handlers, it's returned.
        Otherwise, a new logger is configured with optional rotating file logging.

        Args:
            name (str | None, optional): The name for the logger instance.
                                         If None, defaults to 'logger'. Defaults to None.
            level (int, optional): The minimum logging level. Defaults to logging.DEBUG.
            file_path (str | Path | None, optional): If provided, logs will also be
                                                    written to this file. Defaults to None.
            file_max_bytes (int, optional): Max size in bytes for the log file
                                            before rotation. Defaults to 100KB.
            file_backup_count (int, optional): Number of backup log files to keep.
                                               Defaults to 1.

        Returns:
            logging.Logger: A configured logger instance.
        """

        # Use provided name or default to 'logger'
        effective_name = name if name is not None else "logger"
        logger_to_configure = logging.getLogger(effective_name)

        # If logger already has handlers, return it as-is
        if logger_to_configure.hasHandlers():
            return logger_to_configure

        # Configure the new logger
        logger_to_configure.setLevel(level)

        # Formatters
        separator = '>' if sys.platform == 'win32' else '»' # Some Windows versions don't support '»'
        log_format = f'[%(asctime)s][%(name)s][%(levelname).1s] {separator} %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        level_log_colors = {
            'DEBUG':    'cyan', 'INFO':     'green', 'WARNING':  'yellow',
            'ERROR':    'red', 'CRITICAL': 'red,bold',
        }
        console_formatter = colorlog.ColoredFormatter(
            f'%(log_color)s{log_format}%(reset)s',
            datefmt=date_format, log_colors=level_log_colors, reset=True
        )

        # Console Handlers
        # Messages that are < ERROR go to stdout
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(console_formatter)
        stdout_handler.addFilter(lambda record: record.levelno < logging.ERROR)
        logger_to_configure.addHandler(stdout_handler)
        # Messages that are >= ERROR go to stderr
        stderr_handler = logging.StreamHandler(sys.stderr)
        stderr_handler.setFormatter(console_formatter)
        stderr_handler.setLevel(logging.ERROR)
        logger_to_configure.addHandler(stderr_handler)

        # Optional File Handler
        if file_path is not None:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=file_path, maxBytes=file_max_bytes,
                backupCount=file_backup_count, encoding='utf-8'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(level)
            logger_to_configure.addHandler(file_handler)

        # Prevent propagation for non-root loggers
        if logger_to_configure.name != "root":
            logger_to_configure.propagate = False

        return logger_to_configure

    @staticmethod
    def remove_color_codes(text: str) -> str:
        """
        Remove ANSI color codes from the given text.

        Args:
            text (str): The text to remove the color codes from

        Returns:
            str: The text without the color codes
        """
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)

# --- Uncaught Exception Handling ---
def _handle_uncaught_exception(exc_type, exc_value, exc_traceback):
    """
    Logs uncaught exceptions using the root logger.
    This function is assigned to sys.excepthook to handle errors globally.
    """
    logger = Logger.get_logger()
    tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    traceback_str = "".join(tb_lines)
    message = f"Uncaught exception:\n{traceback_str}"
    logger.critical(message)

# Set the global exception hook to our custom handler
# This ensures that any unhandled exception triggers the logging function
sys.excepthook = _handle_uncaught_exception
# --- End Uncaught Exception Handling ---


if __name__ == "__main__":
    # Example usage
    logger = Logger.get_logger("test1")
    logger.info("This is an info message.")
    logger = Logger.get_logger("test2")
    logger.info("This is an info message.")
    logger = Logger.get_logger()
    logger.info("This is an info message.")
    a = 1/0
