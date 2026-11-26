#!/usr/bin/env python3
"""
Clean logging utility for Rebecca Richards Photography Album Scraper.

Provides structured logging with emoji indicators while maintaining the visual style
that users expect from the scraper output.
"""

import sys
from enum import Enum
from datetime import datetime
from typing import Optional, Any


class LogLevel(Enum):
    """Log levels with corresponding emoji indicators."""
    DEBUG = ("🔍", "DEBUG")
    INFO = ("ℹ️", "INFO")
    SUCCESS = ("✅", "SUCCESS")
    WARNING = ("⚠️", "WARNING")
    ERROR = ("❌", "ERROR")
    PROGRESS = ("🎯", "PROGRESS")
    STATS = ("📊", "STATS")
    FILES = ("📁", "FILES")
    NETWORK = ("🌐", "NETWORK")
    METADATA = ("💾", "METADATA")


class ScraperLogger:
    """
    Clean, structured logger for the scraper tools.
    
    Maintains the emoji-based visual style while providing better organization
    and consistency across all logging calls.
    """
    
    def __init__(self, show_timestamp: bool = False, min_level: LogLevel = LogLevel.INFO):
        """
        Initialize the logger.
        
        Args:
            show_timestamp: Whether to include timestamps in log messages
            min_level: Minimum log level to display
        """
        self.show_timestamp = show_timestamp
        self.min_level = min_level
        self._level_hierarchy = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.SUCCESS: 2,
            LogLevel.WARNING: 3,
            LogLevel.ERROR: 4,
            LogLevel.PROGRESS: 1,
            LogLevel.STATS: 2,
            LogLevel.FILES: 1,
            LogLevel.NETWORK: 1,
            LogLevel.METADATA: 2,
        }
    
    def _should_log(self, level: LogLevel) -> bool:
        """Check if a message should be logged based on the minimum level."""
        return self._level_hierarchy.get(level, 1) >= self._level_hierarchy.get(self.min_level, 1)
    
    def _format_message(self, level: LogLevel, message: str, context: Optional[str] = None) -> str:
        """Format a log message with emoji and optional timestamp."""
        emoji, level_name = level.value
        
        # Build the message parts
        parts = []
        
        if self.show_timestamp:
            timestamp = datetime.now().strftime("%H:%M:%S")
            parts.append(f"[{timestamp}]")
        
        parts.append(emoji)
        
        if context:
            parts.append(f"[{context}]")
        
        parts.append(message)
        
        return " ".join(parts)
    
    def _log(self, level: LogLevel, message: str, context: Optional[str] = None, 
             file=None, end: str = "\n") -> None:
        """Internal logging method."""
        if not self._should_log(level):
            return
        
        formatted_message = self._format_message(level, message, context)
        
        # Use stderr for errors and warnings, stdout for everything else
        output_file = file or (sys.stderr if level in [LogLevel.ERROR, LogLevel.WARNING] else sys.stdout)
        
        print(formatted_message, file=output_file, end=end)
        output_file.flush()
    
    # Core logging methods
    def debug(self, message: str, context: Optional[str] = None) -> None:
        """Log a debug message."""
        self._log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[str] = None) -> None:
        """Log an info message."""
        self._log(LogLevel.INFO, message, context)
    
    def success(self, message: str, context: Optional[str] = None) -> None:
        """Log a success message."""
        self._log(LogLevel.SUCCESS, message, context)
    
    def warning(self, message: str, context: Optional[str] = None) -> None:
        """Log a warning message."""
        self._log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Optional[str] = None, exception: Optional[Exception] = None) -> None:
        """Log an error message, optionally with exception details."""
        if exception:
            self._log(LogLevel.ERROR, f"{message}: {exception}", context)
        else:
            self._log(LogLevel.ERROR, message, context)
    
    # Specialized logging methods for common use cases
    def progress(self, message: str, context: Optional[str] = None) -> None:
        """Log a progress update."""
        self._log(LogLevel.PROGRESS, message, context)
    
    def stats(self, message: str, context: Optional[str] = None) -> None:
        """Log statistics information."""
        self._log(LogLevel.STATS, message, context)
    
    def files(self, message: str, context: Optional[str] = None) -> None:
        """Log file-related operations."""
        self._log(LogLevel.FILES, message, context)
    
    def network(self, message: str, context: Optional[str] = None) -> None:
        """Log network-related operations."""
        self._log(LogLevel.NETWORK, message, context)
    
    def metadata(self, message: str, context: Optional[str] = None) -> None:
        """Log metadata operations."""
        self._log(LogLevel.METADATA, message, context)
    
    # Convenience methods for common patterns
    def header(self, title: str, width: int = 55, char: str = "=") -> None:
        """Print a header with decorative border."""
        self._log(LogLevel.INFO, title)
        self._log(LogLevel.INFO, char * width)
    
    def section(self, title: str) -> None:
        """Print a section separator."""
        self._log(LogLevel.INFO, f"\n{title}")
    
    def step(self, step_number: int, description: str, total_steps: Optional[int] = None) -> None:
        """Log a numbered step in a process."""
        if total_steps:
            self.progress(f"Step {step_number}/{total_steps}: {description}")
        else:
            self.progress(f"Step {step_number}: {description}")
    
    def result(self, operation: str, success: bool, details: Optional[str] = None) -> None:
        """Log the result of an operation."""
        if success:
            message = f"{operation} completed successfully"
            if details:
                message += f": {details}"
            self.success(message)
        else:
            message = f"{operation} failed"
            if details:
                message += f": {details}"
            self.error(message)
    
    def count(self, item_type: str, count: int, context: Optional[str] = None) -> None:
        """Log a count of items."""
        self.stats(f"{item_type}: {count}", context)
    
    def url(self, message: str, url: str) -> None:
        """Log a message with a URL."""
        self.network(f"{message}: {url}")
    
    def file_op(self, operation: str, path: str, success: bool = True) -> None:
        """Log a file operation."""
        if success:
            self.files(f"{operation}: {path}")
        else:
            self.error(f"Failed to {operation.lower()}: {path}")
    
    # Output formatting helpers
    def blank_line(self) -> None:
        """Print a blank line."""
        print()
    
    def separator(self, char: str = "-", width: int = 50) -> None:
        """Print a separator line."""
        self._log(LogLevel.INFO, char * width)
    
    # Context manager support for progress indication
    def progress_context(self, message: str):
        """Context manager for progress indication with automatic completion."""
        return _ProgressContext(self, message)


