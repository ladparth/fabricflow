"""
PostgreSQL data source implementation for Fabric data pipelines.

Provides PostgreSQLSource, a BaseSource implementation for reading data from PostgreSQL
databases in Microsoft Fabric pipelines. Supports connection management, query timeouts,
Copy and Lookup activities, and flexible query execution.

Example:
    from fabricflow.pipeline.sources import PostgreSQLSource

    source = PostgreSQLSource(
        source_connection_id="postgresql-conn-123",
        source_query="SELECT * FROM customers",
        query_timeout="01:30:00"
    )
"""

from .base import BaseSource
from .types import SourceType
from logging import Logger
import logging
from typing import Any, Optional

logger: Logger = logging.getLogger(__name__)


class PostgreSQLSource(BaseSource):
    """
    Data source for reading from PostgreSQL in Fabric pipelines.

    Supports query timeouts, Copy and Lookup activities, and batch operations.

    Args:
        source_connection_id (str): PostgreSQL connection ID.
        source_query (Optional[str]): SQL query to execute.
        first_row_only (Optional[bool]): If True, return only the first row.
        query_timeout (Optional[str]): Timeout in 'HH:MM:SS' format.

    Raises:
        ValueError: On invalid parameters.
    """

    def __init__(
        self,
        source_connection_id: str,
        source_query: Optional[str] = None,
        first_row_only: Optional[bool] = None,
        query_timeout: Optional[str] = "02:00:00",
    ) -> None:
        super().__init__()

        if not source_connection_id:
            raise ValueError("source_connection_id cannot be empty.")
        if first_row_only is not None and not isinstance(first_row_only, bool):
            raise ValueError("first_row_only must be a boolean value.")

        if query_timeout is not None:
            if not isinstance(query_timeout, str):
                raise ValueError(
                    "query_timeout must be a timespan string in 'HH:MM:SS' format, e.g., '02:00:00'."
                )
            parts = query_timeout.split(":")
            if len(parts) != 3 or not all(p.isdigit() for p in parts):
                raise ValueError(
                    "query_timeout must be a timespan string in 'HH:MM:SS' format, e.g., '02:00:00'."
                )

        self.source_connection_id = source_connection_id
        self.source_query = source_query
        self.first_row_only = first_row_only
        self.query_timeout = query_timeout

        logger.info(
            f"PostgreSQLSource initialized: source_connection_id='{source_connection_id}', source_query='{(source_query[:50] + '...') if source_query else None}'"
        )

    @property
    def required_params(self) -> list[str]:
        """List of required parameters for the source."""
        return ["source_query"]

    def to_dict(self) -> dict[str, str]:
        """Convert the source to a dictionary for pipeline execution."""
        result: dict[str, Any] = {
            "source_type": SourceType.POSTGRESQL.value,
            "source_connection_id": self.source_connection_id,
        }
        if self.source_query:
            result["source_query"] = self.source_query
        if self.first_row_only is not None:
            result["first_row_only"] = self.first_row_only
        if self.query_timeout is not None:
            result["query_timeout"] = self.query_timeout
        return result
