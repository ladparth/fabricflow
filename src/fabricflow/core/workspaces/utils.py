"""
Microsoft Fabric workspace utility functions.

This module provides utility functions for working with workspace identifiers
in Microsoft Fabric. It simplifies the process of resolving workspace names
to IDs and handling default workspace scenarios.

Functions:
    get_workspace_id: Resolve workspace name to ID or return default workspace ID.

Example:
    ```python
    from fabricflow.core.workspaces.utils import get_workspace_id
    
    # Get default workspace ID
    default_ws_id = get_workspace_id()
    
    # Resolve workspace name to ID
    ws_id = get_workspace_id("MyWorkspace")
    
    # Pass through existing ID
    ws_id = get_workspace_id("abc123-def456-...")
    ```
"""

from typing import Optional
import sempy.fabric as fabric


def get_workspace_id(workspace: Optional[str] = None) -> str:
    """
    Resolve and return a workspace ID, handling various input scenarios.
    
    This utility function provides a consistent way to obtain workspace IDs
    across the FabricFlow library. It handles three scenarios:
    1. No workspace provided: Returns the default/current workspace ID
    2. Workspace name provided: Resolves the name to its corresponding ID
    3. Workspace ID provided: Returns the ID as-is
    
    Args:
        workspace (Optional[str]): The workspace name, ID, or None for default.
                                  If None, returns the current default workspace ID.
                                  If a name, resolves to the corresponding ID.
                                  If already an ID, returns unchanged.
    
    Returns:
        str: The resolved workspace ID.
        
    Raises:
        Exception: If workspace resolution fails or no default workspace is available.
        
    Example:
        ```python
        from fabricflow.core.workspaces.utils import get_workspace_id
        
        # Get the default workspace ID (current context)
        default_id = get_workspace_id()
        
        # Resolve a workspace name to its ID
        workspace_id = get_workspace_id("MyWorkspace")
        
        # Pass through an existing ID unchanged
        same_id = get_workspace_id("12345678-1234-1234-1234-123456789abc")
        ```
        
    Note:
        This function uses Sempy's fabric module for workspace resolution.
        Ensure you have appropriate permissions to access the workspace.
    """

    if workspace is None:
        return fabric.get_workspace_id()

    return fabric.resolve_workspace_id(workspace)
