from sempy.fabric import FabricRestClient
from typing import Optional, Dict, Any


def list_connections(
    client: FabricRestClient,
    params: Optional[Dict[str, Any]] = None,
    paged: bool = False,
) -> list | Dict[str, Any]:
    """
    List all connections the user has permission for.
    Args:
        params (Optional[Dict[str, Any]]): Query parameters for filtering the connections.
        paged (bool): If True, returns all pages as a flat list using get_paged().
    Returns:
        list or Dict[str, Any]: The list of connections (paged or single response).
    """
    url: str = "/v1/connections"
    if paged:
        return client.get_paged(url, params=params)
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.json()


def resolve_connection_id(client: FabricRestClient, connection: str) -> Optional[str]:
    """
    Resolve a connection by its ID or name and return its ID.

    Args:
        client (FabricRestClient): The Fabric client instance.
        connection (str): The ID or name of the connection to resolve.

    Returns:
        str or None: The resolved connection ID, or None if not found.
    """
    connections = list_connections(client, paged=True)
    if isinstance(connections, dict) and "value" in connections:
        connections = connections["value"]
    for conn in connections:
        if conn.get("id") == connection or conn.get("displayName") == connection:
            return conn.get("id")
    return None
