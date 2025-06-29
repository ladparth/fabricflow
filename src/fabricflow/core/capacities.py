from sempy.fabric import FabricRestClient
from typing import Dict, Any


def list_capacities(
    client: FabricRestClient, paged: bool = False
) -> list | Dict[str, Any]:
    """
    List all capacities in a Fabric workspace.

    Args:
        client (FabricRestClient): The Fabric client instance.
        paged (bool): If True, returns all pages as a flat list using get_paged().

    Returns:
        list or Dict[str, Any]: The list of capacities (paged or single response).
    """
    url: str = "/v1/capacities"
    if paged:
        return client.get_paged(url)
    response = client.get(url)
    response.raise_for_status()
    return response.json()


def resolve_capacity_id(client: FabricRestClient, capacity: str) -> str | None:
    """
    Resolve a capacity by its ID or name and return its ID.

    Args:
        client (FabricRestClient): The Fabric client instance.
        capacity (str): The ID or name of the capacity to resolve.

    Returns:
        str or None: The resolved capacity ID, or None if not found.
    """
    capacities = list_capacities(client, paged=True)

    if isinstance(capacities, dict) and "value" in capacities:
        capacities = capacities["value"]
    for cap in capacities:
        if cap.get("id") == capacity or cap.get("displayName") == capacity:
            return cap.get("id")
    return None
