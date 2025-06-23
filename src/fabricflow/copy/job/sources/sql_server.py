from ..base import BaseSource
from ..types import SourceType
from logging import Logger
import logging
from typing import Optional

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

    """

    def __init__(
        self,
        source_connection_id: str,
        source_database_name: str,
        source_query: Optional[str] = None,
    ) -> None:
        super().__init__()

        if not source_connection_id:
            raise ValueError("source_connection_id cannot be empty.")
        if not source_database_name:
            raise ValueError("source_database_name cannot be empty.")

        self.source_connection_id = source_connection_id
        self.source_database_name = source_database_name
        self.source_query = source_query

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
        result: dict[str, str] = {
            "source_type": SourceType.SQL_SERVER.value,
            "source_connection_id": self.source_connection_id,
            "source_database_name": self.source_database_name,
        }
        if self.source_query:
            result["source_query"] = self.source_query
        return result
