"""
Microsoft Fabric workspaces management via REST API.

This module provides the FabricWorkspacesManager class for comprehensive workspace
management in Microsoft Fabric. It implements CRUD (Create, Read, Update, Delete)
operations for workspaces and capacity assignment functionality.

Classes:
    FabricWorkspacesManager: Complete workspace management with REST API integration.

The FabricWorkspacesManager provides a high-level interface for all workspace-related
operations in Microsoft Fabric, including creating new workspaces, retrieving workspace
details, updating workspace properties, deleting workspaces, and assigning workspaces
to specific capacities.

Key Features:
    - Workspace CRUD operations with proper error handling
    - Automatic workspace and capacity name-to-ID resolution
    - Capacity assignment with validation
    - Paginated listing support for large workspace collections
    - Type-safe interfaces with comprehensive documentation

Workspace Lifecycle:
    1. Create workspace with optional description
    2. Assign to capacity for compute resources
    3. Manage workspace properties and settings
    4. List and filter workspaces
    5. Delete when no longer needed (permanent operation)

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.core.workspaces.manager import FabricWorkspacesManager
    
    client = FabricRestClient()
    manager = FabricWorkspacesManager(client)
    
    # Create a new workspace
    workspace = manager.create_workspace(
        display_name="Data Analytics Workspace",
        description="Workspace for sales analytics and reporting"
    )
    
    # Assign to a capacity
    manager.assign_to_capacity("Data Analytics Workspace", "Premium Capacity")
    
    # List all workspaces
    workspaces = manager.list_workspaces(paged=True)
    
    # Update workspace description
    manager.update_workspace(workspace['id'], {
        'description': 'Updated workspace description'
    })
    ```

Security Note:
    All operations require appropriate Microsoft Fabric permissions. Workspace
    deletion is a permanent operation that cannot be undone - use with caution.
    
Dependencies:
    - sempy.fabric: For FabricRestClient and workspace resolution
    - fabricflow.core.capacities: For capacity ID resolution
    - fabricflow.core.workspaces.utils: For workspace utilities
"""

from typing import Optional, Dict, Any, List
from sempy.fabric import FabricRestClient
from .utils import get_workspace_id
from ..capacities import resolve_capacity_id


class FabricWorkspacesManager:
    """

    Manager for Microsoft Fabric Workspaces via REST API.
    Provides CRUD operations for workspaces using the Sempy FabricRestClient.

    """

    def __init__(self, client: FabricRestClient) -> None:
        """
        Initialize the FabricWorkspacesManager.

        Args:
            client (FabricRestClient): An authenticated FabricRestClient instance.
        """
        self.client = client
        if not isinstance(self.client, FabricRestClient):
            raise TypeError(
                "client must be an instance of FabricRestClient from sempy.fabric"
            )

    def __str__(self) -> str:
        return f"FabricWorkspacesManager(client={self.client})"

    def __repr__(self) -> str:
        return self.__str__()

    def create_workspace(
        self, display_name: str, description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new workspace.

        Args:
            display_name (str): The display name for the workspace.
            description (Optional[str]): The description for the workspace.

        Returns:
            Dict[str, Any]: The created workspace details as a dictionary.
        """
        payload: dict[str, str] = {"displayName": display_name}
        if description:
            payload["description"] = description
        url = "/v1/workspaces"
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """
        Retrieve a workspace by its ID.

        Args:
            workspace_id (str): The ID of the workspace to retrieve.

        Returns:
            Dict[str, Any]: The workspace details as a dictionary.
        """
        url: str = f"/v1/workspaces/{workspace_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def update_workspace(
        self, workspace_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing workspace.

        Args:
            workspace_id (str): The ID of the workspace to update.
            updates (Dict[str, Any]): The fields to update.

        Returns:
            Dict[str, Any]: The updated workspace details as a dictionary.
        """
        url: str = f"/v1/workspaces/{workspace_id}"
        response = self.client.patch(url, json=updates)
        response.raise_for_status()
        return response.json()

    def delete_workspace(self, workspace_id: str) -> None:
        """
        Delete an existing workspace.

        Permanently removes a workspace and all its contents from Microsoft Fabric.
        This operation cannot be undone.

        Args:
            workspace_id (str): The unique identifier of the workspace to delete.

        Returns:
            None

        Raises:
            HTTPError: If the workspace doesn't exist or the user lacks permissions.
            
        Warning:
            This operation permanently deletes the workspace and all its contents
            including items, data, and configurations. Use with caution.
        """
        url: str = f"/v1/workspaces/{workspace_id}"
        response = self.client.delete(url)
        response.raise_for_status()

    def list_workspaces(
        self, params: Optional[Dict[str, Any]] = None, paged: bool = False
    ) -> List[Any] | Dict[str, Any]:
        """
        List all workspaces, optionally filtered by parameters.

        Args:
            params (Optional[Dict[str, Any]]): Query parameters for filtering the workspaces (optional).
            paged (bool): If True, returns all pages as a flat list using get_paged().

        Returns:
            list or Dict[str, Any]: The list of workspaces (paged or single response).
        """
        url: str = "/v1/workspaces"
        if paged:
            return self.client.get_paged(url, params=params)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def assign_to_capacity(self, workspace: str, capacity: str) -> str:
        """
        Assign the specified workspace to the specified capacity.

        This method assigns a Microsoft Fabric workspace to a specific capacity,
        which determines the compute resources and pricing tier for the workspace.
        Both workspace and capacity can be specified by name or ID.

        Args:
            workspace (str): The ID or name of the workspace to assign.
                If a name is provided, it will be resolved to an ID automatically.
            capacity (str): The ID or name of the capacity to assign the workspace to.
                If a name is provided, it will be resolved to an ID automatically.

        Returns:
            str: A success message indicating the workspace was assigned to the capacity.

        Raises:
            ValueError: If the capacity name/ID cannot be resolved to a valid capacity.
            HTTPError: If the assignment request fails (e.g., insufficient permissions,
                invalid workspace/capacity, or capacity at full utilization).

        Example:
            >>> manager = FabricWorkspacesManager(client)
            >>> result = manager.assign_to_capacity("my-workspace", "my-capacity")
            >>> print(result)
            "Workspace 'my-workspace' assigned to capacity 'my-capacity' successfully."
        """
        workspace_id: str = get_workspace_id(workspace)
        capacity_id: str | None = resolve_capacity_id(self.client, capacity)
        if not capacity_id:
            raise ValueError(f"Capacity '{capacity}' could not be resolved to an ID.")
        url: str = f"/v1/workspaces/{workspace_id}/assignToCapacity"
        payload: dict[str, str] = {"capacityId": capacity_id}
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        
        return (
            f"Workspace '{workspace}' assigned to capacity '{capacity}' successfully."
        )
