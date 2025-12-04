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
    _logger: Optional[logging.Logger] = None

    @staticmethod
    def init_logger(name: str = "logger",
                   level: int = logging.DEBUG,
                   file_path: Optional[Union[str, Path]] = None,
                   file_max_bytes: int = 100 * 1024, # 100 KB
                   file_backup_count: int = 1,
                   show_name: bool = False
                   ) -> logging.Logger:
        """
        Initializes the global logger with the specified configuration.
        Should be called once at application startup. Subsequent calls return the existing logger.

        Args:
            name (str, optional): The name for the logger instance. Defaults to 'logger'.
            level (int, optional): The minimum logging level. Defaults to logging.DEBUG.
            file_path (str | Path | None, optional): If provided, logs will also be
                                                    written to this file. If a directory path
                                                    is provided, the log file will be created
                                                    as '{name}.log' inside that directory.
                                                    Defaults to None.
            file_max_bytes (int, optional): Max size in bytes for the log file
                                            before rotation. Defaults to 100KB.
            file_backup_count (int, optional): Number of backup log files to keep.
                                               Defaults to 1.
            show_name (bool, optional): Whether to show the logger name in the format.
                                        Defaults to False.

        Returns:
            logging.Logger: The configured logger instance.
        """

        # Return existing logger if already initialized
        if Logger._logger is not None:
            return Logger._logger

        # Create and configure the logger
        logger_to_configure = logging.getLogger(name)

        # Configure the new logger
        logger_to_configure.setLevel(level)

        # Formatters
        separator = '>' if sys.platform == 'win32' else '»' # Some Windows versions don't support '»'
        name_part = '[%(name)s]' if show_name else ''
        log_format = f'[%(asctime)s]{name_part}[%(levelname).1s] {separator} %(message)s'
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
            file_path_obj = Path(file_path)
            # If file_path is a directory, create the log file path using the logger name
            if file_path_obj.is_dir() or not file_path_obj.suffix:
                file_path_obj = file_path_obj / f"{name}.log"
            # Ensure parent directory exists
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=str(file_path_obj), maxBytes=file_max_bytes,
                backupCount=file_backup_count, encoding='utf-8'
            )
            file_handler.setFormatter(file_formatter)
            file_handler.setLevel(level)
            logger_to_configure.addHandler(file_handler)

        # Prevent propagation for non-root loggers
        if logger_to_configure.name != "root":
            logger_to_configure.propagate = False

        # Setup global exception handler
        sys.excepthook = Logger._handle_uncaught_exception

        # Store and return the logger
        Logger._logger = logger_to_configure
        return logger_to_configure

    @staticmethod
    def get_logger() -> logging.Logger:
        """
        Returns the initialized logger.
        If not initialized, calls init_logger() with default parameters.

        Returns:
            logging.Logger: The global logger instance.
        """
        if Logger._logger is None:
            Logger.init_logger()
        return Logger._logger

    @staticmethod
    def _handle_uncaught_exception(exc_type, exc_value, exc_traceback):
        """
        Logs uncaught exceptions using the main logger.
        This function is assigned to sys.excepthook to handle errors globally.
        """
        logger = Logger.get_logger()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        traceback_str = "".join(tb_lines)
        message = f"Uncaught exception:\n{traceback_str}"
        logger.critical(message)

    @staticmethod
    def remove_color_codes(text: str) -> str:
        """
        Utility method to remove ANSI color codes from the given text.

        Args:
            text (str): The text to remove the color codes from

        Returns:
            str: The text without the color codes
        """
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)


if __name__ == "__main__":
    # Example usage
    # Initialize the logger once at application startup
    Logger.init_logger(name="myapp", level=logging.DEBUG)

    # Get the logger anywhere in the code
    logger = Logger.get_logger()
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")

    # Test uncaught exception handling
    a = 1/0
