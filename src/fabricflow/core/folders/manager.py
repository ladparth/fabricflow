"""
Microsoft Fabric folders management via REST API.

This module provides the FabricFoldersManager class for comprehensive management
of Microsoft Fabric folders within workspaces. It implements CRUD (Create, Read, Update, Delete)
operations.

Classes:
    FabricFoldersManager: Complete folder management with REST API integration.

The FabricFoldersManager provides a unified interface for managing all types of
Microsoft Fabric folders within a workspace. It abstracts the REST API complexity
and provides type-safe operations with comprehensive error handling.

Key Features:
    - Unified CRUD operations for Fabric folders
    - Automatic workspace resolution (name or ID)
    - Paginated listing support for large folder collections
    - Comprehensive error handling and validation
    - Support for folder definitions and metadata

Folder Lifecycle:
    1. Create folder with display name and optional parent folder
    2. Retrieve folder details by ID
    3. Update folder properties and metadata
    4. List and filter folders in workspace
    5. Delete folder when no longer needed

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.core.folders.manager import FabricFoldersManager

    client = FabricRestClient()
    manager = FabricFoldersManager(client, "MyWorkspace")

    # Create a new Folder
    folder = manager.create_folder(
        display_name="My new folder,
    )

    # List all folders in workspace
    folders = manager.list_folders(paged=True)

    # Get specific folder details
    folder_details = manager.get_folder(folder['id'])

    # Update folder description
    manager.update_folder(folder['id'], {
        'displayName': 'Updated folder display name'
    })

    # Delete folder
    manager.delete_folder(folder['id'])
    ```

Security Note:
    All operations require appropriate Microsoft Fabric permissions for the target
    workspace. Folder deletion is permanent and cannot be undone.

Dependencies:
    - sempy.fabric: For FabricRestClient integration
    - fabricflow.core.workspaces.utils: For workspace ID resolution
"""

from typing import Optional, Dict, Any
from sempy.fabric import FabricRestClient
from ..workspaces.utils import get_workspace_id
from .utils import resolve_folder


class FabricFoldersManager:
    """
    Manager for Microsoft Fabric Folders via REST API.
    Implements basic CRUD operations for folders in a Fabric workspace.
    """

    def __init__(
        self, client: FabricRestClient, workspace: Optional[str] = None
    ) -> None:
        """
        Initialize the FabricFoldersManager.

        Args:
            client (FabricRestClient): An authenticated FabricRestClient instance.
            workspace (Optional[str]): The Fabric workspace name or ID. If None, the default workspace will be used.
        """
        self.client = client
        self.workspace_id = get_workspace_id(workspace)
        if not isinstance(self.client, FabricRestClient):
            raise TypeError(
                "Client must be an instance of FabricRestClient from sempy.fabric"
            )

    def create_folder(
        self,
        display_name: str,
        parent_folder_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new folder in the Fabric workspace.

        Args:
            display_name (str): The display name for the folder.
            parent_folder_name (Optional[Any]): Parent folder Name or ID (optional).

        Returns:
            Dict[str, Any]: The created folder details as a dictionary.
        """

        payload: Dict[str, Any] = {"displayName": display_name}
        if parent_folder_name is not None:
            payload["parentFolderId"] = resolve_folder(parent_folder_name)
        url: str = f"/v1/workspaces/{self.workspace_id}/folders"
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_folder(self, folder_id: str) -> Dict[str, Any]:
        """
        Retrieve an folder by its ID from the Fabric workspace.

        Args:
            folder_id (str): The ID of the folder to retrieve.

        Returns:
            Dict[str, Any]: The folder details as a dictionary.
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/folders/{folder_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def update_folder(self, folder_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing folder in the Fabric workspace.

        Args:
            folder_id (str): The ID of the folder to update.
            updates (Dict[str, Any]): The fields to update.

        Returns:
            Dict[str, Any]: The updated folder details as a dictionary.
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/folders/{folder_id}"
        response = self.client.patch(url, json=updates)
        response.raise_for_status()
        return response.json()

    def delete_folder(self, folder_id: str) -> None:
        """
        Delete an folder from the Fabric workspace.

        Args:
            folder_id (str): The ID of the folder to delete.
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/folders/{folder_id}"
        response = self.client.delete(url)
        response.raise_for_status()

    def list_folders(
        self, params: Optional[Dict[str, Any]] = None, paged: bool = False
    ) -> list | Dict[str, Any]:
        """
        List all folders in the Fabric workspace, optionally filtered by parameters.

        Args:
            params (Optional[Dict[str, Any]]): Query parameters for filtering the folders (optional).
            paged (bool): If True, returns all pages as a flat list using get_paged().

        Returns:
            list or Dict[str, Any]: The list of folders (paged or single response).
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/folders"
        if paged:
            return self.client.get_paged(url, params=params)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
