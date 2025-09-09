"""
Microsoft Fabric folders utility functions.

This module provides utility functions for working with Microsoft Fabric folders,
including resolution of folder names to IDs and validation of folder identifiers.

Functions:
    resolve_folder: Resolve an folder name or validate an ID to get the folder ID.
    is_valid_folder_id: Check if an folder ID or name is valid in a workspace.

Example:
    ```python
    from fabricflow.core.folders.utils import resolve_folder

    # Resolve a Lakehouse name to its ID
    folder_id = resolve_folder(
        "MyFolder",
        "MyWorkspace"
    )
    ```
"""

from uuid import UUID
from typing import Any
from sempy.fabric import resolve_folder_id, resolve_folder_path


def resolve_folder(
    folder: str,
    workspace: str | None = None,
) -> str | Any:
    """
    Resolve an folder name to its ID or validate an existing ID.

    This function handles both folder names and IDs, providing a consistent way
    to obtain folder IDs throughout the FabricFlow library. It first attempts
    to parse the input as a UUID, and if that fails, treats it as a name
    to be resolved.

    Args:
        folder (str): The folder name or ID to resolve. Can be either:
                   - A display name (e.g., "MyFolder")
                   - A UUID string (e.g., "12345678-1234-1234-1234-123456789abc")
        workspace (str | None): The workspace name or ID where the folder resides.
                               If None, uses the current workspace context.

    Returns:
        str: The resolved folder ID as a string.

    Raises:
        ValueError: If the folder cannot be resolved or an invalid ID is provided.
        Exception: If folder resolution fails due to permissions or other issues.

    Example:
        ```python
        from fabricflow.core.folders.utils import resolve_folder

        # Resolve by name
        folder_id = resolve_folder(
            "MyFolder",
            "MyWorkspace"
        )

        # Validate existing ID
        validated_id = resolve_folder(
            "12345678-1234-1234-1234-123456789abc",
            "MyWorkspace"
        )
        ```

    Note:
        This function uses Sempy's fabric module for folder resolution.
        Ensure you have appropriate permissions to access the folder and workspace.
    """

    try:
        folder_uuid: UUID = UUID(folder)
    except (ValueError, TypeError):
        return resolve_folder_id(folder, workspace)

    if is_valid_folder_id(folder_uuid, workspace):
        return str(folder_uuid)
    else:
        raise ValueError(f"Invalid folder ID: {folder_uuid} in workspace {workspace}")


def is_valid_folder_id(
    folder: str | UUID,
    workspace: str | None = None,
) -> bool:
    """
    Check if an folder ID or name is valid in the specified workspace.

    This function validates whether an folder exists and is accessible in the
    given workspace. It can be used to verify folder IDs before using them
    in operations or to check if an folder name exists.

    Args:
        folder (str | UUID): The folder name or ID to validate. Can be either:
                          - A display name (e.g., "MyFolder")
                          - A UUID string or UUID object
        workspace (str | None): The workspace name or ID to check within.
                               If None, uses the current workspace context.

    Returns:
        bool: True if the folder is valid and accessible, False otherwise.

    Example:
        ```python
        from fabricflow.core.folders.utils import is_valid_folder_id

        # Check if a Folder exists
        if is_valid_folder_id("MyFolder", "MyWorkspace"):
            print("Folder found")
        else:
            print("Folder not found or not accessible")

        # Validate an ID
        valid_id = is_valid_folder_id(
            "12345678-1234-1234-1234-123456789abc",
            "MyWorkspace"
        )
        ```

    Note:
        This function catches all exceptions and returns False for any errors,
        including permission issues, network problems, or folder not found.
    """
    try:
        resolved_name = resolve_folder_path(folder, workspace)
        return isinstance(resolved_name, str)
    except Exception:
        return False
