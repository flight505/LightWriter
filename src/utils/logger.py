"""Logging configuration for Lightwriter_CLI."""
import logging
import sys

from termcolor import colored

from .constants import DEFAULT_STORE_PATH

# Create logs directory
LOGS_DIR = DEFAULT_STORE_PATH / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

class ColoredFormatter(logging.Formatter):
    """Custom formatter for colored console output."""

    COLORS = {
        'DEBUG': 'grey',
        'INFO': 'white',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red'
    }

    def format(self, record):
        """Format log record with colors."""
        # Color the level name
        if record.levelname in self.COLORS:
            record.levelname = colored(record.levelname, self.COLORS[record.levelname])

        # Color success/error indicators in messages
        if '✓' in record.msg:
            record.msg = colored(record.msg, 'green')
        elif '⚠️' in record.msg:
            record.msg = colored(record.msg, 'yellow')
        elif '❌' in record.msg:
            record.msg = colored(record.msg, 'red')

        return super().format(record)

def setup_logging(name: str = "lightwriter") -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter('%(levelname)s: %(message)s'))
    logger.addHandler(console_handler)

    # File handler for debug logging
    file_handler = logging.FileHandler(LOGS_DIR / "lightwriter.log", encoding='utf-8')
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger

# Create default logger instance
logger = setup_logging()
