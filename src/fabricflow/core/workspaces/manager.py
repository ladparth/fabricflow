from typing import Optional, Dict, Any
from sempy.fabric import FabricRestClient


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
        Delete a workspace by its ID.

        Args:
            workspace_id (str): The ID of the workspace to delete.
        """
        url: str = f"/v1/workspaces/{workspace_id}"
        response = self.client.delete(url)
        response.raise_for_status()

    def list_workspaces(
        self, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        List all workspaces, optionally filtered by parameters.

        Args:
            params (Optional[Dict[str, Any]]): Query parameters for filtering the workspaces (optional).

        Returns:
            Dict[str, Any]: The list of workspaces as a dictionary.
        """
        url: str = "/v1/workspaces"
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