class _ProgressContext:
    """Context manager for progress indication."""
    
    def __init__(self, logger: ScraperLogger, message: str):
        self.logger = logger
        self.message = message
        self.start_time = None
    
    def __enter__(self):
        self.logger.progress(f"Starting: {self.message}")
        self.start_time = datetime.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type is None:
            self.logger.success(f"Completed: {self.message} (took {duration.total_seconds():.1f}s)")
        else:
            self.logger.error(f"Failed: {self.message} after {duration.total_seconds():.1f}s")


# Create a default logger instance
logger = ScraperLogger()

# Convenience functions for direct import
def debug(message: str, context: Optional[str] = None) -> None:
    """Log a debug message."""
    logger.debug(message, context)

def info(message: str, context: Optional[str] = None) -> None:
    """Log an info message."""
    logger.info(message, context)

def success(message: str, context: Optional[str] = None) -> None:
    """Log a success message."""
    logger.success(message, context)

def warning(message: str, context: Optional[str] = None) -> None:
    """Log a warning message."""
    logger.warning(message, context)

def error(message: str, context: Optional[str] = None, exception: Optional[Exception] = None) -> None:
    """Log an error message."""
    logger.error(message, context, exception)

def progress(message: str, context: Optional[str] = None) -> None:
    """Log a progress update."""
    logger.progress(message, context)

def stats(message: str, context: Optional[str] = None) -> None:
    """Log statistics information."""
    logger.stats(message, context)

def files(message: str, context: Optional[str] = None) -> None:
    """Log file operations."""
    logger.files(message, context)

def network(message: str, context: Optional[str] = None) -> None:
    """Log network operations."""
    logger.network(message, context)

def metadata(message: str, context: Optional[str] = None) -> None:
    """Log metadata operations."""
    logger.metadata(message, context)