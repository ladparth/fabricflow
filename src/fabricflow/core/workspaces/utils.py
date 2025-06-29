from typing import Optional
import sempy.fabric as fabric


def get_workspace_id(workspace: Optional[str] = None) -> str:
    """
    Utility to resolve and return a workspace ID.
    If a workspace name is provided, resolve and return its ID.
    If an ID is provided, return it as is.
    If nothing is provided, return the default workspace ID.
    """

    if workspace is None:
        return fabric.get_workspace_id()

    return fabric.resolve_workspace_id(workspace)
