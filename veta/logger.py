"""
Comprehensive logging system for veta package.

This module provides:
1. A centralized logger that can be used throughout the veta package
2. Colored, timestamped logs with different levels (DEBUG, INFO, WARNING, ERROR)
3. Detailed formatting including function name and line number
4. File output with automatic log file generation
5. Easy initialization from any part of the codebase
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union
import inspect

# ANSI color codes for terminal output
class LogColors:
    """ANSI color codes for colored terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Regular colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds colors to log levels and maintains detailed formatting."""
    
    # Color mapping for different log levels (for the actual message text)
    MESSAGE_COLORS = {
        'DEBUG': LogColors.BRIGHT_BLUE,
        'INFO': LogColors.WHITE,  # Keep info messages as standard white
        'WARNING': LogColors.BRIGHT_YELLOW,
        'ERROR': LogColors.BRIGHT_RED,
        'CRITICAL': LogColors.BRIGHT_MAGENTA,
    }
    
    # Color mapping for log level labels
    LEVEL_COLORS = {
        'DEBUG': LogColors.BLUE,
        'INFO': LogColors.GREEN,
        'WARNING': LogColors.YELLOW,
        'ERROR': LogColors.RED,
        'CRITICAL': LogColors.MAGENTA,
    }
    
    # Fixed colors for different parts
    TIMESTAMP_COLOR = LogColors.BRIGHT_GREEN
    LOCATION_COLOR = LogColors.CYAN
    
    def __init__(self, use_colors=True):
        self.use_colors = use_colors and sys.stderr.isatty()  # Only use colors in terminal
        
        # Detailed format with timestamp, level, location, and message
        detailed_format = (
            "%(asctime)s | %(levelname)-8s | "
            "%(name)s:%(funcName)s:%(lineno)d | "
            "%(message)s"
        )
        
        super().__init__(
            fmt=detailed_format,
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def format(self, record):
        # Get the basic formatted message
        formatted = super().format(record)
        
        # Add colors if enabled and this is a terminal
        if self.use_colors:
            level_name = record.levelname
            
            # Split the formatted message into parts
            parts = formatted.split(' | ')
            if len(parts) >= 4:
                timestamp = parts[0]
                level = parts[1]
                location = parts[2]
                message = ' | '.join(parts[3:])  # In case message contains ' | '
                
                # Apply colors to each part
                colored_timestamp = f"{self.TIMESTAMP_COLOR}{timestamp}{LogColors.RESET}"
                colored_level = f"{self.LEVEL_COLORS.get(level_name, '')}{level}{LogColors.RESET}"
                colored_location = f"{self.LOCATION_COLOR}{location}{LogColors.RESET}"
                colored_message = f"{self.MESSAGE_COLORS.get(level_name, '')}{message}{LogColors.RESET}"
                
                # Reconstruct the formatted message with colors
                formatted = f"{colored_timestamp} | {colored_level} | {colored_location} | {colored_message}"
        
        return formatted


class VetaLogger:
    """
    Main logger class for the veta package.
    
    This class provides a centralized logging system that can be used throughout
    the veta package with consistent formatting and output options.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Singleton pattern to ensure only one logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger (only once due to singleton pattern)."""
        if not self._initialized:
            self.logger = logging.getLogger('veta')
            self.logger.setLevel(logging.DEBUG)
            self._handlers_added = False
            VetaLogger._initialized = True
    
    def setup(self, 
              level: Union[str, int] = logging.INFO,
              log_file: Optional[str] = None,
              console_output: bool = True,
              file_level: Union[str, int] = logging.DEBUG,
              console_level: Union[str, int] = logging.INFO,
              auto_generate_file: bool = True) -> None:
        """
        Set up the logger with specified configuration.
        
        Parameters:
        -----------
        level : str or int
            Overall logging level (default: INFO)
        log_file : str, optional
            Path to log file. If None and auto_generate_file is True, 
            will auto-generate a filename.
        console_output : bool
            Whether to output logs to console (default: True)
        file_level : str or int
            Logging level for file output (default: DEBUG)
        console_level : str or int  
            Logging level for console output (default: INFO)
        auto_generate_file : bool
            Whether to auto-generate log file if none specified (default: True)
        """
        
        # Clear any existing handlers to avoid duplicates
        if self._handlers_added:
            self.logger.handlers.clear()
        
        # Convert string levels to integers if needed
        if isinstance(level, str):
            level = getattr(logging, level.upper())
        if isinstance(file_level, str):
            file_level = getattr(logging, file_level.upper())
        if isinstance(console_level, str):
            console_level = getattr(logging, console_level.upper())
            
        self.logger.setLevel(level)
        
        # Set up console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(console_level)
            console_handler.setFormatter(ColoredFormatter(use_colors=True))
            self.logger.addHandler(console_handler)
        
        # Set up file handler
        if log_file or auto_generate_file:
            if not log_file and auto_generate_file:
                log_file = self._generate_log_filename()
            
            if log_file:
                # Ensure log directory exists
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(log_file, mode='a')
                file_handler.setLevel(file_level)
                # Use plain formatter for file (no colors)
                file_formatter = logging.Formatter(
                    fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
                
                self.logger.info(f"Logging to file: {log_file}")
        
        self._handlers_added = True
        self.logger.info("Veta logging system initialized")
    
    def _generate_log_filename(self) -> str:
        """Generate an automatic log filename based on current timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Try to create logs in a few different locations
        possible_dirs = [
            Path.cwd() / "logs",
            Path.cwd(),  
            Path.home() / "veta_logs",
            Path("/tmp") / "veta_logs"
        ]
        
        for log_dir in possible_dirs:
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                return str(log_dir / f"veta_{timestamp}.log")
            except (PermissionError, OSError):
                continue
        
        # Fallback to current directory
        return f"veta_{timestamp}.log"
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance.
        
        Parameters:
        -----------
        name : str, optional
            Name for the logger. If None, returns the main veta logger.
            
        Returns:
        --------
        logging.Logger
            Configured logger instance
        """
        if name:
            return logging.getLogger(f'veta.{name}')
        return self.logger


# Global logger instance
_veta_logger = VetaLogger()


def setup_logging(level: Union[str, int] = logging.INFO,
                 log_file: Optional[str] = None,
                 console_output: bool = True,
                 file_level: Union[str, int] = logging.DEBUG,
                 console_level: Union[str, int] = logging.INFO,
                 auto_generate_file: bool = True) -> None:
    """
    Set up logging for the veta package.
    
    This is the main function to initialize logging. Call this once at the start
    of your application.
    
    Parameters:
    -----------
    level : str or int
        Overall logging level (default: INFO)
    log_file : str, optional
        Path to log file. If None and auto_generate_file is True, 
        will auto-generate a filename.
    console_output : bool
        Whether to output logs to console (default: True)
    file_level : str or int
        Logging level for file output (default: DEBUG)
    console_level : str or int  
        Logging level for console output (default: INFO)
    auto_generate_file : bool
        Whether to auto-generate log file if none specified (default: True)
    
    Examples:
    ---------
    >>> from veta import setup_logging
    >>> setup_logging(level='DEBUG', log_file='my_analysis.log')
    
    >>> # Auto-generate log file with default settings
    >>> setup_logging()
    
    >>> # Console-only logging
    >>> setup_logging(auto_generate_file=False)
    """
    _veta_logger.setup(
        level=level,
        log_file=log_file,
        console_output=console_output,
        file_level=file_level,
        console_level=console_level,
        auto_generate_file=auto_generate_file
    )


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for use in veta modules.
    
    This function automatically sets up basic logging if it hasn't been 
    configured yet. For full control, call setup_logging() first.
    
    Parameters:
    -----------
    name : str, optional
        Name for the logger. If None, returns the main veta logger.
        If provided, will create a child logger named 'veta.{name}'.
        
    Returns:
    --------
    logging.Logger
        Configured logger instance with proper formatting and handlers.
        
    Examples:
    ---------
    >>> from veta import get_logger
    >>> logger = get_logger('survey')
    >>> logger.info("Processing survey data")
    >>> logger.debug("Detailed debug information")
    >>> logger.warning("This is a warning")
    >>> logger.error("An error occurred")
    
    >>> # Get the main logger
    >>> main_logger = get_logger()
    >>> main_logger.info("Main application message")
    """
    # Auto-initialize with basic settings if not already done
    if not _veta_logger._handlers_added:
        _veta_logger.setup()
    
    return _veta_logger.get_logger(name)


# Convenience function to get caller info for manual logging
def get_caller_info(frame_offset: int = 1) -> tuple:
    """
    Get information about the calling function.
    
    Parameters:
    -----------
    frame_offset : int
        How many frames up the stack to look (default: 1)
        
    Returns:
    --------
    tuple
        (function_name, filename, line_number)
    """
    frame = inspect.currentframe()
    try:
        for _ in range(frame_offset + 1):
            frame = frame.f_back
            if frame is None:
                return ("unknown", "unknown", 0)
        
        return (
            frame.f_code.co_name,
            os.path.basename(frame.f_code.co_filename),
            frame.f_lineno
        )
    finally:
        del frame
