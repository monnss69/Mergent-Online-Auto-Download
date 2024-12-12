import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt: Optional[str] = None):
        super().__init__()
        self.fmt = fmt or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logging(
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    log_format: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        log_file: Optional path to log file
        level: Logging level
        log_format: Optional custom log format
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("MergentScraper")
    logger.setLevel(level)
    
    # Default format if none provided
    if not log_format:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create console handler with custom formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(CustomFormatter(log_format))
    logger.addHandler(console_handler)
    
    # Create file handler if log file specified
    if log_file:
        log_path = Path(log_file)
        if not log_path.parent.exists():
            log_path.parent.mkdir(parents=True)
            
        # Add timestamp to filename if not provided
        if not log_path.suffix:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = log_path.with_suffix(f".{timestamp}.log")
            
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(file_handler)
    
    return logger

class LoggerManager:
    """Singleton logger manager to ensure consistent logging across modules"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_logger(cls) -> logging.Logger:
        """Get or create logger instance"""
        if cls._logger is None:
            cls._logger = setup_logging()
        return cls._logger
    
    @classmethod
    def setup(cls, **kwargs) -> logging.Logger:
        """Setup logger with custom configuration"""
        cls._logger = setup_logging(**kwargs)
        return cls._logger