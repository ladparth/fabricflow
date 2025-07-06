from .base import BaseSource
from .types import SourceType, IsolationLevel
from logging import Logger
import logging
from typing import Any, Optional

logger: Logger = logging.getLogger(__name__)


class SQLServerSource(BaseSource):
    """
    Represents a source for data from a SQL Server database.
    Inherits common properties from BaseSource.

    Attributes:
        source_connection_id (str): Unique identifier for the SQL Server connection.
        source_database_name (str): Name of the SQL Server database.
        source_query (str): SQL query to execute against the database. If you choose to pass the query from a list, you can leave this blank,
                            but ensure that the 'source_query' key is still present in the list of dictionaries used for pipeline parameters.
                            You may access required parameters using the `required_params` property.
        first_row_only (bool): If True, only the first row of the result set will be returned. Only to be used with Lookup Activity.
        isolation_level (str): The isolation level for the SQL query execution. Optional.
                              If not specified, the default isolation level of the SQL Server connection will be used.
                              It specifies the transaction locking behavior for the SQL source. The allowed values are:
                              ReadCommitted, ReadUncommitted, RepeatableRead, Serializable, Snapshot
        query_timeout (str): The timeout for the SQL query execution as a timespan string, e.g., "02:00:00" (default is "02:00:00" for 120 minutes).
    """

    def __init__(
        self,
        source_connection_id: str,
        source_database_name: str,
        source_query: Optional[str] = None,
        first_row_only: Optional[bool] = None,
        isolation_level: Optional[IsolationLevel] = None,
        query_timeout: Optional[str] = "02:00:00",
    ) -> None:
        super().__init__()

        if not source_connection_id:
            raise ValueError("source_connection_id cannot be empty.")
        if not source_database_name:
            raise ValueError("source_database_name cannot be empty.")
        if first_row_only is not None and not isinstance(first_row_only, bool):
            raise ValueError("first_row_only must be a boolean value.")
        if isolation_level and not isinstance(isolation_level, IsolationLevel):
            raise ValueError(
                "isolation_level must be an instance of IsolationLevel enum."
            )
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
        self.source_database_name = source_database_name
        self.source_query = source_query
        self.first_row_only = first_row_only
        self.isolation_level = isolation_level
        self.query_timeout = query_timeout

        logger.info(
            f"SQLServerSource initialized: source_connection_id='{source_connection_id}', source_database_name='{source_database_name}', source_query='{(source_query[:50] + '...') if source_query else None}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of required parameters for the SQL Server source.
        This can be overridden by subclasses to provide specific parameters.
        """
        return ["source_query"]

    def to_dict(self) -> dict[str, str]:
        """
        Converts the SQLServerSource object to a dictionary.
        Only includes 'source_query' if source_query is not empty.
        """
        result: dict[str, Any] = {
            "source_type": SourceType.SQL_SERVER.value,
            "source_connection_id": self.source_connection_id,
            "source_database_name": self.source_database_name,
        }
        if self.source_query:
            result["source_query"] = self.source_query
        if self.first_row_only is not None:
            result["first_row_only"] = self.first_row_only
        if self.isolation_level is not None:
            result["isolation_level"] = self.isolation_level.value
        if self.query_timeout is not None:
            result["query_timeout"] = self.query_timeout
        return result
