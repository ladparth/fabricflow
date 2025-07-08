"""
Logging utilities for FabricFlow.

This module provides convenient functions for setting up consistent
logging configuration across the FabricFlow package.

Functions:
    setup_logging: Configure logging for FabricFlow with custom levels and formats.
"""

from logging import Logger, StreamHandler, Formatter
from typing import TextIO
import logging


def setup_logging(level=logging.INFO, format_string=None) -> None:
    """
    Convenience function to set up logging for FabricFlow.

    Configures a dedicated logger for the FabricFlow package with console output.
    Removes any existing handlers to avoid duplicate log messages and sets up
    a new StreamHandler with the specified format and level.

    Args:
        level (int, optional): Logging level from the logging module. 
            Defaults to logging.INFO. Common values:
            - logging.DEBUG: Detailed information for diagnosing problems
            - logging.INFO: General information about program execution  
            - logging.WARNING: Something unexpected happened
            - logging.ERROR: A serious problem occurred
            - logging.CRITICAL: Very serious error occurred
        format_string (str, optional): Custom log format string. If None,
            uses default format with timestamp, logger name, level, and message.
            Defaults to "%(asctime)s - %(name)s - %(levelname)s - %(message)s".

    Returns:
        None

    Example:
        >>> import fabricflow
        >>> import logging
        >>> 
        >>> # Set up basic logging
        >>> fabricflow.setup_logging()
        >>> 
        >>> # Set up debug logging with custom format
        >>> fabricflow.setup_logging(
        ...     level=logging.DEBUG,
        ...     format_string="%(levelname)s: %(message)s"
        ... )

    Note:
        This function modifies the global logging configuration for the
        'fabricflow' logger namespace. All FabricFlow modules use loggers
        that inherit from this namespace.
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create a logger for FabricFlow
    fabricflow_logger: Logger = logging.getLogger("fabricflow")

    # Remove existing handlers to avoid duplicates
    for handler in fabricflow_logger.handlers[:]:
        fabricflow_logger.removeHandler(handler)

    # Create console handler
    console_handler: StreamHandler[TextIO] = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter: Formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    fabricflow_logger.addHandler(console_handler)
    fabricflow_logger.setLevel(level)

    # Prevent logs from being handled by parent loggers
    fabricflow_logger.propagate = False
