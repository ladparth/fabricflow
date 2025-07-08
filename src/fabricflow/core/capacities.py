"""
Microsoft Fabric capacities management utilities.

This module provides functions for working with capacities in Microsoft Fabric,
including listing available capacities and resolving capacity identifiers.

Functions:
    list_capacities: Retrieve a list of available capacities.
    resolve_capacity_id: Resolve a capacity name or ID to its actual ID.

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.core.capacities import resolve_capacity_id

    client = FabricRestClient()
    capacity_id = resolve_capacity_id(client, "MyCapacity")
    ```
"""

from sempy.fabric import FabricRestClient
from typing import Dict, Any


def list_capacities(
    client: FabricRestClient, paged: bool = False
) -> list | Dict[str, Any]:
    """
    List all capacities available in Microsoft Fabric Resource.

    Retrieves a list of capacities that the user has permission to view.
    Capacities represent compute resources that can be assigned to workspaces.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        paged (bool): If True, automatically fetches all pages and returns a flat list.
                     If False, returns the raw API response with pagination metadata.

    Returns:
        list | Dict[str, Any]: If paged=True, returns a list of capacity objects.
                              If paged=False, returns the raw API response dictionary
                              with pagination metadata.

    Raises:
        requests.HTTPError: If the API request fails.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.core.capacities import list_capacities

        client = FabricRestClient()

        # Get all capacities (automatically handle pagination)
        all_capacities = list_capacities(client, paged=True)

        # Get first page only
        first_page = list_capacities(client, paged=False)
        ```
    """
    url: str = "/v1/capacities"
    if paged:
        return client.get_paged(url)
    response = client.get(url)
    response.raise_for_status()
    return response.json()


def resolve_capacity_id(client: FabricRestClient, capacity: str) -> str | None:
    """
    Resolve a capacity identifier by name or ID and return the capacity ID.

    This function accepts either a capacity name or ID and returns the corresponding
    capacity ID. It's useful when you have a capacity name and need the ID for
    API operations, or when you want to validate that a capacity exists.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        capacity (str): The capacity name or ID to resolve.

    Returns:
        str | None: The resolved capacity ID if found, None if not found.
                   Returns the same value if the input was already an ID.

    Raises:
        requests.HTTPError: If the API request to list capacities fails.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.core.capacities import resolve_capacity_id

        client = FabricRestClient()

        # Resolve by name
        capacity_id = resolve_capacity_id(client, "My Premium Capacity")

        # Resolve by ID (returns the same ID)
        capacity_id = resolve_capacity_id(client, "abc123-def456-...")

        if capacity_id:
            print(f"Capacity ID: {capacity_id}")
        else:
            print("Capacity not found")
        ```

    Note:
        This function fetches all capacities and searches through them, which may
        be slow if you have many capacities. The search is case-sensitive for both
        names and IDs.
    """
    capacities = list_capacities(client, paged=True)

    if isinstance(capacities, dict) and "value" in capacities:
        capacities = capacities["value"]

    if isinstance(capacities, list):
        for cap in capacities:
            if isinstance(cap, dict):
                if cap.get("id") == capacity or cap.get("displayName") == capacity:
                    return cap.get("id")
    return None
