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
    Resolves an item name or ID to its corresponding UUID in the specified workspace.

    Args:
        item (str): The item name or ID to resolve.
        item_type (FabricItemType): The type of the item (e.g., LAKEHOUSE, DATASET).
        workspace (str): The workspace name or ID.

    Returns:
        str: The resolved item ID as a string.
    """

    try:
        _item_type: str | None = item_type.value if item_type else None

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
    Checks if the provided item is a valid item in the specified workspace.

    Args:
        item (str): The item name or ID to check.
        workspace (str): The workspace name or ID.
        item_type (FabricItemType): The type of the item (e.g., LAKEHOUSE, DATASET).

    Returns:
        bool: True if the item is valid, False otherwise.
    """
    try:
        _item_type: str | None = item_type.value if item_type else None
        resolved_name = resolve_item_name(item, _item_type, workspace)
        return isinstance(resolved_name, str)
    except Exception:
        return False
