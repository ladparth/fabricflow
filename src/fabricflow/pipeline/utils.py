"""Microsoft Fabric data pipeline utility functions."""

import logging
from logging import Logger
from sempy.fabric import FabricRestClient
from typing import Any, Dict, Optional, Union
from .templates import DataPipelineTemplates, get_template
from ..core.items.manager import FabricCoreItemsManager
from ..core.items.types import FabricItemType

logger: Logger = logging.getLogger(__name__)


def create_data_pipeline(
    client: FabricRestClient,
    template: Union[DataPipelineTemplates, Dict[str, Any], str],
    workspace: Optional[str] = None,
    display_name: Optional[str] = None,
) -> dict:
    """
    Create a Microsoft Fabric data pipeline using a template, JSON definition, or file path.

    Supports:
        - DataPipelineTemplates enum value (predefined template)
        - dict (pipeline JSON definition)
        - str (file path to pipeline definition)

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        template (DataPipelineTemplates | dict | str): Template enum, pipeline JSON dict, or file path.
        workspace (Optional[str]): Target workspace name or ID. If None, uses the default workspace.
        display_name (Optional[str]): Display name for the pipeline. if file path is provided, the file name will be used as the display name.

    Returns:
        dict: Details of the created pipeline (id, displayName, type, workspaceId).

    Raises:
        FileNotFoundError: If the template file cannot be found.
        Exception: If pipeline creation fails.

    Example:
        pipeline = create_data_pipeline(client, DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE, workspace="MyWorkspace")
        pipeline = create_data_pipeline(client, {"name": "MyPipeline", "properties": {"activities": [...] }}, workspace="MyWorkspace")
        pipeline = create_data_pipeline(client, "path/to/pipeline.json", workspace="MyWorkspace")
    """
    # Validate template type

    if not isinstance(template, (DataPipelineTemplates, dict, str)):
        raise TypeError(
            "template must be a DataPipelineTemplates enum, a dict (pipeline definition), or a str (file path)"
        )

    # Get the base64-encoded template definition in correct format
    definition_dict: dict = get_template(template)

    # Resolve display name
    resolved_display_name: str = display_name or definition_dict.get(
        "displayName", "Untitled Pipeline"
    )

    # Only pass supported parameters to create_item
    logger.info(
        f"Creating data pipeline with template: {resolved_display_name} in workspace: {workspace}"
    )

    # Prepare the payload for FabricCoreItemsManager
    items_manager: FabricCoreItemsManager = FabricCoreItemsManager(client, workspace)

    return items_manager.create_item(
        display_name=resolved_display_name,
        item_type=FabricItemType.DATA_PIPELINE,
        definition=definition_dict["definition"],
    )
