"""
Microsoft Fabric items utility functions.

This module provides utility functions for working with Microsoft Fabric items,
including resolution of item names to IDs and validation of item identifiers.

Items in Fabric represent various resources like Lakehouses, Datasets, Reports,
and other workspace artifacts that can be managed through the REST API.

Functions:
    resolve_item: Resolve an item name or validate an ID to get the item ID.
    is_valid_item_id: Check if an item ID or name is valid in a workspace.

Example:
    ```python
    from fabricflow.core.items.utils import resolve_item
    from fabricflow.core.items.types import FabricItemType
    
    # Resolve a Lakehouse name to its ID
    lakehouse_id = resolve_item(
        "MyLakehouse", 
        FabricItemType.LAKEHOUSE, 
        "MyWorkspace"
    )
    ```
"""

from uuid import UUID
from typing import Any
from .types import FabricItemType
from sempy.fabric import resolve_item_id, resolve_item_name


def resolve_item(
    item: str,
    item_type: FabricItemType | None = None,
    workspace: str | None = None,
) -> str | Any:
    """
    Resolve an item name to its ID or validate an existing ID.
    
    This function handles both item names and IDs, providing a consistent way
    to obtain item IDs throughout the FabricFlow library. It first attempts
    to parse the input as a UUID, and if that fails, treats it as a name
    to be resolved.
    
    Args:
        item (str): The item name or ID to resolve. Can be either:
                   - A display name (e.g., "MyLakehouse")
                   - A UUID string (e.g., "12345678-1234-1234-1234-123456789abc")
        item_type (FabricItemType | None): The type of item to resolve.
                                          Used for validation and scoping the search.
                                          If None, searches across all item types.
        workspace (str | None): The workspace name or ID where the item resides.
                               If None, uses the current workspace context.
    
    Returns:
        str: The resolved item ID as a string.
        
    Raises:
        ValueError: If the item cannot be resolved or an invalid ID is provided.
        Exception: If item resolution fails due to permissions or other issues.
        
    Example:
        ```python
        from fabricflow.core.items.utils import resolve_item
        from fabricflow.core.items.types import FabricItemType
        
        # Resolve by name
        lakehouse_id = resolve_item(
            "MyLakehouse",
            FabricItemType.LAKEHOUSE,
            "MyWorkspace"
        )
        
        # Validate existing ID
        validated_id = resolve_item(
            "12345678-1234-1234-1234-123456789abc",
            FabricItemType.LAKEHOUSE,
            "MyWorkspace"
        )
        ```
        
    Note:
        This function uses Sempy's fabric module for item resolution.
        Ensure you have appropriate permissions to access the item and workspace.
    """

    _item_type: str | None = item_type.value if item_type else None

    try:
        item_uuid: UUID = UUID(item)
    except (ValueError, TypeError):
        return resolve_item_id(item, _item_type, workspace)

    if is_valid_item_id(item_uuid, item_type, workspace):
        return str(item_uuid)
    else:
        raise ValueError(f"Invalid item ID: {item_uuid} in workspace {workspace}")


def is_valid_item_id(
    item: str | UUID,
    item_type: FabricItemType | None = None,
    workspace: str | None = None,
) -> bool:
    """
    Check if an item ID or name is valid in the specified workspace.
    
    This function validates whether an item exists and is accessible in the
    given workspace. It can be used to verify item IDs before using them
    in operations or to check if an item name exists.
    
    Args:
        item (str | UUID): The item name or ID to validate. Can be either:
                          - A display name (e.g., "MyLakehouse")
                          - A UUID string or UUID object
        item_type (FabricItemType | None): The expected type of the item.
                                          Used for validation and scoping.
                                          If None, checks across all item types.
        workspace (str | None): The workspace name or ID to check within.
                               If None, uses the current workspace context.
    
    Returns:
        bool: True if the item is valid and accessible, False otherwise.
        
    Example:
        ```python
        from fabricflow.core.items.utils import is_valid_item_id
        from fabricflow.core.items.types import FabricItemType
        
        # Check if a Lakehouse exists
        if is_valid_item_id("MyLakehouse", FabricItemType.LAKEHOUSE, "MyWorkspace"):
            print("Lakehouse found")
        else:
            print("Lakehouse not found or not accessible")
            
        # Validate an ID
        valid_id = is_valid_item_id(
            "12345678-1234-1234-1234-123456789abc",
            FabricItemType.LAKEHOUSE,
            "MyWorkspace"
        )
        ```
        
    Note:
        This function catches all exceptions and returns False for any errors,
        including permission issues, network problems, or item not found.
    """
    try:
        _item_type: str | None = item_type.value if item_type else None
        resolved_name = resolve_item_name(item, _item_type, workspace)
        return isinstance(resolved_name, str)
    except Exception:
        return False
