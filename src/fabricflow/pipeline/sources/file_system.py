"""
FileSystemSource: File system data source for Fabric data pipelines.

Provides pattern-based file selection, date filtering, recursive traversal, and copy behavior
configuration for Microsoft Fabric Copy activities.

Example:
    source = FileSystemSource(
        source_connection_id="fileserver-conn-123",
        source_folder_pattern="data/incoming/*",
        source_file_pattern="*.csv",
        recursive_search=True
    )
"""

from .base import BaseSource
from .types import SourceType
from logging import Logger
import logging
from typing import Any, Optional

logger: Logger = logging.getLogger(__name__)


class FileSystemSource(BaseSource):
    """
    File server source for Fabric data pipelines.

    Supports:
    - Wildcard folder/file patterns
    - Date filtering (modified before/after)
    - Recursive directory traversal
    - Source file deletion after copy
    - Configurable connection limits

    Args:
        source_connection_id (str): File server connection ID.
        source_folder_pattern (Optional[str]): Wildcard folder pattern. Default: "*".
        source_file_pattern (Optional[str]): Wildcard file pattern. Default: "*".
        source_modified_after (Optional[str]): ISO datetime for filtering files modified after.
        source_modified_before (Optional[str]): ISO datetime for filtering files modified before.
        recursive_search (Optional[bool]): Enable recursive search. Default: True.
        delete_source_after_copy (Optional[bool]): Delete files after copy. Default: False.
        max_concurrent_connections (Optional[int]): Max concurrent connections. Default: 10.

    Raises:
        ValueError: On invalid arguments.
    """

    def __init__(
        self,
        source_connection_id: str,
        source_folder_pattern: Optional[str] = "*",
        source_file_pattern: Optional[str] = "*",
        source_modified_after: Optional[str] = None,
        source_modified_before: Optional[str] = None,
        recursive_search: Optional[bool] = True,
        delete_source_after_copy: Optional[bool] = False,
        max_concurrent_connections: Optional[int] = 10,
    ) -> None:
        super().__init__()

        if not source_connection_id:
            raise ValueError("source_connection_id cannot be empty.")
        if recursive_search is not None and not isinstance(recursive_search, bool):
            raise ValueError("recursive_search must be a boolean value.")
        if delete_source_after_copy is not None and not isinstance(
            delete_source_after_copy, bool
        ):
            raise ValueError("delete_source_after_copy must be a boolean value.")
        if max_concurrent_connections is not None:
            if (
                not isinstance(max_concurrent_connections, int)
                or max_concurrent_connections <= 0
            ):
                raise ValueError(
                    "max_concurrent_connections must be a positive integer."
                )

        self.source_connection_id = source_connection_id
        self.source_folder_pattern = source_folder_pattern
        self.source_file_pattern = source_file_pattern
        self.source_modified_after = source_modified_after
        self.source_modified_before = source_modified_before
        self.recursive_search = recursive_search
        self.delete_source_after_copy = delete_source_after_copy
        self.max_concurrent_connections = max_concurrent_connections

        logger.info(
            f"FileSystemSource initialized: source_connection_id='{source_connection_id}', "
            f"source_folder_pattern='{source_folder_pattern}', source_file_pattern='{source_file_pattern}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns required parameter names for file server sources.
        """
        return []

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the FileSystemSource object to a dictionary.
        Only includes parameters that are not None or empty.
        """
        result: dict[str, Any] = {
            "source_type": SourceType.FILE_SERVER.value,
            "source_connection_id": self.source_connection_id,
        }

        if self.source_folder_pattern:
            result["source_folder_pattern"] = self.source_folder_pattern
        if self.source_file_pattern:
            result["source_file_pattern"] = self.source_file_pattern
        if self.source_modified_after:
            result["source_modified_after"] = self.source_modified_after
        if self.source_modified_before:
            result["source_modified_before"] = self.source_modified_before
        if self.recursive_search is not None:
            result["recursive_search"] = self.recursive_search
        if self.delete_source_after_copy is not None:
            result["delete_source_after_copy"] = self.delete_source_after_copy
        if self.max_concurrent_connections is not None:
            result["max_concurrent_connections"] = self.max_concurrent_connections

        return result
