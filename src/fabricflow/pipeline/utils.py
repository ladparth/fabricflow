"""
Microsoft Fabric data pipeline utility functions.

This module provides high-level utility functions for creating and managing
data pipelines in Microsoft Fabric. It simplifies common pipeline operations
by wrapping the lower-level API calls with convenient interfaces.

Functions:
    create_data_pipeline: Create a new data pipeline from a template.

These utilities work with the template system to provide quick deployment
of pre-configured pipeline patterns for common data integration scenarios.

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.pipeline.utils import create_data_pipeline
    from fabricflow.pipeline.templates import DataPipelineTemplates

    client = FabricRestClient()
    pipeline = create_data_pipeline(
        client,
        DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE,
        workspace="MyWorkspace"
    )
    ```
"""

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
    Create a Microsoft Fabric data pipeline using a predefined template.

    This function creates a new data pipeline in the specified workspace using
    one of the available templates. Templates provide pre-configured pipeline
    definitions for common data integration patterns.

    The pipeline will be created with the template name as the display name
    and will be ready for parameterization and execution.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        template (DataPipelineTemplates): The template to use for pipeline creation.
                                         Must be a value from the DataPipelineTemplates enum.
        workspace (Optional[str]): Target workspace name or ID. If None, uses the
                                  current default workspace.

    Returns:
        dict: Dictionary containing the created pipeline details including:
             - id: Pipeline ID
             - displayName: Pipeline display name (same as template name)
             - type: Item type (always "DataPipeline")
             - workspaceId: Workspace ID where pipeline was created

    Raises:
        FileNotFoundError: If the template file cannot be found.
        Exception: If pipeline creation fails due to permissions or other issues.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.pipeline.utils import create_data_pipeline
        from fabricflow.pipeline.templates import DataPipelineTemplates

        client = FabricRestClient()

        # Create a copy pipeline template
        pipeline = create_data_pipeline(
            client,
            DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE,
            workspace="MyWorkspace"
        )

        print(f"Created pipeline: {pipeline['displayName']} (ID: {pipeline['id']})")
        ```

    Note:
        The created pipeline will contain parameter placeholders that need to be
        populated when executing the pipeline. Use the Copy or Lookup classes
        to execute the pipeline with appropriate parameters.
    """

    # Get the base64-encoded template definition in correct format
    definition_dict: dict = get_template(template)

    # Prepare the payload for FabricCoreItemsManager
    items_manager: FabricCoreItemsManager = FabricCoreItemsManager(client, workspace)

    # Only pass supported parameters to create_item
    logger.info(
        f"Creating data pipeline with template: {template.value} in workspace: {workspace}"
    )
    return items_manager.create_item(
        display_name=template.value,
        item_type=FabricItemType.DATA_PIPELINE,
        definition=definition_dict["definition"],
    )
