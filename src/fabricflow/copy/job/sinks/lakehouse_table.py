from ..base import BaseSink
from ..types import SinkType
import logging
from logging import Logger
from typing import Optional
from sempy.fabric import resolve_workspace_id
from ....core.items.utils import resolve_item
from ....core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


class LakehouseTableSink(BaseSink):
    """
    Represents a sink for writing data to a Lakehouse table.
    Defines attributes specific to Lakehouse tables.

    Attributes:
        sink_lakehouse (str): The name or ID of the Lakehouse where the table resides.
        sink_workspace (str): The name or ID of the workspace containing the Lakehouse.
        sink_table_name (str): The name of the table to write data to.
        sink_schema_name (str): The name of the schema containing the table.
        sink_table_action (str): The action to perform on the table (e.g., "Overwrite", "Append").

        If you choose to pass the sink_table_name, sink_schema_name, or sink_table_action from a list, you can leave these blank, but ensure that the corresponding 'sink_table_name', 'sink_schema_name', and 'sink_table_action' keys are still present in the list of dictionaries used for pipeline parameters.
        You may access required parameters using the `required_params` property.

        The class will resolve Lakehouse and Workspace names to IDs using sempy.fabric.resolve_item and resolve_workspace_id if a name is provided.
    """

    def __init__(
        self,
        sink_lakehouse: str,
        sink_workspace: str,
        sink_table_name: Optional[str] = None,
        sink_schema_name: Optional[str] = None,
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

        self.sink_table_name = sink_table_name
        self.sink_schema_name = sink_schema_name
        self.sink_table_action = sink_table_action

        logger.info(
            f"LakehouseTableSink initialized: sink_table_name='{sink_table_name}', sink_table_action='{sink_table_action}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns a list of keys that are required parameters for the sink.
        For LakehouseTableSink, these are the table and schema names and table action.
        """
        return ["sink_table_name", "sink_schema_name", "sink_table_action"]

    def to_dict(self) -> dict[str, str]:
        """
        Converts the LakehouseTableSink object to a dictionary.
        Only includes sink_table_name, sink_schema_name, and sink_table_action if they are not empty.
        """
        result: dict[str, str] = {
            "sink_type": SinkType.LAKEHOUSE_TABLE.value,
            "sink_lakehouse_id": self.sink_lakehouse_id,
            "sink_workspace_id": self.sink_workspace_id,
        }
        if self.sink_table_name:
            result["sink_table_name"] = self.sink_table_name
        if self.sink_schema_name:
            result["sink_schema_name"] = self.sink_schema_name
        if self.sink_table_action:
            result["sink_table_action"] = self.sink_table_action
        return result
