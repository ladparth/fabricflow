from .base import BaseSink
from .types import SinkType
import logging
from logging import Logger
from typing import Optional
from sempy.fabric import resolve_workspace_id
from ...core.items.utils import resolve_item
from ...core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


class LakehouseTableSink(BaseSink):
    """
    Represents a sink for writing data to a Microsoft Fabric Lakehouse table.
    
    This sink handles writing data to tables within a Lakehouse in Microsoft Fabric.
    It automatically resolves workspace and lakehouse names to their corresponding IDs
    and supports various table operations like overwrite and append.
    
    The sink can be configured with specific table details at initialization or these
    can be provided later through the items parameter in pipeline activities.
    
    Attributes:
        sink_workspace_id (str): Resolved workspace ID containing the Lakehouse.
        sink_lakehouse_id (str): Resolved Lakehouse ID where the table resides.
        sink_table_name (Optional[str]): Name of the target table.
        sink_schema_name (Optional[str]): Schema name containing the table.
        sink_table_action (Optional[str]): Action to perform ("Overwrite", "Append", etc.).
        
    Args:
        sink_lakehouse (str): Name or ID of the target Lakehouse.
        sink_workspace (str): Name or ID of the workspace containing the Lakehouse.
        sink_schema_name (Optional[str]): Schema name. Can be provided later via items.
        sink_table_name (Optional[str]): Table name. Can be provided later via items.
        sink_table_action (Optional[str]): Table action. Can be provided later via items.
        
    Raises:
        ValueError: If workspace or lakehouse cannot be resolved.
        
    Note:
        If table details (name, schema, action) are not provided during initialization,
        they must be included in the items list when executing pipeline activities.
        Use the `required_params` property to see which parameters are mandatory.
        
    Example:
        ```python
        # Initialize with all details
        sink = LakehouseTableSink(
            sink_lakehouse="MyLakehouse",
            sink_workspace="MyWorkspace", 
            sink_table_name="SalesData",
            sink_schema_name="dbo",
            sink_table_action="Overwrite"
        )
        
        # Initialize for use with items list
        sink = LakehouseTableSink(
            sink_lakehouse="MyLakehouse",
            sink_workspace="MyWorkspace"
        )
        # Table details provided later in copy.items([...])
        ```
    """

    def __init__(
        self,
        sink_lakehouse: str,
        sink_workspace: str,
        sink_schema_name: Optional[str] = None,
        sink_table_name: Optional[str] = None,
        sink_table_action: Optional[str] = None,
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

        self.sink_table_name = sink_table_name
        self.sink_schema_name = sink_schema_name
        self.sink_table_action = sink_table_action

        logger.info(
            f"LakehouseTableSink initialized: sink_table_name='{sink_table_name}', sink_table_action='{sink_table_action}'"
        )

    @property
    def required_params(self) -> list[str]:
        """
        Returns the list of required parameter names for this sink type.
        
        For LakehouseTableSink, the required parameters are table name, schema name,
        and table action. These must be provided either during initialization or
        in the items list when executing pipeline activities.
        
        Returns:
            list[str]: List of required parameter names:
                      ["sink_table_name", "sink_schema_name", "sink_table_action"]
        """
        return ["sink_table_name", "sink_schema_name", "sink_table_action"]

    def to_dict(self) -> dict[str, str]:
        """
        Converts the LakehouseTableSink configuration to a dictionary.
        
        This method creates a dictionary representation suitable for use in
        pipeline execution payloads. It includes the resolved workspace and
        lakehouse IDs, sink type, and any configured table details.
        
        Returns:
            dict[str, str]: Dictionary containing:
                - sink_type: Always "LakehouseTable"
                - sink_lakehouse_id: Resolved Lakehouse ID
                - sink_workspace_id: Resolved workspace ID
                - sink_table_name: Table name (if configured)
                - sink_schema_name: Schema name (if configured) 
                - sink_table_action: Table action (if configured)
                
        Note:
            Optional parameters (table_name, schema_name, table_action) are only
            included if they were provided during initialization.
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
