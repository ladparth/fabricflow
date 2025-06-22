import logging
from logging import Logger
from sempy.fabric import FabricRestClient
from typing import Optional
from .templates import DataPipelineTemplates, get_template
from ..core.items.manager import FabricCoreItemsManager
from ..core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


def create_data_pipeline(
    client: FabricRestClient,
    template: DataPipelineTemplates,
    workspace: Optional[str] = None,
) -> dict:
    """
    Create a Microsoft Fabric data pipeline using a template.

    Args:
        client (FabricRestClient): The FabricRestClient instance for API calls.
        template (DataPipelineTemplates): The data pipeline template enum value.
        workspace (Optional[str]): Workspace name or ID. If None, uses the default workspace.

    Returns:
        dict: The created data pipeline details.
    Raises:
        FileNotFoundError: If the template file does not exist.
    """

    # Get the base64-encoded template definition in correct format
    definition_dict: dict = get_template(template)

    # Prepare the payload for FabricCoreItemsManager
    items_manager: FabricCoreItemsManager = FabricCoreItemsManager(client, workspace)

    # Only pass supported parameters to create_item
    return items_manager.create_item(
        display_name=template.value,
        item_type=FabricItemType.DATA_PIPELINE,
        definition=definition_dict["definition"],
    )
