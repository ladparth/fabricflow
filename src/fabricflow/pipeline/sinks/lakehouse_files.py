"""
LakehouseFilesSink: Sink for writing files to Microsoft Fabric Lakehouse Files area.

Provides support for:
- Workspace and lakehouse resolution
- Directory management
- Configurable copy behaviors
- Staging and parallel copy options

Example:
    sink = LakehouseFilesSink(
        sink_lakehouse="data-lakehouse",
        sink_workspace="analytics-workspace",
        sink_directory="incoming/files"
    )
"""

from .base import BaseSink
from .types import SinkType, FileCopyBehavior
import logging
from logging import Logger
from typing import Optional, Any
from sempy.fabric import resolve_workspace_id
from ...core.items.utils import resolve_item
from ...core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


class LakehouseFilesSink(BaseSink):
    """
    Sink for writing files to the Files area of a Microsoft Fabric Lakehouse.

    Resolves workspace and lakehouse IDs, manages directory structure, and supports
    copy behavior, staging, and parallel copy options.

    Args:
        sink_lakehouse (str): Lakehouse name or ID.
        sink_workspace (str): Workspace name or ID.
        sink_directory (Optional[str]): Target directory path.
        copy_behavior (Optional[FileCopyBehavior]): Copy behavior (FileCopyBehavior.PRESERVE_HIERARCHY, FileCopyBehavior.FLATTEN_HIERARCHY).
        enable_staging (Optional[bool]): Use staging for transfers.
        parallel_copies (Optional[int]): Number of parallel operations.
        max_concurrent_connections (Optional[int]): Max connections.

    Raises:
        ValueError: On invalid or unresolved parameters.
    """

    def __init__(
        self,
        sink_lakehouse: str,
        sink_workspace: str,
        sink_directory: Optional[str] = None,
        copy_behavior: Optional[FileCopyBehavior] = FileCopyBehavior.PRESERVE_HIERARCHY,
        enable_staging: Optional[bool] = False,
        parallel_copies: Optional[int] = 4,
        max_concurrent_connections: Optional[int] = 10,
    ) -> None:
        super().__init__()

        self.sink_workspace_id = resolve_workspace_id(sink_workspace)
        if not self.sink_workspace_id:
            raise ValueError("sink_workspace (name or id) could not be resolved.")

        self.sink_lakehouse_id = resolve_item(
            sink_lakehouse, FabricItemType.LAKEHOUSE, self.sink_workspace_id
        )
        if not self.sink_lakehouse_id:
            raise ValueError("sink_lakehouse (name or id) could not be resolved.")

        if enable_staging is not None and not isinstance(enable_staging, bool):
            raise ValueError("enable_staging must be a boolean value.")
        if copy_behavior is not None and not isinstance(
            copy_behavior, FileCopyBehavior
        ):
            raise ValueError(
                "copy_behavior must be an instance of FileCopyBehavior enum."
            )
        if parallel_copies is not None:
            if not isinstance(parallel_copies, int) or parallel_copies <= 0:
                raise ValueError("parallel_copies must be a positive integer.")
        if max_concurrent_connections is not None:
            if (
                not isinstance(max_concurrent_connections, int)
                or max_concurrent_connections <= 0
            ):
                raise ValueError(
                    "max_concurrent_connections must be a positive integer."
                )

        self.sink_directory = sink_directory
        self.copy_behavior = copy_behavior
        self.enable_staging = enable_staging
        self.parallel_copies = parallel_copies
        self.max_concurrent_connections = max_concurrent_connections

        logger.info(
            f"LakehouseFilesSink initialized: sink_directory='{sink_directory}', "
            f"copy_behavior='{copy_behavior}', enable_staging='{enable_staging}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns required parameter names for Lakehouse Files sinks.
        """
        return []

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the sink configuration to a dictionary.
        Only includes parameters that are not None.
        """
        result: dict[str, Any] = {
            "sink_type": SinkType.LAKEHOUSE_FILES.value,
            "sink_lakehouse_id": self.sink_lakehouse_id,
            "sink_workspace_id": self.sink_workspace_id,
        }

        if self.sink_directory:
            result["sink_directory"] = self.sink_directory
        if self.copy_behavior:
            result["copy_behavior"] = self.copy_behavior.value
        if self.enable_staging is not None:
            result["enable_staging"] = self.enable_staging
        if self.parallel_copies is not None:
            result["parallel_copies"] = self.parallel_copies
        if self.max_concurrent_connections is not None:
            result["max_concurrent_connections"] = self.max_concurrent_connections

        return result
