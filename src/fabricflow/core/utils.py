"""
Core utility functions for Microsoft Fabric workspace and resource management.

This module provides high-level convenience functions for common operations
in Microsoft Fabric, such as creating workspaces and assigning them to capacities.

Functions:
    create_workspace: Create a new workspace and optionally assign it to a capacity.

These utilities wrap the lower-level managers to provide simple, one-line solutions
for common setup tasks in Fabric environments.

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.core.utils import create_workspace

    client = FabricRestClient()
    workspace = create_workspace(
        client,
        "MyNewWorkspace",
        capacity_name="MyCapacity",
        description="A workspace for data processing"
    )
    ```
"""

from fabricflow.core.workspaces.manager import FabricWorkspacesManager
from sempy.fabric import FabricRestClient
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


def create_workspace(
    client: FabricRestClient,
    workspace_name: str,
    capacity_name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a new Microsoft Fabric workspace and optionally assign it to a capacity.

    This function provides a convenient way to create a new workspace and assign it
    to a specific capacity in a single operation. It handles the workspace creation
    and capacity assignment steps automatically.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        workspace_name (str): Name for the new workspace. Must be unique within the tenant.
        capacity_name (Optional[str]): Name of the capacity to assign the workspace to.
                                     If None, the workspace will not be assigned to any capacity.
        description (Optional[str]): Optional description for the workspace.

    Returns:
        dict[str, Any]: Dictionary containing the created workspace details including:
                       - id: Workspace ID
                       - displayName: Workspace display name
                       - description: Workspace description (if provided)
                       - capacityId: Capacity ID (if assigned)

    Raises:
        Exception: If workspace creation fails or capacity assignment fails.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow as create_workspace

        client = FabricRestClient()

        # Create workspace without capacity assignment
        workspace = create_workspace(client, "MyWorkspace")

        # Create workspace with capacity assignment
        workspace = create_workspace(
            client,
            "MyWorkspace",
            capacity_name="MyCapacity",
            description="Data processing workspace"
        )
        ```

    Note:
        This function prints status messages during execution. If capacity_name
        is provided, the workspace will be assigned to that capacity after creation.
    """
    ws: FabricWorkspacesManager = FabricWorkspacesManager(client)
    workspace: dict[str, Any] = ws.create_workspace(
        display_name=workspace_name,
        description=description,
    )
    logger.info("Workspace '%s' created successfully.", workspace_name)

    if capacity_name:
        ws.assign_to_capacity(workspace_name, capacity_name)
        logger.info(
            "Workspace '%s' assigned to capacity '%s'.", workspace_name, capacity_name
        )

    return workspace
