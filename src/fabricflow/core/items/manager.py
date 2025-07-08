"""
Microsoft Fabric core items management via REST API.

This module provides the FabricCoreItemsManager class for comprehensive management
of Microsoft Fabric items within workspaces. It implements CRUD (Create, Read, Update, Delete)
operations for all supported Fabric item types including Lakehouses, Data Pipelines,
Reports, Semantic Models, and many others.

Classes:
    FabricCoreItemsManager: Complete item management with REST API integration.

The FabricCoreItemsManager provides a unified interface for managing all types of
Microsoft Fabric items within a workspace. It abstracts the REST API complexity
and provides type-safe operations with comprehensive error handling.

Supported Item Types:
    All item types defined in FabricItemType enum are supported, including:
    - Data Storage: Lakehouses, Warehouses, SQL Databases
    - Analytics: Reports, Dashboards, Semantic Models  
    - Data Processing: Data Pipelines, Dataflows, Notebooks
    - Real-time: Eventstreams, Eventhouses, KQL components
    - Machine Learning: ML Models, ML Experiments
    - Development: Environments, Spark Job Definitions
    - And many more...

Key Features:
    - Unified CRUD operations for all Fabric item types
    - Automatic workspace resolution (name or ID)
    - Type-safe item creation with FabricItemType enum
    - Paginated listing support for large item collections
    - Comprehensive error handling and validation
    - Support for item definitions and metadata

Item Lifecycle:
    1. Create item with display name, type, and optional definition
    2. Retrieve item details by ID
    3. Update item properties and metadata
    4. List and filter items in workspace
    5. Delete item when no longer needed

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.core.items.manager import FabricCoreItemsManager
    from fabricflow.core.items.types import FabricItemType
    
    client = FabricRestClient()
    manager = FabricCoreItemsManager(client, "MyWorkspace")
    
    # Create a new Lakehouse
    lakehouse = manager.create_item(
        display_name="Sales Data Lakehouse",
        item_type=FabricItemType.LAKEHOUSE
    )
    
    # Create a data pipeline with definition
    pipeline = manager.create_item(
        display_name="ETL Pipeline",
        item_type=FabricItemType.DATA_PIPELINE,
        definition=pipeline_definition
    )
    
    # List all items in workspace
    items = manager.list_items(paged=True)
    
    # Get specific item details
    item_details = manager.get_item(lakehouse['id'])
    
    # Update item description
    manager.update_item(lakehouse['id'], {
        'description': 'Updated lakehouse for sales analytics'
    })
    
    # Delete item
    manager.delete_item(pipeline['id'])
    ```

Security Note:
    All operations require appropriate Microsoft Fabric permissions for the target
    workspace. Item deletion is permanent and cannot be undone.
    
Dependencies:
    - sempy.fabric: For FabricRestClient integration
    - fabricflow.core.workspaces.utils: For workspace ID resolution
    - fabricflow.core.items.types: For FabricItemType definitions
"""

from typing import Optional, Dict, Any
from sempy.fabric import FabricRestClient
from ..workspaces.utils import get_workspace_id
from .types import FabricItemType


class FabricCoreItemsManager:
    """
    Manager for Microsoft Fabric Core Items via REST API.
    Implements basic CRUD operations for items in a Fabric workspace.

    Supported item types are defined in the FabricItemType enum.
    For a full list, see: https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item
    """

    def __init__(
        self, client: FabricRestClient, workspace: Optional[str] = None
    ) -> None:
        """
        Initialize the FabricCoreItemsManager.

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

    def create_item(
        self,
        display_name: str,
        item_type: FabricItemType,
        definition: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Create a new item in the Fabric workspace.

        Args:
            display_name (str): The display name for the item.
            item_type (FabricItemType): The type of item to create.
            definition (Optional[Any]): The item definition (optional).

        Returns:
            Dict[str, Any]: The created item details as a dictionary.
        """
        payload: Dict[str, Any] = {"displayName": display_name, "type": item_type.value}
        if definition is not None:
            payload["definition"] = definition
        url: str = f"/v1/workspaces/{self.workspace_id}/items"
        response = self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def get_item(self, item_id: str) -> Dict[str, Any]:
        """
        Retrieve an item by its ID from the Fabric workspace.

        Args:
            item_id (str): The ID of the item to retrieve.

        Returns:
            Dict[str, Any]: The item details as a dictionary.
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/items/{item_id}"
        response = self.client.get(url)
        response.raise_for_status()
        return response.json()

    def update_item(self, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing item in the Fabric workspace.

        Args:
            item_id (str): The ID of the item to update.
            updates (Dict[str, Any]): The fields to update.

        Returns:
            Dict[str, Any]: The updated item details as a dictionary.
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/items/{item_id}"
        response = self.client.patch(url, json=updates)
        response.raise_for_status()
        return response.json()

    def delete_item(self, item_id: str) -> None:
        """
        Delete an item from the Fabric workspace.

        Args:
            item_id (str): The ID of the item to delete.
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/items/{item_id}"
        response = self.client.delete(url)
        response.raise_for_status()

    def list_items(
        self, params: Optional[Dict[str, Any]] = None, paged: bool = False
    ) -> list | Dict[str, Any]:
        """
        List all items in the Fabric workspace, optionally filtered by parameters.

        Args:
            params (Optional[Dict[str, Any]]): Query parameters for filtering the items (optional).
            paged (bool): If True, returns all pages as a flat list using get_paged().

        Returns:
            list or Dict[str, Any]: The list of items (paged or single response).
        """
        url: str = f"/v1/workspaces/{self.workspace_id}/items"
        if paged:
            return self.client.get_paged(url, params=params)
        response = self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()
