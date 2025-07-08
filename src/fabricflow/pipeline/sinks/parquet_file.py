from .base import BaseSink
from .types import SinkType
import logging
from logging import Logger
from typing import Optional
from sempy.fabric import resolve_workspace_id
from ...core.items.utils import resolve_item
from ...core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


class ParquetFileSink(BaseSink):
    """
    Represents a sink for writing data to a Parquet file in a Microsoft Fabric Lakehouse.

    This sink handles writing data to Parquet files stored in a Lakehouse Files area.
    It automatically resolves workspace and lakehouse names to their corresponding IDs
    and supports organizing files into directory structures.

    The sink can be configured with specific file details at initialization or these
    can be provided later through the items parameter in pipeline activities.

    Attributes:
        sink_workspace_id (str): Resolved workspace ID containing the Lakehouse.
        sink_lakehouse_id (str): Resolved Lakehouse ID where the file will be stored.
        sink_file_name (Optional[str]): Name of the target Parquet file (e.g., "data.parquet").
        sink_directory (Optional[str]): Directory path where the file will be stored.

    Args:
        sink_lakehouse (str): Name or ID of the target Lakehouse.
        sink_workspace (str): Name or ID of the workspace containing the Lakehouse.
        sink_directory (Optional[str]): Directory path. Can be provided later via items.
        sink_file_name (Optional[str]): Parquet file name. Can be provided later via items.

    Raises:
        ValueError: If workspace or lakehouse cannot be resolved.

    Note:
        If file details (name, directory) are not provided during initialization,
        they must be included in the items list when executing pipeline activities.
        Use the `required_params` property to see which parameters are mandatory.

    Example:
        ```python
        # Initialize with all details
        sink = ParquetFileSink(
            sink_lakehouse="MyLakehouse",
            sink_workspace="MyWorkspace",
            sink_file_name="sales_data.parquet",
            sink_directory="/exports/sales/"
        )

        # Initialize for use with items list
        sink = ParquetFileSink(
            sink_lakehouse="MyLakehouse",
            sink_workspace="MyWorkspace"
        )
        # File details provided later in copy.items([...])
        ```
    """

    def __init__(
        self,
        sink_lakehouse: str,
        sink_workspace: str,
        sink_directory: Optional[str] = None,
        sink_file_name: Optional[str] = None,
    ) -> None:
        super().__init__()

        # Resolve workspace and lakehouse to IDs if needed
        self.sink_workspace_id = resolve_workspace_id(sink_workspace)

        if not self.sink_workspace_id:
            raise ValueError("sink_workspace (name or id) could not be resolved.")

        self.sink_lakehouse_id = resolve_item(
            sink_lakehouse, FabricItemType.LAKEHOUSE, self.sink_workspace_id
        )

        if not self.sink_lakehouse_id:
            raise ValueError("sink_lakehouse (name or id) could not be resolved.")

        self.sink_file_name = sink_file_name
        self.sink_directory = sink_directory

        logger.info(
            f"ParquetFileSink initialized: sink_file_name='{sink_file_name}', sink_directory='{sink_directory}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns the list of required parameter names for this sink type.

        For ParquetFileSink, the required parameters are file name and directory.
        These must be provided either during initialization or in the items list
        when executing pipeline activities.

        Returns:
            list[str]: List of required parameter names:
                      ["sink_file_name", "sink_directory"]
        """
        return ["sink_file_name", "sink_directory"]

    def to_dict(self) -> dict[str, str]:
        """
        Converts the ParquetFileSink configuration to a dictionary.

        This method creates a dictionary representation suitable for use in
        pipeline execution payloads. It includes the resolved workspace and
        lakehouse IDs, sink type, and any configured file details.

        Returns:
            dict[str, str]: Dictionary containing:
                - sink_type: Always "ParquetFile"
                - sink_lakehouse_id: Resolved Lakehouse ID
                - sink_workspace_id: Resolved workspace ID
                - sink_file_name: Parquet file name (if configured)
                - sink_directory: Directory path (if configured)

        Note:
            Optional parameters (file_name, directory) are only included if they
            were provided during initialization.
        """
        result: dict[str, str] = {
            "sink_type": SinkType.PARQUET_FILE.value,
            "sink_lakehouse_id": self.sink_lakehouse_id,
            "sink_workspace_id": self.sink_workspace_id,
        }
        if self.sink_file_name:
            result["sink_file_name"] = self.sink_file_name
        if self.sink_directory:
            result["sink_directory"] = self.sink_directory
        return result
