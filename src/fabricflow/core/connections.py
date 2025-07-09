"""
Microsoft Fabric connections management utilities.

This module provides functions for working with connections in Microsoft Fabric,
including listing available connections and resolving connection identifiers.

Connections in Fabric represent configured data sources and destinations that
can be used in data pipelines and other data operations.

Functions:
    list_connections: Retrieve a list of available connections.
    resolve_connection_id: Resolve a connection name or ID to its actual ID.

Example:
    ```python
    from sempy.fabric import FabricRestClient
    from fabricflow.core.connections import resolve_connection_id

    client = FabricRestClient()
    connection_id = resolve_connection_id(client, "MyConnection")
    ```
"""

from sempy.fabric import FabricRestClient
from typing import Optional, Dict, Any


def list_connections(
    client: FabricRestClient,
    params: Optional[Dict[str, Any]] = None,
    paged: bool = False,
) -> list | Dict[str, Any]:
    """
    List all connections the user has permission to access.

    Retrieves a list of connections available in the current Fabric Data Gateway.
    The user must have appropriate permissions to view the connections.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        params (Optional[Dict[str, Any]]): Optional query parameters for filtering
                                          the connections response.
        paged (bool): If True, automatically fetches all pages and returns a flat list.
                     If False, returns the raw API response.

    Returns:
        list | Dict[str, Any]: If paged=True, returns a list of connection objects.
                              If paged=False, returns the raw API response dictionary
                              with pagination metadata.

    Raises:
        requests.HTTPError: If the API request fails.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.core.connections import list_connections

        client = FabricRestClient()

        # Get all connections (automatically handle pagination)
        all_connections = list_connections(client, paged=True)

        # Get first page only
        first_page = list_connections(client, paged=False)
        ```
    """
    url: str = "/v1/connections"
    if paged:
        return client.get_paged(url, params=params)
    response = client.get(url, params=params)
    response.raise_for_status()
    return response.json()


def resolve_connection_id(client: FabricRestClient, connection: str) -> Optional[str]:
    """
    Resolve a connection identifier by name or ID and return the connection ID.

    This function accepts either a connection name or ID and returns the corresponding
    connection ID. It's useful when you have a connection name and need the ID for
    API operations, or when you want to validate that a connection exists.

    Args:
        client (FabricRestClient): Authenticated Fabric REST client instance.
        connection (str): The connection name or ID to resolve.

    Returns:
        Optional[str]: The resolved connection ID if found, None if not found.
                      Returns the same value if the input was already an ID.

    Raises:
        requests.HTTPError: If the API request to list connections fails.

    Example:
        ```python
        from sempy.fabric import FabricRestClient
        from fabricflow.core.connections import resolve_connection_id

        client = FabricRestClient()

        # Resolve by name
        connection_id = resolve_connection_id(client, "MySQL Connection")

        # Resolve by ID (returns the same ID)
        connection_id = resolve_connection_id(client, "abc123-def456-...")

        if connection_id:
            print(f"Connection ID: {connection_id}")
        else:
            print("Connection not found")
        ```

    Note:
        This function fetches all connections and searches through them, which may
        be slow if you have many connections. The search is case-sensitive for both
        names and IDs.
    """
    connections = list_connections(client, paged=True)
    if isinstance(connections, dict) and "value" in connections:
        connections = connections["value"]

    if isinstance(connections, list):
        for conn in connections:
            if isinstance(conn, dict):
                if (
                    conn.get("id") == connection
                    or conn.get("displayName") == connection
                ):
                    return conn.get("id")
    return None
