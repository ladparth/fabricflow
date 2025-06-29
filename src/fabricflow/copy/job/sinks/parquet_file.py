from ..base import BaseSink
from ..types import SinkType
import logging
from logging import Logger
from typing import Optional
from sempy.fabric import resolve_workspace_id
from ....core.items.utils import resolve_item
from ....core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


class ParquetFileSink(BaseSink):
    """
    Represents a sink for writing data to a Parquet file.
    Defines attributes specific to Parquet file sink.

    Attributes:
        sink_lakehouse (str): The name or ID of the Lakehouse where the table resides.
        sink_workspace (str): The name or ID of the workspace containing the Lakehouse.
        sink_file_name (str): The name of the Parquet file to write data to. i.e "table_name.parquet".
        sink_directory (str): The directory where the Parquet file will be stored.

        If you choose to pass the sink_file_name and sink_directory from a list, you can leave these blank, but ensure that the corresponding 'sink_file_name' and 'sink_directory' keys are still present in the list of dictionaries used for pipeline parameters.
        You may access required parameters using the `required_params` property.

        The class will resolve Lakehouse and Workspace names to IDs using sempy.fabric.resolve_item and resolve_workspace_id if a name is provided.
    """

    def __init__(
        self,
        sink_lakehouse: str,
        sink_workspace: str,
        sink_file_name: Optional[str] = None,
        sink_directory: Optional[str] = None,
        sink_table_action: Optional[str] = None,
    ) -> None:
        super().__init__()

        # Resolve workspace and lakehouse to IDs if needed
        self.sink_workspace_id = resolve_workspace_id(sink_workspace)
        self.sink_lakehouse_id = resolve_item(
            sink_lakehouse, FabricItemType.LAKEHOUSE, self.sink_workspace_id
        )

        if not self.sink_lakehouse_id:
            raise ValueError("sink_lakehouse (name or id) could not be resolved.")
        if not self.sink_workspace_id:
            raise ValueError("sink_workspace (name or id) could not be resolved.")

        self.sink_file_name = sink_file_name
        self.sink_directory = sink_directory
        self.sink_table_action = sink_table_action

        logger.info(
            f"ParquetFileSink initialized: sink_file_name='{sink_file_name}', sink_directory='{sink_directory}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of keys that are required parameters for the sink.
        For ParquetFileSink, these are the file name and directory.
        """
        return ["sink_file_name", "sink_directory"]

    def to_dict(self) -> dict[str, str]:
        """
        Converts the ParquetFileSink object to a dictionary.
        Only includes sink_file_name and sink_directory if they are not empty.
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
