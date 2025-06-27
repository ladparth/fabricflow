from fabricflow.core.workspaces.manager import FabricWorkspacesManager
from sempy.fabric import FabricRestClient
from typing import Optional, Any


def create_workspace(
    client: FabricRestClient,
    workspace_name: str,
    capacity_name: Optional[str] = None,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a new workspace in a specified capacity.
    Args:
        workspace_name (str): The name of the workspace to create.
        capacity_name (Optional[str]): The name of the capacity where the workspace will be created.
        description (Optional[str]): An optional description for the workspace.
    """
    ws: FabricWorkspacesManager = FabricWorkspacesManager(client)
    workspace: dict[str, Any] = ws.create_workspace(
        display_name=workspace_name,
        description=description,
    )
    print(f"Workspace '{workspace_name}' created successfully.")

    if capacity_name:
        ws.assign_to_capacity(workspace_name, capacity_name)
        print(f"Workspace '{workspace_name}' assigned to capacity '{capacity_name}'.")

    return workspace
