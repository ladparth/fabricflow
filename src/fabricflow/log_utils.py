from logging import Logger, StreamHandler, Formatter
from typing import TextIO
import logging


def setup_logging(level=logging.INFO, format_string=None) -> None:
    """
    Convenience function to set up logging for FabricFlow.

    Args:
        level: Logging level (logging.DEBUG, logging.INFO, etc.)
        format_string: Custom log format string
            (default: "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    Example:
        import fabricflow
        fabricflow.setup_logging(level=logging.DEBUG)
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
